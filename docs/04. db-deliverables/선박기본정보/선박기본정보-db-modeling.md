# 데이터 모델링 — 선박기본정보

## 개요
- 대상 DBMS: **Oracle 11g XE**
- 적재 대상 계정: **komsa** (KOMSA 선박 도메인)
- 업무영역: 선박(VSL) / 주제영역: 선박 기본정보 / 원천: `work/선박기본정보.csv` (45컬럼, 68,933행)
- 모델 형태: **원천 1:1 적재형 단일 테이블**(스테이징/기본정보 마스터). 반복그룹은 정규화 후보로 표기하되, 본 적재 목적상 원천 구조를 유지한다.

## 엔터티 목록
| 엔터티명 | 설명 | 주식별자 | 수퍼타입 | 개인정보 |
|---|---|---|---|---|
| 선박기본정보 | 선박 1척의 제원·검사·정원 기본정보 | 선박기본정보ID(인조키) | - | 없음(선박명·선적항은 공개정보) |

> **인조키 채택 사유**: 자연키 후보 `선박번호`에 **중복 22건** 존재(68,933행 중 고유 68,911) → 유일성 미충족. 주식별자는 SEQUENCE 인조키 `선박기본정보ID`, `선박번호`는 비유일 탐색키(인덱스)로 둔다.

## 반복그룹(정규화 후보)
| 반복그룹 | 원천 컬럼 | 정규화 후보 엔터티 | 처리 |
|---|---|---|---|
| 주기관 1~2 | 주기관종류/마력/KW/대 ×2 | 선박주기관(1:N) | 보완 후보 — 본 적재는 평면 유지 |
| 차기검사 1~5 | 차기검사종류/일 ×5 | 선박차기검사(1:N) | 보완 후보 — 본 적재는 평면 유지 |
| 여객등급 | 특/1/2/3등급 | 여객정원(1:N) | 보완 후보 — 본 적재는 평면 유지 |

## 속성/컬럼 매핑 (45 → 물리컬럼, 영문명 후보)
| # | 한글컬럼 | 영문컬럼(후보) | 타입(후보) | 코드성 | 비고 |
|---|---|---|---|---|---|
| - | 선박기본정보ID(인조키) | VSL_BSC_ID | NUMBER | PK | SEQUENCE 채번 |
| 1 | 구분 | DIV_NM | VARCHAR2(20) | 범주 | 어선/일반선 |
| 2 | 선박번호 | VSL_NO | VARCHAR2(20) | - | 비유일 인덱스 |
| 3 | 선박명 | VSL_NM | VARCHAR2(200) | - | |
| 4 | 관할지사 | BROF_NM | VARCHAR2(60) | 범주 | 지사명 |
| 5 | 선박구분 | VSL_SE_NM | VARCHAR2(30) | 범주 | 기선/부선 등 |
| 6 | 선박재질 | VSL_MTPRPT_NM | VARCHAR2(30) | 범주 | FRP/강 등 |
| 7 | 선적항 | SHPM_PRT_NM | VARCHAR2(100) | - | |
| 8 | 길이 | LEN | NUMBER(10,2) | - | m |
| 9 | 너비 | BRTH | NUMBER(10,2) | - | m |
| 10 | 깊이 | DPTH | NUMBER(10,2) | - | m |
| 11 | 총톤수 | TOT_TON | NUMBER(13,2) | - | 천단위콤마 제거 |
| 12 | 주기관종류1 | MENG_KND1_NM | VARCHAR2(40) | 범주 | |
| 13 | 주기관1마력 | MENG1_HP | NUMBER(10) | - | |
| 14 | 주기관1KW | MENG1_KW | NUMBER(10) | - | |
| 15 | 주기관1_대 | MENG1_CNT | NUMBER(5) | - | |
| 16 | 주기관종류2 | MENG_KND2_NM | VARCHAR2(40) | 범주 | |
| 17 | 주기관2마력 | MENG2_HP | NUMBER(10) | - | |
| 18 | 주기관2KW | MENG2_KW | NUMBER(10) | - | |
| 19 | 주기관2_대 | MENG2_CNT | NUMBER(5) | - | |
| 20 | 진수일 | LNCH_DE | DATE | - | YYYY-MM-DD |
| 21 | 용도1 | USG1_NM | VARCHAR2(60) | - | |
| 22 | 용도2 | USG2_NM | VARCHAR2(60) | - | |
| 23 | 최종검사일 | LAST_INSP_DE | DATE | - | YYYY-MM-DD |
| 24 | 차기검사종류1 | NEXT_INSP_KND1_NM | VARCHAR2(20) | 범주 | |
| 25 | 차기검사일1 | NEXT_INSP_DT1 | DATE | - | YYYY-MM-DD HH24:MI:SS |
| 26 | 차기검사종류2 | NEXT_INSP_KND2_NM | VARCHAR2(20) | 범주 | |
| 27 | 차기검사일2 | NEXT_INSP_DT2 | DATE | - | |
| 28 | 차기검사종류3 | NEXT_INSP_KND3_NM | VARCHAR2(20) | 범주 | |
| 29 | 차기검사일3 | NEXT_INSP_DT3 | DATE | - | |
| 30 | 차기검사종류4 | NEXT_INSP_KND4_NM | VARCHAR2(20) | 범주 | |
| 31 | 차기검사일4 | NEXT_INSP_DT4 | DATE | - | |
| 32 | 차기검사종류5 | NEXT_INSP_KND5_NM | VARCHAR2(20) | 범주 | |
| 33 | 차기검사일5 | NEXT_INSP_DT5 | DATE | - | |
| 34 | 증서만료일자 | CERT_EXPRY_DE | DATE | - | YYYY-MM-DD |
| 35 | 계선여부 | LAYUP_YN | CHAR(1) | Y/N | 공백 다수 |
| 36 | 운항중지시작일 | NVGT_HLT_BGNDE | DATE | - | |
| 37 | 운항중지종료일 | NVGT_HLT_ENDDE | DATE | - | |
| 38 | 여객_특등급 | PSNR_SPCL_CLS | NUMBER(6) | - | 정원(명) |
| 39 | 여객_1등급 | PSNR_CLS1 | NUMBER(6) | - | |
| 40 | 여객_2등급 | PSNR_CLS2 | NUMBER(6) | - | |
| 41 | 여객_3등급 | PSNR_CLS3 | NUMBER(6) | - | |
| 42 | 여객_소계 | PSNR_SUBTOT | NUMBER(8) | - | |
| 43 | 선원수 | CREW_CNT | NUMBER(6) | - | |
| 44 | 임시승선자수 | TMP_BORD_CNT | NUMBER(6) | - | |
| 45 | 최대승선인원합계 | MAX_BORD_PRSNL_TOT | NUMBER(8) | - | |
| - | 적재일시(관리) | LOAD_DT | TIMESTAMP | - | 적재 추적용, DEFAULT SYSTIMESTAMP |

