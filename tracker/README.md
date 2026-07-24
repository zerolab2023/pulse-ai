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

## 경쟁사 gap 분석 (누적) — "1위 대비 뭐가 부족한가"

순위만 보는 게 아니라 **1위 글과 비교해 우리가 뭘 놓쳤는지**를 계산하고 **매일 누적**한다.

```bash
python3 -m tracker.gap --config config/watchlist.example.json --mock --seed-days 8
```

출력 예:
```
🔎 [안양 검진센터]  우리: 4위   |   1위: 안양 검진센터 총정리 상세가이드
     • 현재 4위, 1위와 3칸 차이
     • 1위 제목엔 '검진센터'가 있는데 우리 제목엔 없음 → 제목에 '검진센터' 반영
     • 우리 글 74일 전 / 1위 18일 전 — 1위가 더 최신 → 본문 리프레시
     📈 누적 추세: ███▇▇▅▅▅  (5개→3개, 개선중 ↓)
     ℹ️  글자수·이미지수·목차 구조는 API로 측정 불가 → 본문 수집(옵션) 필요
```

**공식 API로 되는 안전한 비교**(제목 키워드 / 발행 최신성 / 순위 격차)만 한다.
글자수·이미지수·목차 구조 같은 **본문 신호는 API로 안 보이므로**, 필요 시 본문 수집(옵션)이나
네이버 애널리틱스 연동으로 확장한다(현재는 측정 불가임을 명시만 함).
**누적 추세**로 "부족한 점이 5개→3개로 줄고 있다"처럼 개선 여부를 추적한다.

## 모듈 구성

- `config.py` — 워치리스트 로딩
- `fetcher.py` — `NaverApiFetcher`(공식 API) / `MockFetcher`(검증용). `fetch_serp()`로 상위 목록 반환
- `storage.py` — SQLite 시계열 저장(무의존성)
- `analyzer.py` — 이동평균·추세·진입소요일·알림 규칙
- `competitor.py` — 1위 대비 gap 계산 + 누적 저장(`GapStore`)
- `run.py` — 일일 순위 실행 CLI
- `gap.py` — 경쟁사 gap 분석 실행 CLI

의존성: 파이썬 3.10+ 표준 라이브러리만. 별도 설치 불필요.
