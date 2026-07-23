# 일일 키워드 순위 트래커 (Daily Rank Tracker)

클로즈드 루프의 **"눈(센서)"**. 매일 네이버 검색에서 우리 병원 블로그 글의 키워드 순위를
측정해 시계열로 쌓고, 파생지표와 알림을 만들어 L1(콘텐츠 루프)에 신호를 넘긴다.

> 설계 배경·전체 그림은 [`docs/marketing-agent-design.md`](../docs/marketing-agent-design.md) 5.3 / 6장 참고.

## 크롤링이 아니라 "공식 API"

이 트래커는 검색결과 HTML을 긁는 **크롤링이 아니다.** 네이버가 허가한
**공식 검색 API**(`openapi.naver.com/v1/search/blog.json`)를 키로 정식 호출한다 → 차단·정책위반 없음.
대신 API 정렬은 실제 통합검색(SERP) 순위와 완전히 같지는 않다. 우리는 절대순위가 아니라
**7일 이동평균 추세**로 판단하므로 이 근사로 충분하다. 정확도가 더 필요하면 `Fetcher`만
상용 순위추적 API 구현으로 교체하면 된다(인터페이스로 분리해 둠).

## 빠른 시작 (API 키 없이 mock으로 로직 검증)

```bash
# 과거 10일치 가짜 시계열을 채우고 오늘자 리포트 출력
python3 -m tracker.run --config config/watchlist.example.json --mock --seed-days 10
```

- `--mock` : 네이버 대신 가짜 순위 생성(파이프라인 검증용). 코드 변경 없이 플래그만 뗀다.
- `--seed-days N` : 추세/알림을 시연하기 위해 과거 N일치를 미리 채움.

## 실제 측정 (운영)

```bash
export NAVER_CLIENT_ID=...        # 네이버 개발자센터 애플리케이션(검색) 키
export NAVER_CLIENT_SECRET=...
python3 -m tracker.run --config config/watchlist.json --date 2026-07-23
```

매일 새벽 1회 실행되도록 스케줄러(cron 등)에 건다. 예: `0 6 * * *`.

## 워치리스트 (`config/watchlist.json`)

`config/watchlist.example.json`을 복사해 작성한다.

| 필드 | 의미 |
|---|---|
| `blog_id` | 우리 블로그 식별자 (`blog.naver.com/{blog_id}`) |
| `keywords[].keyword` | 매일 순위를 확인할 키워드 |
| `keywords[].post_url` | 그 키워드로 미는 우리 글(없으면 채널 단위 매칭) |
| `keywords[].published_at` | 발행일 — '진입 소요일' 계산에 사용 |
| `first_page_size` | 1페이지 기준(기본 10위) |
| `moving_avg_days` | 이동평균 창(기본 7일) |
| `drop_alert_days` | N일 연속 하락 시 경보(기본 3일) |

## 산출 지표 → 루프 연결

| 지표/알림 | 다음 행동 (루프) |
|---|---|
| 🎉 신규 1페이지 진입 | 성공 템플릿 후보로 승격(few-shot 예시화) |
| ⚠️ N일 연속 하락 | L1 리라이트 큐 등록 + 담당자 알림 |
| ⚠️ 1페이지 이탈 | 경쟁글 진입 여부 점검 |
| 진입 소요일 / 7일 이동평균 | 채널 성장 추세(L2) 판단 근거 |

## 모듈 구성

- `config.py` — 워치리스트 로딩
- `fetcher.py` — `NaverApiFetcher`(공식 API) / `MockFetcher`(검증용), 교체 가능한 인터페이스
- `storage.py` — SQLite 시계열 저장(무의존성)
- `analyzer.py` — 이동평균·추세·진입소요일·알림 규칙
- `run.py` — 일일 실행 CLI

의존성: 파이썬 3.10+ 표준 라이브러리만. 별도 설치 불필요.