## 물리 테이블명 (테이블명명규칙 적용)
- 한글명: **선박기본정보**
- 영문명: **TB_VSL_BSC** — `TB_[업무영역:VSL 선박]_[관리대상/유형:BSC 기본]` 구조.
  - 금지명 회피: `정보(INFO)`는 무의미 접미어로 제외 → `기본=BSC`로 표기.
  - 표준단어 영문약어명 기반(선박=VSL, 기본=BSC).

## 키/제약/인덱스
| 구분 | 대상 | 비고 |
|---|---|---|
| PK | PK_TB_VSL_BSC (VSL_BSC_ID) | 인조키 |
| SEQUENCE | SEQ_TB_VSL_BSC | START 1, NOCACHE |
| INDEX | IX_TB_VSL_BSC_VSL_NO (VSL_NO) | 비유일(선박번호 중복 허용) |
| NOT NULL | VSL_BSC_ID | 그 외 원천 결측 다수로 NULL 허용 |

## 업무규칙
- 선박번호는 식별 대상이나 중복 존재 → UK 불가, 비유일 인덱스로 운영.
- 날짜 컬럼은 2종 포맷(`YYYY-MM-DD`, `YYYY-MM-DD HH24:MI:SS.FF3`) → DATE 변환, 공백은 NULL.
- 숫자 컬럼의 천단위 콤마(예: `2,831.00`)는 제거 후 적재.
- 계선여부는 Y/N, 공백은 NULL.

## 표준화 검토 요청 항목 (2단계 metadata-agent)
- 컬럼 영문약어명 표준 일치 확인: 너비(BRTH)·관할지사(BROF)·주기관(MENG)·승선(BORD)·계선(LAYUP) 등 사전 미등록 후보 → 공공표준 우선, 없으면 KOMSA 기관표준 등록.
- 코드성 컬럼(_NM 범주): 구분/선박구분/선박재질/주기관종류/차기검사종류/계선여부 → 표준코드 등록 검토.
