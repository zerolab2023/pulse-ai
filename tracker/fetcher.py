"""검색 결과에서 우리 블로그의 순위를 찾아오는 Fetcher.

두 가지 구현:
- NaverApiFetcher : 네이버 공식 검색 API(정책 준수) 사용. 환경변수로 키 주입.
- MockFetcher     : API 키 없이 로컬에서 파이프라인 전체를 돌려보기 위한 가짜 구현.

주의(설계서 5.3의 '리스크·주의'와 일치):
- 공식 검색 API의 정렬은 실제 통합검색(SERP) 순위와 '완전히' 같지는 않다.
  하지만 정책을 지키며 매일 안정적으로 시계열을 쌓는 데는 가장 합리적인 출발점이다.
- 순위는 지역/로그인/시점에 따라 달라지므로, 측정 조건(비로그인·display 개수)을 고정한다.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass
class RankResult:
    """한 키워드에 대한 측정 결과."""

    keyword: str
    rank: int | None            # 1-based 순위. 결과에서 못 찾으면 None(미노출)
    found_url: str | None       # 매칭된 우리 글 URL
    total_scanned: int          # 훑어본 결과 개수(순위 판정 신뢰도 참고용)
    note: str = ""


class Fetcher(Protocol):
    def fetch(self, keyword: str, blog_id: str, post_id: str | None) -> RankResult: ...


def _match(item_link: str, item_bloggerlink: str, blog_id: str, post_id: str | None) -> bool:
    """검색 결과 항목이 '우리 글'인지 판정.

    post_id가 있으면 글 단위 정확 매칭, 없으면 블로그(채널) 단위 매칭.
    """
    haystack = f"{item_link} {item_bloggerlink}".lower()
    if blog_id.lower() not in haystack:
        return False
    if post_id:
        return post_id.lower() in item_link.lower()
    return True


class NaverApiFetcher:
    """네이버 검색 API(blog) 기반. NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 필요."""

    ENDPOINT = "https://openapi.naver.com/v1/search/blog.json"

    def __init__(self, client_id: str | None = None, client_secret: str | None = None,
                 display: int = 100, timeout: int = 10):
        self.client_id = client_id or os.environ.get("NAVER_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("NAVER_CLIENT_SECRET", "")
        self.display = display        # 최대 100. 100위 밖은 '미노출'로 간주.
        self.timeout = timeout
        if not (self.client_id and self.client_secret):
            raise RuntimeError(
                "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 미설정 — mock 모드(--mock)로 먼저 검증하세요."
            )

    def fetch(self, keyword: str, blog_id: str, post_id: str | None) -> RankResult:
        qs = urllib.parse.urlencode({"query": keyword, "display": self.display, "sort": "sim"})
        req = urllib.request.Request(
            f"{self.ENDPOINT}?{qs}",
            headers={
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret,
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("items", [])
        for idx, item in enumerate(items, start=1):
            if _match(item.get("link", ""), item.get("bloggerlink", ""), blog_id, post_id):
                return RankResult(keyword, idx, item.get("link"), len(items))
        return RankResult(keyword, None, None, len(items), note="not found in top %d" % len(items))


class MockFetcher:
    """API 없이 파이프라인을 검증하기 위한 결정론적 가짜 Fetcher.

    키워드+날짜 해시로 순위를 만들어, '진입/유지/급락' 같은 패턴을 재현한다.
    실제 순위와 무관하며 오직 로직 검증용이다.
    """

    def __init__(self, day_index: int = 0):
        # day_index를 넣으면 날짜별로 순위가 변하는 시계열을 흉내낼 수 있다.
        self.day_index = day_index

    def fetch(self, keyword: str, blog_id: str, post_id: str | None) -> RankResult:
        seed = sum(ord(c) for c in keyword) + self.day_index
        # 대략 3~40위 사이를 오가되, 일부 키워드는 미노출이 되도록.
        base = (seed * 7) % 45
        if base > 40:
            return RankResult(keyword, None, None, 100, note="mock: not ranked")
        rank = 1 + base % 40
        url = f"https://blog.naver.com/{blog_id}/{post_id or '000000'}"
        return RankResult(keyword, rank, url, 100, note="mock")
