---
name: crud-sql-generation
description: 생성된 테이블의 기본 CRUD SQL 생성 스킬. 컬럼정의서·생성 객체를 기반으로 대상 DBMS(Oracle/PostgreSQL) 문법의 SELECT/INSERT/UPDATE/DELETE(+페이징·단건조회)를 작성한다. 트리거 - "CRUD SQL", "기본 쿼리 생성", "SELECT/INSERT/UPDATE/DELETE", "Mapper SQL".
allowed-tools: Read, Write, Grep, Glob, Bash
---

# crud-sql-generation (기본 CRUD SQL 생성)

> 생성된 테이블별로 기본 CRUD SQL을 대상 DBMS 문법으로 제공한다. 컬럼·PK는 컬럼정의서/생성 객체에서 가져온다.

## 사용 시점

- dba-orchestrator 3단계(CRUD 제공)
- "CRUD SQL", "기본 쿼리/Mapper SQL 생성"을 요청받을 때

## 입력

- `{요구사항번호}-컬럼정의서.xlsx` 또는 db-object-creation의 생성 객체(테이블·컬럼·PK·NOT NULL)
- `대상 DBMS`

## 생성 규칙

- **DDL 동봉(self-contained)**: 각 테이블 스크립트는 **상단에 DDL(① CREATE TABLE ② CREATE INDEX ③ COMMENT(테이블·컬럼)) 을 함께 포함**하고, 그 아래 CRUD를 둔다. 한 파일만으로 테이블 생성~기본쿼리까지 재현 가능해야 한다.
  - DDL 정의는 db-object-creation의 `ddl/`(컬럼정의서·생성 객체)와 **동일**해야 한다(불일치 금지).
  - 시퀀스 채번 테이블은 `CREATE SEQUENCE`도 포함한다.
  - 멱등성: DDL 앞에 `DROP`(가드)·`WHENEVER SQLERROR` 등 재실행 안전장치를 둔다(대상 DBMS 분기).
- 테이블당 CRUD 5종: **목록조회(페이징)·단건조회·등록·수정·삭제**.
- 컬럼명은 표준용어 영문약어명(생성 객체와 동일).
- 바인드 변수 사용(SQL Injection 방지): Oracle `:param` / `#{param}`(MyBatis), PostgreSQL `$1` / `#{param}`.
- 페이징·채번·UPSERT는 DBMS 분기.

## 스크립트 구성 (DDL + CRUD 순서)

```text
sql/{테이블}_crud.sql
├── [1] DDL — 테이블 생성   : (DROP 가드) CREATE TABLE / CREATE SEQUENCE
├── [2] DDL — 인덱스        : CREATE INDEX / (PK·UK는 테이블 제약)
├── [3] DDL — 코멘트        : COMMENT ON TABLE / COMMENT ON COLUMN (전 컬럼)
└── [4] CRUD               : 목록조회·단건조회·등록·수정·삭제
```

## Oracle 분기

```sql
-- ============ [1~3] DDL: 테이블·인덱스·코멘트 (동봉) ============
WHENEVER SQLERROR CONTINUE
DROP TABLE MBER CASCADE CONSTRAINTS;
DROP SEQUENCE SEQ_MBER;
WHENEVER SQLERROR EXIT SQL.SQLCODE
CREATE TABLE MBER (
  MBER_NO  NUMBER       NOT NULL,
  MBER_NM  VARCHAR2(60) NOT NULL,
  CONSTRAINT PK_MBER PRIMARY KEY (MBER_NO)
);
CREATE SEQUENCE SEQ_MBER START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE INDEX IX_MBER_NM ON MBER (MBER_NM);
COMMENT ON TABLE  MBER         IS '회원';
COMMENT ON COLUMN MBER.MBER_NO IS '회원번호';
COMMENT ON COLUMN MBER.MBER_NM IS '회원명';

-- ============ [4] CRUD ============
-- 목록조회 (ROWNUM 3중 페이징)
SELECT * FROM (
  SELECT ROWNUM RN, A.* FROM (
    SELECT MBER_NO, MBER_NM FROM MBER WHERE 1=1
      AND (MBER_NM LIKE '%' || :searchKeyword || '%' OR :searchKeyword IS NULL)
    ORDER BY MBER_NO
  ) A WHERE ROWNUM <= :lastIndex
) WHERE RN > :firstIndex;

-- 단건조회
SELECT MBER_NO, MBER_NM FROM MBER WHERE MBER_NO = :mberNo;
-- 등록 (시퀀스 채번 시 SEQ_MBER.NEXTVAL)
INSERT INTO MBER (MBER_NO, MBER_NM) VALUES (:mberNo, :mberNm);
-- 수정
UPDATE MBER SET MBER_NM = :mberNm WHERE MBER_NO = :mberNo;
-- 삭제
DELETE FROM MBER WHERE MBER_NO = :mberNo;
```

## PostgreSQL 분기

```sql
-- 목록조회 (LIMIT/OFFSET)
SELECT mber_no, mber_nm FROM app.mber
 WHERE ($1::text IS NULL OR mber_nm LIKE '%' || $1 || '%')
 ORDER BY mber_no LIMIT $2 OFFSET $3;

-- 단건조회
SELECT mber_no, mber_nm FROM app.mber WHERE mber_no = $1;
-- 등록 (RETURNING)
INSERT INTO app.mber (mber_no, mber_nm) VALUES ($1, $2) RETURNING mber_no;
-- 수정
UPDATE app.mber SET mber_nm = $2 WHERE mber_no = $1;
-- 삭제
DELETE FROM app.mber WHERE mber_no = $1;
-- UPSERT (선택)
INSERT INTO app.mber (mber_no, mber_nm) VALUES ($1, $2)
  ON CONFLICT (mber_no) DO UPDATE SET mber_nm = EXCLUDED.mber_nm;
```

## DBMS 분기 대응표

| 항목 | Oracle | PostgreSQL |
|---|---|---|
| 페이징 | ROWNUM 3중 서브쿼리 | `LIMIT … OFFSET …` |
| 채번 | `SEQ.NEXTVAL` | `RETURNING` / IDENTITY |
| UPSERT | `MERGE` | `ON CONFLICT … DO UPDATE` |
| 바인드 | `:param` | `$n` |

## MyBatis 연계 (선택, egov 표준)

요청 시 동일 SQL을 MyBatis Mapper XML(`#{param}`, `<where>`, `<if>`, `<![CDATA[]]>`)로 변환한다. eGov 네이밍(`SampleDAO`, `selectList`)을 따른다.

## 산출물

- 테이블별 `sql/{테이블}_crud.sql` — **DDL(테이블 생성·인덱스·코멘트) + CRUD 동봉**(대상 DBMS 분기), 필요 시 `mapper/{Domain}Mapper.xml`
- DDL 부분은 db-object-creation `ddl/`와 정의 일치(같은 컬럼·타입·제약·인덱스·코멘트)

## 경계

- 파라미터는 항상 바인드 변수(문자열 결합/`${}` 직접 치환 금지 — SQL Injection 방지).
- 동적 ORDER BY는 화이트리스트 검증 후에만 허용.
- 데이터를 임의로 변경·삭제 실행하지 않는다(SQL 작성·제공까지, 실행은 사용자/애플리케이션).
