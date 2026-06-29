# 데이터 모델링 — 보안관리

## 개요
- 대상 DBMS: **Oracle 11g**
- 업무영역: 보안(SEC) / 주제영역: **보안관리(권한·롤·그룹 기반 접근통제)**
- 원천: 전자정부 표준프레임워크(eGov) 공통컴포넌트 보안관리 5테이블 정의
- 모델 형태: **권한(Author) — 롤(Role) M:N 매핑 + 롤 자기참조 계층 + 권한그룹**의 RBAC(역할기반 접근통제) 모델
- 영문 물리명 정책: 원본 테이블ID/컬럼ID는 **eGov 공통컴포넌트 표준 객체명**이므로 영문 물리명을 **그대로 유지**한다(표준 준수). 표준화 검토는 한글 용어·도메인 매핑·검토의견 위주로 수행한다.
- 대상 사용자: 업무시스템 사용자 / 서비스 이용자 / DB관리자 / 스토리지관리자 등 보안 분류 대상

## 엔터티 목록
| 엔터티명 | 물리테이블명 | 설명 | 주식별자 | 엔터티유형 | 개인정보 |
|---|---|---|---|---|---|
| 권한정보 | COMTNAUTHORINFO | 보안 분류 단위(업무시스템 사용자/서비스 이용자/DB관리자/스토리지관리자 등) 권한 | 권한코드(AUTHOR_CODE) | 기본/마스터 | 없음 |
| 롤정보 | COMTNROLEINFO | 권한에 종속되는 보안요소(등록/수정/삭제 롤 등) | 롤코드(ROLE_CODE) | 기본/마스터 | 없음 |
| 권한그룹정보 | COMTNAUTHORGROUPINFO | 권한을 그룹별로 부여하기 위한 그룹 정보 | 그룹ID(GROUP_ID) | 기본/마스터 | 없음 |
| 권한롤관계 | COMTNAUTHORROLERELATE | 권한과 롤의 M:N 매핑 | 권한코드+롤코드 (복합) | 매핑/관계 | 없음 |
| 롤계층구조 | COMTNROLES_HIERARCHY | 롤 간 상하 계층 구조(자기참조) | 부모롤+자식롤 (복합) | 매핑/관계 | 없음 |

> 본 5테이블은 eGov 공통컴포넌트 표준 객체로, 임의 엔터티/속성을 추가하지 않는다(추측 금지). 관리컬럼(등록일시 등) 미정의 항목은 원본 정의를 그대로 따른다.

## 관계 (Relationship)
| # | 부모 엔터티 | 자식 엔터티 | 관계 | 카디널리티 | 식별/비식별 | FK 컬럼 |
|---|---|---|---|---|---|---|
| R1 | 권한정보 | 권한롤관계 | 권한은 여러 롤에 매핑된다 | 1:N | 식별 | AUTHOR_CODE → COMTNAUTHORINFO.AUTHOR_CODE |
| R2 | 롤정보 | 권한롤관계 | 롤은 여러 권한에 매핑된다 | 1:N | 식별 | ROLE_CODE → COMTNROLEINFO.ROLE_CODE |
| R3 | 롤정보 | 롤계층구조 (부모) | 롤은 상위 롤로 참조된다 | 1:N | 식별 | PARNTS_ROLE → COMTNROLEINFO.ROLE_CODE (보완 필요: 원본 FK 대상 명시 없음) |
| R4 | 롤정보 | 롤계층구조 (자식) | 롤은 하위 롤로 참조된다 | 1:N | 식별 | CHLDRN_ROLE → COMTNROLEINFO.ROLE_CODE (보완 필요: 원본 FK 대상 명시 없음) |

- **권한 ↔ 롤은 M:N** → 교차 엔터티 `권한롤관계(COMTNAUTHORROLERELATE)`로 해소(권한코드+롤코드 복합 PK).
- **롤계층구조**는 롤정보에 대한 **자기참조(self-reference)** 계층(부모롤-자식롤). 단, 원본 컬럼 길이 `VARCHAR2(30)`이 `ROLE_CODE VARCHAR2(50)`와 불일치 → 데이터구조검증에서 점검(아래 §검증 후보).
- **권한그룹정보(COMTNAUTHORGROUPINFO)**: 원본 정의상 권한과의 직접 FK가 명시되지 않음 → **독립 그룹 마스터**로 모델링. 권한-그룹 매핑 테이블은 입력에 없으므로 임의 생성하지 않는다(보완 필요로 표기).

