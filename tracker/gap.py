"""경쟁사 gap 분석 실행기 (CLI).

키워드별로 "우리 순위 + 1위 대비 부족한 점"을 계산하고, 누적 추세를 보여준다.

사용:
  # API 키 없이 로직 검증 (가짜 SERP)
  python3 -m tracker.gap --config config/watchlist.example.json --mock --seed-days 8

  # 실제 (NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 필요)
  python3 -m tracker.gap --config config/watchlist.json
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta

from .competitor import GapStore, analyze_gap
from .config import Watchlist
from .fetcher import MockFetcher, NaverApiFetcher
from .storage import RankStore


def _spark(trend: list[tuple[str, int]]) -> str:
    """부족한 점 개수 추세를 간단한 막대로. 줄어들면 개선 중."""
    if not trend:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    mx = max(c for _, c in trend) or 1
    bars = "".join(blocks[min(len(blocks) - 1, round(c / mx * (len(blocks) - 1)))] for _, c in trend)
    first, last = trend[0][1], trend[-1][1]
    arrow = "개선중 ↓" if last < first else "악화 ↑" if last > first else "정체 →"
    return f"{bars}  ({first}개→{last}개, {arrow})"


def _measure(wl: Watchlist, gstore: GapStore, fetcher, day: str, on: date) -> None:
    for kt in wl.keywords:
        items = fetcher.fetch_serp(kt.keyword)
        rep = analyze_gap(kt.keyword, items, wl.blog_id, on=on)
        if rep:
            gstore.upsert(day, rep)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="네이버 블로그 경쟁사 gap 분석 + 누적")
    p.add_argument("--config", required=True)
    p.add_argument("--db", default="rank_history.db")
    p.add_argument("--date", default=date.today().isoformat())
    p.add_argument("--mock", action="store_true")
    p.add_argument("--seed-days", type=int, default=0, help="(mock) 과거 N일치 누적 시연")
    args = p.parse_args(argv)

    wl = Watchlist.load(args.config)
    store = RankStore(args.db)
    gstore = GapStore(store._conn)  # 같은 DB에 gap 테이블 추가
    today = date.fromisoformat(args.date)

    try:
        if args.mock and args.seed_days > 0:
            start = today - timedelta(days=args.seed_days)
            for i in range(args.seed_days):
                d = start + timedelta(days=i)
                _measure(wl, gstore, MockFetcher(day_index=i, our_blog_id=wl.blog_id),
                         d.isoformat(), d)

        fetcher = (MockFetcher(day_index=args.seed_days, our_blog_id=wl.blog_id)
                   if args.mock else NaverApiFetcher())
        _measure(wl, gstore, fetcher, args.date, today)

        print(f"=== {wl.display_name} · 경쟁사 gap 분석 ({args.date}) ===\n")
        for kt in wl.keywords:
            items = fetcher.fetch_serp(kt.keyword)
            rep = analyze_gap(kt.keyword, items, wl.blog_id, on=today)
            if not rep:
                continue
            rank_str = f"{rep.our_rank}위" if rep.our_rank else "미노출"
            print(f"🔎 [{kt.keyword}]  우리: {rank_str}   |   1위: {rep.top1_title[:30]}")
            if not rep.gaps:
                print("     ✅ 1위 대비 관찰되는 부족한 점 없음(제목·최신성 기준)")
            for g in rep.gaps:
                print(f"     • {g.detail}")
                print(f"         → {g.action}")
            trend = gstore.gap_count_trend(kt.keyword)
            if len(trend) > 1:
                print(f"     📈 누적 추세: {_spark(trend)}")
            print(f"     ℹ️  {rep.deep_signal_note}")
            print()
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
