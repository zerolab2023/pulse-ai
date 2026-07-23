"""파생지표 계산 + 알림 규칙 (설계서 5.3 / 6장과 일치).

매일 측정하되(트래커), 판정은 노이즈를 줄인 이동평균 추세로 내린다.
'매일 측정, 주기적으로 판단' 원칙을 여기서 코드로 구현한다.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import date

from .storage import RankRow


@dataclass
class KeywordInsight:
    keyword: str
    today_rank: int | None
    on_first_page: bool               # 오늘 1페이지(<=N위) 노출 여부
    moving_avg: float | None          # 최근 창의 평균 순위(미노출 제외)
    days_to_first_page: int | None    # 발행 → 최초 1페이지 진입까지 일수
    trend: str                        # "up" | "down" | "flat" | "n/a"
    alerts: list[str] = field(default_factory=list)


def _rank_value(r: RankRow, miss_penalty: int) -> int:
    """미노출은 큰 순위값(패널티)으로 환산해 이동평균·추세에 반영."""
    return r.rank if r.rank is not None else miss_penalty


def analyze(
    keyword: str,
    history: list[RankRow],
    *,
    first_page_size: int = 10,
    moving_avg_days: int = 7,
    drop_alert_days: int = 3,
    published_at: str | None = None,
    miss_penalty: int = 100,
) -> KeywordInsight:
    if not history:
        return KeywordInsight(keyword, None, False, None, None, "n/a", ["no data"])

    today = history[-1]
    today_rank = today.rank
    on_first_page = today_rank is not None and today_rank <= first_page_size

    window = history[-moving_avg_days:]
    ranked = [r.rank for r in window if r.rank is not None]
    moving_avg = round(statistics.mean(ranked), 1) if ranked else None

    # 진입 소요일: 발행일 이후 최초로 1페이지에 든 날짜와의 간격
    days_to_first_page = None
    if published_at:
        pub = date.fromisoformat(published_at)
        for r in history:
            r_date = date.fromisoformat(r.date)
            if r_date < pub:
                continue  # 발행 이전 측정치는 진입 계산에서 제외(오염 방지)
            if r.rank is not None and r.rank <= first_page_size:
                days_to_first_page = (r_date - pub).days
                break

    # 추세: 최근 절반 vs 이전 절반의 평균 순위 비교(순위는 작을수록 좋음)
    trend = "n/a"
    if len(window) >= 4:
        half = len(window) // 2
        older = [_rank_value(r, miss_penalty) for r in window[:half]]
        newer = [_rank_value(r, miss_penalty) for r in window[half:]]
        diff = statistics.mean(newer) - statistics.mean(older)
        trend = "up" if diff <= -1 else "down" if diff >= 1 else "flat"

    alerts: list[str] = []

    # 신규 1페이지 진입 (어제까지 미진입 → 오늘 진입)
    prev = history[-2] if len(history) >= 2 else None
    prev_first = prev is not None and prev.rank is not None and prev.rank <= first_page_size
    if on_first_page and not prev_first:
        alerts.append(f"🎉 신규 1페이지 진입 (현재 {today_rank}위) → 성공 템플릿 후보로 승격")

    # N일 연속 하락 → 이탈 경보 (L1 리라이트 큐)
    if len(history) > drop_alert_days:
        recent = history[-(drop_alert_days + 1):]
        vals = [_rank_value(r, miss_penalty) for r in recent]
        if all(b > a for a, b in zip(vals, vals[1:])):  # 순위 숫자가 계속 커짐 = 하락
            alerts.append(f"⚠️ {drop_alert_days}일 연속 하락 → L1 리라이트 큐 등록 + 담당자 알림")

    # 1페이지 → 이탈
    if prev_first and not on_first_page:
        alerts.append("⚠️ 1페이지에서 이탈 → 원인 점검(경쟁글 진입 여부 확인)")

    return KeywordInsight(
        keyword, today_rank, on_first_page, moving_avg, days_to_first_page, trend, alerts
    )