## 속성/컬럼 매핑 (영문 물리명 유지)

### 1) 권한정보 — COMTNAUTHORINFO
| # | 한글컬럼 | 영문컬럼 | 타입 | NULL | 키 | 코드성 | 비고 |
|---|---|---|---|---|---|---|---|
| 1 | 권한코드 | AUTHOR_CODE | VARCHAR2(30) | NOT NULL | PK | - | 관리되는 코드 아님(자유식별값) |
| 2 | 권한명 | AUTHOR_NM | VARCHAR2(60) | NOT NULL | - | - | |
| 3 | 권한설명 | AUTHOR_DC | VARCHAR2(200) | NULL | - | - | |
| 4 | 권한생성일 | AUTHOR_CREAT_DE | CHAR(20) | NOT NULL | - | - | 문자형 일자(원본 CHAR(20)) |

### 2) 롤정보 — COMTNROLEINFO
| # | 한글컬럼 | 영문컬럼 | 타입 | NULL | 키 | 코드성 | 비고 |
|---|---|---|---|---|---|---|---|
| 1 | 롤코드 | ROLE_CODE | VARCHAR2(50) | NOT NULL | PK | - | 시스템 자동생성 ID |
| 2 | 롤명 | ROLE_NM | VARCHAR2(60) | NOT NULL | - | - | |
| 3 | 롤패턴 | ROLE_PTTRN | VARCHAR2(300) | NULL | - | - | URL/리소스 패턴 |
| 4 | 롤설명 | ROLE_DC | VARCHAR2(200) | NULL | - | - | |
| 5 | 롤유형 | ROLE_TY | VARCHAR2(80) | NULL | - | 범주 | |
| 6 | 롤정렬 | ROLE_SORT | VARCHAR2(10) | NULL | - | - | 정렬순서(문자형) |
| 7 | 롤생성일 | ROLE_CREAT_DE | CHAR(20) | NOT NULL | - | - | 문자형 일자(원본 CHAR(20)) |

### 3) 권한그룹정보 — COMTNAUTHORGROUPINFO
| # | 한글컬럼 | 영문컬럼 | 타입 | NULL | 키 | 코드성 | 비고 |
|---|---|---|---|---|---|---|---|
| 1 | 그룹ID | GROUP_ID | CHAR(20) | NOT NULL | PK | - | |
| 2 | 그룹명 | GROUP_NM | VARCHAR2(60) | NOT NULL | - | - | |
| 3 | 그룹생성일 | GROUP_CREAT_DE | CHAR(20) | NOT NULL | - | - | 문자형 일자(원본 CHAR(20)) |
| 4 | 그룹설명 | GROUP_DC | VARCHAR2(100) | NULL | - | - | |

### 4) 권한롤관계 — COMTNAUTHORROLERELATE
| # | 한글컬럼 | 영문컬럼 | 타입 | NULL | 키 | 코드성 | 비고 |
|---|---|---|---|---|---|---|---|
| 1 | 권한코드 | AUTHOR_CODE | VARCHAR2(30) | NOT NULL | PK,FK | - | → COMTNAUTHORINFO.AUTHOR_CODE |
| 2 | 롤코드 | ROLE_CODE | VARCHAR2(50) | NOT NULL | PK,FK | - | → COMTNROLEINFO.ROLE_CODE |
| 3 | 생성일시 | CREAT_DT | DATE | NULL | - | - | 날짜형(DATE) |

- 인덱스: i01(AUTHOR_CODE), i02(ROLE_CODE)

