"""검색 결과(SERP)를 가져오는 Fetcher.

두 가지 구현:
- NaverApiFetcher : 네이버 공식 검색 API(정책 준수) 사용. 환경변수로 키 주입.
- MockFetcher     : API 키 없이 로컬에서 파이프라인 전체를 돌려보기 위한 가짜 구현.

핵심: fetch_serp()가 상위 결과 목록 전체를 돌려준다. 여기서
- 우리 글의 순위(fetch)  와
- 1위 경쟁글과의 비교(gap 분석)  가 모두 파생된다.

주의(설계서 5.3의 '리스크·주의'와 일치):
- 공식 검색 API의 정렬은 실제 통합검색(SERP) 순위와 '완전히' 같지는 않다.
  하지만 정책을 지키며 매일 안정적으로 시계열을 쌓는 데는 가장 합리적인 출발점이다.
- API로는 제목·발행일까지만 보인다. 글자수·이미지수 등 본문 신호는 별도 수집(옵션)이 필요하다.
- 순위는 지역/로그인/시점에 따라 달라지므로, 측정 조건(비로그인·display 개수)을 고정한다.
"""
from __future__ import annotations

import html
import json
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass
class SerpItem:
    """검색 결과 한 건. (공식 API가 주는 범위)"""

    rank: int                   # 1-based 순위
    title: str                  # 제목(태그 제거)
    link: str
    bloggerlink: str = ""
    postdate: str = ""          # YYYYMMDD (없을 수 있음)
    description: str = ""


@dataclass
class RankResult:
    """한 키워드에 대한 우리 글의 순위."""

    keyword: str
    rank: int | None            # 1-based 순위. 결과에서 못 찾으면 None(미노출)
    found_url: str | None       # 매칭된 우리 글 URL
    total_scanned: int          # 훑어본 결과 개수(순위 판정 신뢰도 참고용)
    note: str = ""


class Fetcher(Protocol):
    def fetch_serp(self, keyword: str) -> list[SerpItem]: ...


def _clean(text: str) -> str:
    """네이버 API 제목/본문의 <b> 태그와 HTML 엔티티 제거."""
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def _match(item_link: str, item_bloggerlink: str, blog_id: str, post_id: str | None) -> bool:
    """검색 결과 항목이 '우리 글'인지 판정."""
    haystack = f"{item_link} {item_bloggerlink}".lower()
    if blog_id.lower() not in haystack:
        return False
    if post_id:
        return post_id.lower() in item_link.lower()
    return True


def find_rank(items: list[SerpItem], blog_id: str, post_id: str | None,
              keyword: str) -> RankResult:
    """SERP 목록에서 우리 글의 순위를 찾는다. (fetcher 공통 로직)"""
    for it in items:
        if _match(it.link, it.bloggerlink, blog_id, post_id):
            return RankResult(keyword, it.rank, it.link, len(items))
    return RankResult(keyword, None, None, len(items),
                      note=f"not found in top {len(items)}")


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

    def fetch_serp(self, keyword: str) -> list[SerpItem]:
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
        items = []
        for idx, it in enumerate(data.get("items", []), start=1):
            items.append(SerpItem(
                rank=idx,
                title=_clean(it.get("title", "")),
                link=it.get("link", ""),
                bloggerlink=it.get("bloggerlink", ""),
                postdate=it.get("postdate", ""),
                description=_clean(it.get("description", "")),
            ))
        return items


class MockFetcher:
    """API 없이 파이프라인을 검증하기 위한 결정론적 가짜 Fetcher.

    키워드+날짜 해시로 상위 목록을 만들어, '진입/유지/급락'과 경쟁 구도를 재현한다.
    실제 순위와 무관하며 오직 로직 검증용이다.
    """

    def __init__(self, day_index: int = 0, our_blog_id: str = "anyang-checkup"):
        self.day_index = day_index
        self.our_blog_id = our_blog_id

    def fetch_serp(self, keyword: str, top_n: int = 10) -> list[SerpItem]:
        seed = sum(ord(c) for c in keyword)
        tokens = keyword.split()
        # 우리 글: 대체로 상위권에 존재(2~8위), 일부 키워드는 미노출.
        our_rank = None if seed % 11 == 0 else 2 + (seed % 7)
        # 제목 키워드 커버리지: day_index가 커질수록(운영이 최적화할수록) 넓어진다 → 부족한 점 감소.
        cover_n = min(len(tokens), 1 + self.day_index // 3)
        our_title = " ".join(tokens[:cover_n]) + " 안내 - 우리병원블로그"

        items: list[SerpItem] = []
        for i in range(1, top_n + 1):
            if our_rank == i:
                # 우리 글: 제목 커버리지 부분적 + 오래된 발행일(부족한 점을 만들기 위함)
                items.append(SerpItem(i, our_title,
                                      f"https://blog.naver.com/{self.our_blog_id}/2230000{i:03d}",
                                      f"blog.naver.com/{self.our_blog_id}", "20260510"))
            else:
                # 경쟁글: 상위일수록 제목에 키워드를 잘 담고 더 최신
                cover = " ".join(tokens if i <= 3 else tokens[:1])
                pdate = "20260705" if i <= 3 else "20260601"
                items.append(SerpItem(i, f"{cover} 총정리 상세가이드",
                                      f"https://blog.naver.com/rival{i}/12345{i:02d}",
                                      f"blog.naver.com/rival{i}", pdate))
        return items
