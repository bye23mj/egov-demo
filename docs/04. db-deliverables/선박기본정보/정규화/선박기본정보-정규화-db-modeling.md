# 데이터 모델링 (정규화) — 선박기본정보

> ADR-0001의 후속 과제: 적재형 단일테이블(TB_VSL_BSC)의 **반복그룹 3종을 1:N 정규화**한다.
> 현행 적재형 산출물(`../`)은 보존하고, 본 산출물은 **목표(정규화) 모델**을 정의한다.

## 개요
- 대상 DBMS: **Oracle 11g XE** / 스키마: **komsa**
- 변환: 단일 테이블 → **부모 1 + 자식 3 (1:N)**
- 정규화 대상 반복그룹: 주기관(×2), 차기검사(×5), 여객등급(특/1/2/3)

## 엔터티 관계 (논리)
```
선박기본정보(1) ──< 선박주기관(N)
선박기본정보(1) ──< 선박차기검사(N)
선박기본정보(1) ──< 선박여객정원(N)
```

## 엔터티 목록
| 엔터티 | 영문테이블 | 설명 | 주식별자 | 관계 |
|---|---|---|---|---|
| 선박기본정보 | TB_VSL_BSC | 선박 제원·검사기준·정원 요약(반복그룹 제거) | VSL_BSC_ID | 부모 |
| 선박주기관 | TB_VSL_MENG | 선박별 주기관 N건 | VSL_MENG_ID | 자식(1:N) |
| 선박차기검사 | TB_VSL_NXTM_INSP | 선박별 차기검사 N건 | VSL_NXTM_INSP_ID | 자식(1:N) |
| 선박여객정원 | TB_VSL_PSNR_CPCT | 선박별 여객등급 정원 N건 | VSL_PSNR_CPCT_ID | 자식(1:N) |

## 부모 TB_VSL_BSC (정규화 후 — 반복그룹 컬럼 제거)
- **유지**: VSL_BSC_ID(PK), 구분·선박번호·선박명·관할지사·선박구분·선박재질·선적항·길이·너비·깊이·총톤수·진수일·용도1·2·최종검사일·증서만료일자·계선여부·운항중지시작/종료일·여객소계·선원수·임시승선자수·최대승선인원합계·적재일시
- **제거(자식 이관)**: 주기관종류1/마력1/KW1/대1·주기관종류2/마력2/KW2/대2 → TB_VSL_MENG / 차기검사종류1~5·차기검사일1~5 → TB_VSL_NXTM_INSP / 여객특·1·2·3등급 → TB_VSL_PSNR_CPCT
- 비고: `여객_소계`는 집계요약으로 부모 유지(자식은 등급별 명세)

## 자식 1 — 선박주기관 TB_VSL_MENG (1:N)
| 한글컬럼 | 영문컬럼 | 타입 | 키 | 표준단어 | 설명 |
|---|---|---|---|---|---|
| 선박주기관ID | VSL_MENG_ID | NUMBER | PK | 인조키 | SEQ 채번 |
| 선박기본정보ID | VSL_BSC_ID | NUMBER | FK | - | →TB_VSL_BSC |
| 주기관순번 | MENG_SEQ | NUMBER(2) | UK(複) | 주기관(MENG)+순서(SEQ) | 1~2 |
| 주기관종류 | MENG_KND_NM | VARCHAR2(40) | - | 주기관(MENG)+종류(KND) | |
| 주기관마력 | MENG_HP | NUMBER(10) | - | 주기관(MENG)+마력(HP) | |
| 주기관KW | MENG_KW | NUMBER(10) | - | 주기관(MENG)+KW | |
| 주기관대수 | MENG_CNT | NUMBER(5) | - | 주기관(MENG)+수(CNT) | |
- 복합 유일키: (VSL_BSC_ID, MENG_SEQ)

## 자식 2 — 선박차기검사 TB_VSL_NXTM_INSP (1:N)
| 한글컬럼 | 영문컬럼 | 타입 | 키 | 표준단어 | 설명 |
|---|---|---|---|---|---|
| 선박차기검사ID | VSL_NXTM_INSP_ID | NUMBER | PK | 인조키 | SEQ 채번 |
| 선박기본정보ID | VSL_BSC_ID | NUMBER | FK | - | →TB_VSL_BSC |
| 차기검사순번 | NXTM_INSP_SEQ | NUMBER(2) | UK(複) | 차기(NXTM)+검사(INSP)+순서(SEQ) | 1~5 |
| 차기검사종류 | NXTM_INSP_KND_NM | VARCHAR2(20) | - | 차기검사+종류(KND) | |
| 차기검사일시 | NXTM_INSP_DT | DATE | - | 차기검사+일시(DT) | |
- 복합 유일키: (VSL_BSC_ID, NXTM_INSP_SEQ)

## 자식 3 — 선박여객정원 TB_VSL_PSNR_CPCT (1:N)
| 한글컬럼 | 영문컬럼 | 타입 | 키 | 표준단어 | 설명 |
|---|---|---|---|---|---|
| 선박여객정원ID | VSL_PSNR_CPCT_ID | NUMBER | PK | 인조키 | SEQ 채번 |
| 선박기본정보ID | VSL_BSC_ID | NUMBER | FK | - | →TB_VSL_BSC |
| 여객등급구분 | PSNR_GRD_SE | VARCHAR2(10) | UK(複) | 여객(PSNR)+등급(GRD)+구분(SE) | 특/1/2/3 |
| 여객정원수 | PSNR_CPCT_CNT | NUMBER(6) | - | 여객(PSNR)+정원(PSCP)+수(CNT) | 등급별 정원 |
- 복합 유일키: (VSL_BSC_ID, PSNR_GRD_SE)

## 테이블명명규칙 적용
- TB_VSL_MENG = `TB_[VSL 선박]_[MENG 주기관]` / TB_VSL_NXTM_INSP = 선박차기검사 / TB_VSL_PSNR_CPCT = 선박여객정원
- 모두 표준단어 영문약어 기반, 금지명 회피, 엔터티 정합. Oracle 30byte 이내(최장 VSL_NXTM_INSP_ID=16).

## 업무규칙
- 자식 행은 원천 반복그룹에서 **값이 존재하는 슬롯만** 생성(NULL 슬롯 제외).
- FK는 ON DELETE CASCADE(부모 삭제 시 자식 정리) 또는 RESTRICT 중 운영정책에 따름 — 기본 RESTRICT.

## 표준화 검토 요청 항목 (2단계)
- 신규 단어: 순번→**순서(SEQ)** 표준 사용(순번 미등록), 정원→**PSCP** 사용. 구분/등급/주기관/검사는 기존 표준 재사용.