### 5) 롤계층구조 — COMTNROLES_HIERARCHY
| # | 한글컬럼 | 영문컬럼 | 타입 | NULL | 키 | 코드성 | 비고 |
|---|---|---|---|---|---|---|---|
| 1 | 부모롤 | PARNTS_ROLE | VARCHAR2(30) | NOT NULL | PK,FK | - | → COMTNROLEINFO.ROLE_CODE (길이 불일치 점검) |
| 2 | 자식롤 | CHLDRN_ROLE | VARCHAR2(30) | NOT NULL | PK,FK | - | → COMTNROLEINFO.ROLE_CODE (길이 불일치 점검) |

- 인덱스: i01(PARNTS_ROLE), i02(CHLDRN_ROLE)

## 물리 테이블명 (테이블명명규칙 검토)
- 본 5테이블은 eGov 공통컴포넌트 표준 객체명(`COMTN...`)으로 **물리명 변경 금지**(표준 준수).
- 테이블명명규칙(`TB_[업무영역]_[관리대상]_[유형]`)은 신규 테이블 생성 시 적용 기준이며, 본 건은 기존 표준 객체이므로 **현행 유지**가 표준 부합. (검토의견은 표준화검토 단계에서 기록)

## 키/제약/인덱스 요약
| 테이블 | PK | FK | INDEX | NOT NULL |
|---|---|---|---|---|
| COMTNAUTHORINFO | AUTHOR_CODE | - | (PK) | AUTHOR_CODE, AUTHOR_NM, AUTHOR_CREAT_DE |
| COMTNROLEINFO | ROLE_CODE | - | (PK) | ROLE_CODE, ROLE_NM, ROLE_CREAT_DE |
| COMTNAUTHORGROUPINFO | GROUP_ID | - | (PK) | GROUP_ID, GROUP_NM, GROUP_CREAT_DE |
| COMTNAUTHORROLERELATE | AUTHOR_CODE+ROLE_CODE | AUTHOR_CODE→AUTHORINFO, ROLE_CODE→ROLEINFO | i01(AUTHOR_CODE), i02(ROLE_CODE) | AUTHOR_CODE, ROLE_CODE |
| COMTNROLES_HIERARCHY | PARNTS_ROLE+CHLDRN_ROLE | PARNTS_ROLE→ROLEINFO, CHLDRN_ROLE→ROLEINFO | i01(PARNTS_ROLE), i02(CHLDRN_ROLE) | PARNTS_ROLE, CHLDRN_ROLE |

## 업무규칙
- 권한(AUTHOR)은 보안 분류 단위이며 롤(ROLE)을 M:N으로 가진다.
- 롤은 자기참조 계층(부모-자식)으로 상속/포함 관계를 표현한다(Spring Security RoleHierarchy 대응).
- 권한코드는 "관리되는 코드 아님" = 표준코드 대상 아님(자유 식별값). 롤코드는 시스템 자동생성 ID.
- 생성일 컬럼은 원본이 CHAR(20)(권한/롤/그룹) 또는 DATE(권한롤관계 CREAT_DT)로 혼재 → 표준도메인 매핑 시 점검.

## 데이터구조검증 후보 (3단계 입력)
1. **롤계층구조 FK 길이 불일치**: PARNTS_ROLE/CHLDRN_ROLE `VARCHAR2(30)` vs 참조 대상 `ROLE_CODE VARCHAR2(50)` → 잠재 절단/무결성 리스크. (보완 후보)
2. **롤계층구조 FK 대상 명시 없음**: 원본은 PK,FK만 표기, 참조 테이블 미기재 → COMTNROLEINFO 추정. (확인/보완 후보)
3. **권한그룹-권한 연계 부재**: COMTNAUTHORGROUPINFO와 권한 매핑 테이블 입력 없음 → 독립 그룹으로 유지, 임의 생성 금지.
4. **생성일 도메인 일관성**: CHAR(20) 문자형 일자 vs DATE 혼재 → 표준도메인 매핑 검토.

## 대상 DBMS 제약 (Oracle 11g)
- VARCHAR2/CHAR/DATE 모두 Oracle 11g 호환. 자기참조 FK·복합 PK 지원.
- 식별자 길이 30byte 이내(11g 한계) — 모든 테이블/컬럼/인덱스명 적합(COMTN... 최장 ≤ 22자).
