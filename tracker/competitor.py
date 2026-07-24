"""경쟁사 gap 분석 — "1위는 갖췄는데 우리는 뭐가 부족한가"를 계산하고 누적한다.

공식 API로 관찰 가능한 신호만으로 비교한다(안전):
  - 순위 격차       : 우리 순위 vs 1위
  - 제목 키워드     : 1위 제목엔 있는데 우리 제목엔 빠진 검색어 토큰
  - 발행 최신성     : 1위 글이 더 최신인지(네이버는 신선도를 반영)

본문 신호(글자수·이미지수·목차 구조·체류시간)는 API로 안 보인다.
→ deep_signal_note로 "본문 수집(옵션) 또는 애널리틱스 연동 필요"임을 명시만 한다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date

from .fetcher import SerpItem


@dataclass
class Gap:
    kind: str          # rank | title_keyword | freshness | not_ranked
    detail: str        # 사람이 읽는 설명
    action: str        # 무엇을 하면 되는지


@dataclass
class GapReport:
    keyword: str
    our_rank: int | None
    top1_title: str
    top1_url: str
    gaps: list[Gap] = field(default_factory=list)
    deep_signal_note: str = "글자수·이미지수·목차 구조는 API로 측정 불가 → 본문 수집(옵션) 필요"

    @property
    def gap_count(self) -> int:
        return len(self.gaps)


def _post_age_days(postdate: str, on: date) -> int | None:
    """YYYYMMDD → 측정일 기준 경과일. 파싱 실패 시 None."""
    if not postdate or len(postdate) != 8 or not postdate.isdigit():
        return None
    try:
        d = date(int(postdate[:4]), int(postdate[4:6]), int(postdate[6:8]))
    except ValueError:
        return None
    return (on - d).days


def analyze_gap(
    keyword: str,
    items: list[SerpItem],
    blog_id: str,
    *,
    on: date,
    freshness_gap_days: int = 21,
) -> GapReport | None:
    """SERP에서 1위와 우리 글을 비교해 부족한 점 목록을 만든다."""
    if not items:
        return None

    top1 = items[0]
    tokens = [t for t in keyword.split() if t]

    # 우리 글 찾기 — gap 분석은 '이 키워드로 우리 블로그(채널)가 몇 위냐'가 핵심이므로
    # 글 단위(post_id)가 아니라 채널(blog_id) 단위로, 가장 높이 노출된 글을 잡는다.
    ours = next(
        (it for it in items if blog_id.lower() in f"{it.link} {it.bloggerlink}".lower()),
        None,
    )

    report = GapReport(keyword, ours.rank if ours else None, top1.title, top1.link)

    # 1) 순위 격차 / 미노출
    if ours is None:
        report.gaps.append(Gap(
            "not_ranked",
            f"미노출 — 1위는 '{top1.title}'",
            "이 키워드로 글을 발행하거나 기존 글을 최적화해 진입시켜야 함",
        ))
    elif ours.rank > 1:
        report.gaps.append(Gap(
            "rank",
            f"현재 {ours.rank}위, 1위와 {ours.rank - 1}칸 차이",
            "아래 부족한 점들을 메우면 순위 상승 여지",
        ))

    # 2) 제목 키워드: 1위 제목엔 있는데 우리 제목엔 없는 토큰
    if ours is not None:
        for t in tokens:
            in_top1 = t in top1.title
            in_ours = t in ours.title
            if in_top1 and not in_ours:
                report.gaps.append(Gap(
                    "title_keyword",
                    f"1위 제목엔 '{t}'가 있는데 우리 제목엔 없음",
                    f"제목에 '{t}' 키워드 반영",
                ))

    # 3) 발행 최신성: 1위가 우리보다 충분히 더 최신이면
    if ours is not None:
        top1_age = _post_age_days(top1.postdate, on)
        ours_age = _post_age_days(ours.postdate, on)
        if top1_age is not None and ours_age is not None and (ours_age - top1_age) >= freshness_gap_days:
            report.gaps.append(Gap(
                "freshness",
                f"우리 글 {ours_age}일 전 / 1위 {top1_age}일 전 — 1위가 더 최신",
                "본문을 최신 정보로 리프레시(재발행)해 신선도 신호 확보",
            ))

    return report


# ---- 누적 저장 (SQLite) ----

class GapStore:
    """gap 스냅샷을 매 측정마다 누적. 부족한 점 개수의 추세를 볼 수 있다."""

    def __init__(self, conn):
        self._conn = conn
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS competitor_gap (
                date       TEXT NOT NULL,
                keyword    TEXT NOT NULL,
                our_rank   INTEGER,
                top1_url   TEXT,
                top1_title TEXT,
                gap_count  INTEGER,
                gaps_json  TEXT,
                PRIMARY KEY (date, keyword)
            )
            """
        )
        self._conn.commit()

    def upsert(self, day: str, r: GapReport) -> None:
        self._conn.execute(
            """
            INSERT INTO competitor_gap
                (date, keyword, our_rank, top1_url, top1_title, gap_count, gaps_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date, keyword) DO UPDATE SET
                our_rank=excluded.our_rank, top1_url=excluded.top1_url,
                top1_title=excluded.top1_title, gap_count=excluded.gap_count,
                gaps_json=excluded.gaps_json
            """,
            (day, r.keyword, r.our_rank, r.top1_url, r.top1_title, r.gap_count,
             json.dumps([g.__dict__ for g in r.gaps], ensure_ascii=False)),
        )
        self._conn.commit()

    def gap_count_trend(self, keyword: str, limit: int = 14) -> list[tuple[str, int]]:
        """(날짜, 부족한 점 개수)를 오래된 순으로. 개수가 줄면 개선 중."""
        cur = self._conn.execute(
            "SELECT date, gap_count FROM competitor_gap WHERE keyword=? ORDER BY date DESC LIMIT ?",
            (keyword, limit),
        )
        return list(reversed([(r[0], r[1]) for r in cur.fetchall()]))
