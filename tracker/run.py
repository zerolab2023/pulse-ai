"""일일 순위 트래커 실행기 (CLI).

하루 1회 실행:
  1) 워치리스트의 각 키워드로 순위 측정 (API 또는 mock)
  2) SQLite 시계열에 적재
  3) 파생지표 계산 + 알림 출력

사용:
  # API 키 없이 로직 검증 (가짜 데이터)
  python -m tracker.run --config config/watchlist.example.json --mock --seed-days 10

  # 실제 측정 (환경변수 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 필요)
  python -m tracker.run --config config/watchlist.json --date 2026-07-23
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta

from .analyzer import analyze
from .config import Watchlist
from .fetcher import MockFetcher, NaverApiFetcher, find_rank
from .storage import RankRow, RankStore


def _measure_and_store(wl: Watchlist, store: RankStore, fetcher, day: str) -> None:
    for kt in wl.keywords:
        items = fetcher.fetch_serp(kt.keyword)
        res = find_rank(items, wl.blog_id, kt.post_id, kt.keyword)
        store.upsert(RankRow(day, kt.keyword, res.rank, res.found_url, res.note))


def _report(wl: Watchlist, store: RankStore) -> list[str]:
    lines: list[str] = []
    first_page_hits = 0
    for kt in wl.keywords:
        hist = store.history(kt.keyword, limit=wl.moving_avg_days * 3)
        ins = analyze(
            kt.keyword,
            hist,
            first_page_size=wl.first_page_size,
            moving_avg_days=wl.moving_avg_days,
            drop_alert_days=wl.drop_alert_days,
            published_at=kt.published_at,
        )
        first_page_hits += int(ins.on_first_page)
        rank_str = f"{ins.today_rank}위" if ins.today_rank else "미노출"
        avg_str = f"{ins.moving_avg}" if ins.moving_avg is not None else "-"
        d2f = f", 진입 {ins.days_to_first_page}일" if ins.days_to_first_page is not None else ""
        flag = "🟢" if ins.on_first_page else "⚪"
        lines.append(
            f"{flag} [{ins.trend:>4}] {kt.keyword}: {rank_str} "
            f"(7일평균 {avg_str}{d2f})"
        )
        for a in ins.alerts:
            lines.append(f"       └ {a}")
    lines.append("")
    lines.append(f"📊 채널 요약: 1페이지 노출 {first_page_hits}/{len(wl.keywords)}개")
    return lines


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="네이버 블로그 일일 키워드 순위 트래커")
    p.add_argument("--config", required=True, help="워치리스트 JSON 경로")
    p.add_argument("--db", default="rank_history.db", help="SQLite 파일 경로")
    p.add_argument("--date", default=date.today().isoformat(), help="측정일 YYYY-MM-DD")
    p.add_argument("--mock", action="store_true", help="API 없이 가짜 데이터로 실행")
    p.add_argument("--seed-days", type=int, default=0,
                   help="(mock 전용) 과거 N일치 시계열을 미리 채워 추세/알림을 시연")
    args = p.parse_args(argv)

    wl = Watchlist.load(args.config)
    store = RankStore(args.db)

    try:
        if args.mock and args.seed_days > 0:
            # 과거 N일치를 날짜별로 다른 순위(day_index)로 채워 넣는다.
            start = date.fromisoformat(args.date) - timedelta(days=args.seed_days)
            for i in range(args.seed_days):
                day = (start + timedelta(days=i)).isoformat()
                _measure_and_store(wl, store, MockFetcher(day_index=i, our_blog_id=wl.blog_id), day)

        fetcher = (MockFetcher(day_index=args.seed_days, our_blog_id=wl.blog_id)
                   if args.mock else NaverApiFetcher())
        _measure_and_store(wl, store, fetcher, args.date)

        print(f"=== {wl.display_name} · 일일 순위 리포트 ({args.date}) ===")
        print("\n".join(_report(wl, store)))
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
