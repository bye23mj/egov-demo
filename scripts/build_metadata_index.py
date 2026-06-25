#!/usr/bin/env python3
"""공공메타데이터 xlsx → TSV 인덱스 변환기.

docs/03. metadata/공공 하위의 .xlsx(공공메타데이터)를 같은 위치에 동일 이름의 .tsv로
변환한다. metadata-agent가 xlsx를 통째로 로드하지 않고 Grep으로 빠르게 조회할 수 있게
하는 경량 인덱스를 만든다.

방향성(중요):
- 공공: xlsx = 원본, tsv = 파생 인덱스 → 이 스크립트(xlsx → tsv).
- 기관: tsv = 원본, xlsx = 파생 → `scripts/sync_metadata.py`(tsv → xlsx).
  기관은 여기서 변환하지 않는다. 기관 xlsx로 tsv를 덮어써 신규 등록분이 사라지는 것을 막기 위함.

- 셀 내 탭/개행은 공백으로 치환하여 TSV 정합성을 보장한다.
- 완전 빈 행은 건너뛴다.
- 공공 xlsx 원본은 읽기만 한다(.tsv는 파생물).

사용:
    python3 scripts/build_metadata_index.py
"""
import csv
import glob
import os

META_DIR = "docs/03. metadata/공공"


def clean(value):
    if value is None:
        return ""
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()


def convert(xlsx_path):
    import openpyxl

    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb.active
    tsv_path = os.path.splitext(xlsx_path)[0] + ".tsv"
    rows_written = 0
    with open(tsv_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n",
                            quoting=csv.QUOTE_NONE, escapechar="\\")
        for row in ws.iter_rows(values_only=True):
            cells = [clean(c) for c in row]
            if not any(cells):
                continue
            writer.writerow(cells)
            rows_written += 1
    wb.close()
    return tsv_path, rows_written


def main():
    files = sorted(glob.glob(os.path.join(META_DIR, "**", "*.xlsx"), recursive=True))
    if not files:
        print(f"변환 대상 xlsx 없음: {META_DIR}")
        return
    for xlsx in files:
        tsv, n = convert(xlsx)
        print(f"{os.path.relpath(tsv)}: {n} rows")


if __name__ == "__main__":
    main()
