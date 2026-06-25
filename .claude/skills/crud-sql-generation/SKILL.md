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

- 테이블당 5종: **목록조회(페이징)·단건조회·등록·수정·삭제**.
- 컬럼명은 표준용어 영문약어명(생성 객체와 동일).
- 바인드 변수 사용(SQL Injection 방지): Oracle `:param` / `#{param}`(MyBatis), PostgreSQL `$1` / `#{param}`.
- 페이징·채번·UPSERT는 DBMS 분기.

## Oracle 분기

```sql
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

- 테이블별 `sql/{테이블}_crud.sql`(대상 DBMS 분기), 필요 시 `mapper/{Domain}Mapper.xml`

## 경계

- 파라미터는 항상 바인드 변수(문자열 결합/`${}` 직접 치환 금지 — SQL Injection 방지).
- 동적 ORDER BY는 화이트리스트 검증 후에만 허용.
- 데이터를 임의로 변경·삭제 실행하지 않는다(SQL 작성·제공까지, 실행은 사용자/애플리케이션).
