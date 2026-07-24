#!/usr/bin/env bash
# 안양 검진센터 상위 블로그 화면 캡처 스크립트 (사용자 PC에서 실행)
#
# 이 원격 컨테이너는 네트워크 정책상 naver.com 접속이 막혀 있어 캡처가 불가능합니다.
# 아래 스크립트를 '사용자님 본인 PC'에서 실행하면 실제 네이버 화면을 캡처할 수 있습니다.
#
# 사전 준비(최초 1회):
#   npm i -g playwright && npx playwright install chromium
#
# 실행:
#   bash capture_naver.sh "안양 검진센터"
#
# 결과: ./shots/ 폴더에 검색결과(SERP) + 상위 블로그 캡처 저장

set -euo pipefail
KEYWORD="${1:-안양 검진센터}"
OUTDIR="./shots"
mkdir -p "$OUTDIR"

node - "$KEYWORD" "$OUTDIR" <<'JS'
const { chromium } = require('playwright');
const [ , , keyword, outdir ] = process.argv;

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 2000 },
    locale: 'ko-KR',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
             + '(KHTML, like Gecko) Chrome/125.0 Safari/537.36',
  });
  const page = await ctx.newPage();

  // 1) 통합검색 결과 캡처
  const serp = `https://search.naver.com/search.naver?query=${encodeURIComponent(keyword)}`;
  await page.goto(serp, { waitUntil: 'networkidle', timeout: 60000 });
  await page.screenshot({ path: `${outdir}/00_serp.png`, fullPage: true });
  console.log('saved SERP:', `${outdir}/00_serp.png`);

  // 2) 블로그 탭 상위 글 링크 수집(상위 3개)
  const blogTab = `https://search.naver.com/search.naver?ssc=tab.blog.all&query=${encodeURIComponent(keyword)}`;
  await page.goto(blogTab, { waitUntil: 'networkidle', timeout: 60000 });
  await page.screenshot({ path: `${outdir}/01_blogtab.png`, fullPage: true });

  const links = await page.$$eval('a', as => as
    .map(a => a.href)
    .filter(h => h.includes('blog.naver.com') || h.includes('blog.me'))
    .slice(0, 6));
  const top3 = [...new Set(links)].slice(0, 3);

  // 3) 상위 블로그 3개 본문 캡처
  let i = 1;
  for (const url of top3) {
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
      // 네이버 블로그는 iframe(mainFrame) 안에 본문이 있는 경우가 많음
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `${outdir}/blog_${i}.png`, fullPage: true });
      console.log('saved blog:', url);
    } catch (e) {
      console.log('skip:', url, e.message);
    }
    i++;
  }

  await browser.close();
  console.log('done →', outdir);
})();
JS
