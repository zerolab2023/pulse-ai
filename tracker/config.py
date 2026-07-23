"""워치리스트 설정 로딩.

한 블로그(우리 병원)와, 매일 순위를 확인할 키워드 목록을 정의한다.
JSON 파일에서 읽어오며, 스키마는 config/watchlist.example.json 참고.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class KeywordTarget:
    """추적할 키워드 하나. 발행한 글 URL을 연결해 '진입 소요일'을 계산한다."""

    keyword: str
    post_url: str | None = None          # 이 키워드로 밀고 있는 우리 글(없으면 채널 전체로 매칭)
    published_at: str | None = None      # YYYY-MM-DD, 진입 소요일 계산용
    tab: str = "blog"                    # blog | view (검색 탭)

    @property
    def post_id(self) -> str | None:
        """blog.naver.com/{blogId}/{logNo} 형태에서 logNo(글 고유번호) 추출."""
        if not self.post_url:
            return None
        return self.post_url.rstrip("/").split("/")[-1] or None


@dataclass
class Watchlist:
    """우리 블로그 식별자 + 추적 키워드 목록."""

    blog_id: str                         # 예: "anyang-checkup" (blog.naver.com/anyang-checkup)
    display_name: str
    keywords: list[KeywordTarget] = field(default_factory=list)
    # 판정 파라미터 (설계서 6장과 일치)
    first_page_size: int = 10            # 1페이지 = 상위 N위
    moving_avg_days: int = 7             # 이동평균 창(노이즈 제거)
    drop_alert_days: int = 3             # N일 연속 하락 시 이탈 경보

    @classmethod
    def load(cls, path: str | Path) -> "Watchlist":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        keywords = [KeywordTarget(**k) for k in data.pop("keywords", [])]
        return cls(keywords=keywords, **data)
