"""컴플라이언스 게이트 실행기 (CLI).

글 초안(txt/md 파일 또는 표준입력)을 검사해 발행 가부를 판정한다.
콘텐츠 생성기 → 이 게이트 → 발행 순서로 파이프라인에 끼운다(fail-closed).

사용:
  python3 -m compliance.run --file draft.md
  echo "완치 후기 이벤트 최고의 병원" | python3 -m compliance.run
  python3 -m compliance.run --file draft.md --json      # 기계 판독용 JSON

종료 코드: PASS/REVIEW=0, BLOCK=2 (CI/자동화에서 발행 차단에 활용)
"""
from __future__ import annotations

import argparse
import json
import sys

from .checker import check

_ICON = {"BLOCK": "🛑", "REVIEW": "🟡", "PASS": "🟢"}


def _render(report) -> str:
    lines = [f"{_ICON[report.decision]} 판정: {report.decision} "
             f"(차단 {report.block_count}건 / 검토 {report.warn_count}건)"]
    if not report.violations:
        lines.append("   위험 표현이 발견되지 않았습니다. (단, 최종 감수는 필요)")
    for i, v in enumerate(report.violations, 1):
        tag = "🛑 차단" if v.severity == "block" else "🟡 검토"
        lines.append("")
        lines.append(f"{i}. [{tag}] {v.category} — '{v.matched}'")
        lines.append(f"   위치: {v.context}")
        lines.append(f"   근거: {v.reason}")
        lines.append(f"   대안: {v.suggestion}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="의료광고법 컴플라이언스 게이트 v1")
    p.add_argument("--file", help="검사할 글 파일(txt/md). 없으면 표준입력에서 읽음")
    p.add_argument("--json", action="store_true", help="JSON으로 출력(기계 판독용)")
    args = p.parse_args(argv)

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    report = check(text)

    if args.json:
        print(json.dumps({
            "decision": report.decision,
            "block_count": report.block_count,
            "warn_count": report.warn_count,
            "violations": [v.__dict__ for v in report.violations],
        }, ensure_ascii=False, indent=2))
    else:
        print(_render(report))

    return 2 if report.decision == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
