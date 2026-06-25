#!/usr/bin/env python3
# 선박기본정보.csv → 정제 데이터 + SQL*Loader 컨트롤 파일 생성
import csv, os

SRC = "/Users/ai/vscode/egov-demo/work/선박기본정보.csv"
OUT = "/Users/ai/vscode/egov-demo/docs/05. db-build/선박기본정보/sql"
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(OUT, "vsl_bsc.dat")
CTL  = os.path.join(OUT, "vsl_bsc.ctl")

# CSV 순서대로 (영문컬럼, 종류). 종류: num/date/char
COLS = [
 ("DIV_NM","char"),("VSL_NO","char"),("VSL_NM","char"),("CMPTNC_BROF_NM","char"),
 ("VSL_SE_NM","char"),("VSL_MTPRPT_NM","char"),("SHPM_PRT_NM","char"),
 ("LEN","num"),("BRTH","num"),("DPTH","num"),("TOT_TON","num"),
 ("MENG_KND1_NM","char"),("MENG1_HP","num"),("MENG1_KW","num"),("MENG1_CNT","num"),
 ("MENG_KND2_NM","char"),("MENG2_HP","num"),("MENG2_KW","num"),("MENG2_CNT","num"),
 ("LNCH_DE","date"),("USG1_NM","char"),("USG2_NM","char"),("LAST_INSP_DE","date"),
 ("NXTM_INSP_KND1_NM","char"),("NXTM_INSP_DT1","date"),("NXTM_INSP_KND2_NM","char"),("NXTM_INSP_DT2","date"),
 ("NXTM_INSP_KND3_NM","char"),("NXTM_INSP_DT3","date"),("NXTM_INSP_KND4_NM","char"),("NXTM_INSP_DT4","date"),
 ("NXTM_INSP_KND5_NM","char"),("NXTM_INSP_DT5","date"),("CERT_EXPRY_DE","date"),
 ("LAYUP_YN","char"),("NVGT_HLT_BGNG_DE","date"),("NVGT_HLT_END_DE","date"),
 ("PSNR_SPCL_GRD","num"),("PSNR_GRD1","num"),("PSNR_GRD2","num"),("PSNR_GRD3","num"),
 ("PSNR_STOT","num"),("CREW_CNT","num"),("TMPR_EMKT_CNT","num"),("MAX_EMKT_PRSNL_SUM","num"),
]
SEP = "\x1f"  # Unit Separator — 데이터에 등장하지 않는 구분자

def clean(val, kind):
    v = val.strip()
    if v == "": return ""
    if kind == "num":  return v.replace(",", "")
    if kind == "date": return v[:10]  # YYYY-MM-DD (시각부 절삭, 전부 00:00:00)
    return v.replace(SEP, " ").replace("\n", " ").replace("\r", " ")

f = open(SRC, encoding="utf-8-sig"); r = csv.reader(f); header = next(r)
assert len(header) == len(COLS), f"컬럼수 불일치 {len(header)} vs {len(COLS)}"
n = 0
with open(DATA, "w", encoding="utf-8") as out:
    for row in r:
        if len(row) < len(COLS): row += [""] * (len(COLS) - len(row))
        out.write(SEP.join(clean(row[i], COLS[i][1]) for i in range(len(COLS))) + "\n")
        n += 1
print(f"정제 데이터 {n}행 → {DATA}")

# 컨트롤 파일
lines = [
 "OPTIONS (DIRECT=FALSE, ERRORS=1000, ROWS=2000)",
 "LOAD DATA",
 "CHARACTERSET AL32UTF8",
 "INFILE 'vsl_bsc.dat'",
 "BADFILE 'vsl_bsc.bad'",
 "DISCARDFILE 'vsl_bsc.dsc'",
 "INTO TABLE TB_VSL_BSC",
 "APPEND",
 "FIELDS TERMINATED BY X'1F'",
 "TRAILING NULLCOLS",
 "(",
 "  VSL_BSC_ID SEQUENCE(1,1),",
]
fld = []
for e, kind in COLS:
    if kind == "date":
        fld.append(f'  {e} DATE "YYYY-MM-DD" NULLIF {e}=BLANKS')
    elif kind == "num":
        fld.append(f'  {e} NULLIF {e}=BLANKS')
    else:
        fld.append(f'  {e} CHAR(4000) NULLIF {e}=BLANKS')
lines.append(",\n".join(fld))
lines.append(")")
open(CTL, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"컨트롤 파일 → {CTL}")
