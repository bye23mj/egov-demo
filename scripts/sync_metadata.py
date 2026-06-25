#!/usr/bin/env python3
"""기관메타데이터 TSV → xlsx 동기화기.

metadata-agent가 신규 표준(단어·용어·도메인·코드)을 기관 TSV에 등록(append)한 뒤,
TSV를 원본 기준으로 삼아 동일 이름의 xlsx를 갱신한다.

방향성(중요):
- 기관: tsv = 원본(source of truth), xlsx = 파생 → 이 스크립트(tsv → xlsx).
- 공공: xlsx = 원본, tsv = 파생 인덱스 → `scripts/build_metadata_index.py`(xlsx → tsv).
  공공은 READONLY이므로 여기서 절대 건드리지 않는다(기관 디렉토리만 대상).

규칙:
- 1행은 헤더로 그대로 보존한다.
- 기존 xlsx가 있으면 시트명을 보존한다.
- 순수 정수 문자열(예: '1', '13')만 숫자로 기록하고, 나머지(코드값 선행 0, '-', 텍스트)는
  데이터 유실 방지를 위해 문자열로 기록한다.

사용:
    python3 scripts/sync_metadata.py            # 기관 TSV 전체 동기화
    python3 scripts/sync_metadata.py "docs/03. metadata/기관/KOMSA표준용어.tsv"  # 특정 파일만
"""
import glob
import os
import re
import sys

ORG_DIR = "docs/03. metadata/기관"
INT_RE = re.compile(r"-?\d+$")


def _cell(value):
    # 선행 0이 있는 숫자(코드값 등)는 문자열로 유지하고, 순수 정수만 int로 변환한다.
    if INT_RE.match(value) and not (len(value) > 1 and value.lstrip("-").startswith("0")):
        try:
            return int(value)
        except ValueError:
            return value
    return value


def sync(tsv_path):
    import openpyxl

    xlsx_path = os.path.splitext(tsv_path)[0] + ".xlsx"

    sheet_name = "Sheet1"
    if os.path.exists(xlsx_path):
        old = openpyxl.load_workbook(xlsx_path, read_only=True)
        sheet_name = old.active.title
        old.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    rows = 0
    with open(tsv_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            ws.append([_cell(c) for c in line.split("\t")])
            rows += 1

    wb.save(xlsx_path)
    return xlsx_path, rows


def main():
    targets = sys.argv[1:] or sorted(glob.glob(os.path.join(ORG_DIR, "*.tsv")))
    if not targets:
        print(f"동기화 대상 TSV 없음: {ORG_DIR}")
        return
    for tsv in targets:
        # 안전장치: 공공 디렉토리는 동기화 대상에서 제외(READONLY).
        if os.sep + "공공" + os.sep in tsv:
            print(f"건너뜀(공공 READONLY): {tsv}")
            continue
        xlsx, n = sync(tsv)
        print(f"{os.path.relpath(xlsx)}: {n} rows (헤더 포함)")


if __name__ == "__main__":
    main()
