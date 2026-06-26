---
name: db-object-creation
description: 공공DB 객체 생성 스킬. da-agent 산출물(테이블/컬럼정의서, 마이그레이션)을 입력받아 대상 DBMS(Oracle/PostgreSQL)에 DB·user/스키마·테이블스페이스·테이블·인덱스를 생성한다. 트리거 - "DB 생성", "user 생성", "테이블 생성", "인덱스 설정", "테이블스페이스".
allowed-tools: Read, Write, Grep, Glob, Bash
---

# db-object-creation (공공DB 객체 생성)

> da-agent의 DB 산출물을 입력으로, 프로비저닝된 DBMS에 실제 객체를 생성한다. 표준용어 영문약어명·표준도메인을 그대로 반영한다.

## 사용 시점

- dba-orchestrator 2단계(DB 객체 생성)
- "DB/user/테이블스페이스/테이블/인덱스 생성"을 요청받을 때

## 입력

- da-agent 산출물: `docs/04. db-deliverables/{요구사항번호}/`
  - `{요구사항번호}-테이블정의서.xlsx`, `{요구사항번호}-컬럼정의서.xlsx`
  - `migrations/{순번}_{설명}.up/.down.sql` (있으면 우선 활용)
- `대상 DBMS`, 프로비저닝 접속 정보(db-provisioning 1단계)

## 생성 순서 (의존성)

```text
1) 테이블스페이스  → 2) user/스키마(+권한)  → 3) 테이블  → 4) 인덱스  → 5) 제약/시퀀스 →  6) 코맨트 입력
```

각 단계 DDL을 `ddl/`에 저장하고(가역 위해 drop 스크립트 동반), 접속하여 실행한다.

## Oracle 분기

```sql
-- 1) 테이블스페이스
CREATE TABLESPACE TBS_APP DATAFILE 'tbs_app01.dbf' SIZE 100M AUTOEXTEND ON;
-- 2) user(=스키마) + 권한
CREATE USER &APP_USER IDENTIFIED BY "&APP_PWD" DEFAULT TABLESPACE TBS_APP QUOTA UNLIMITED ON TBS_APP;
GRANT CONNECT, RESOURCE, CREATE VIEW TO &APP_USER;
-- 3) 테이블 (컬럼정의서 → VARCHAR2/NUMBER/DATE)
CREATE TABLE MBER ( MBER_NO CHAR(13) NOT NULL, MBER_NM VARCHAR2(100), CONSTRAINT PK_MBER PRIMARY KEY (MBER_NO) ) TABLESPACE TBS_APP;
-- 4) 인덱스 / 5) 시퀀스
CREATE INDEX IX_MBER_NM ON MBER (MBER_NM) TABLESPACE TBS_APP;
CREATE SEQUENCE SEQ_MBER START WITH 1 INCREMENT BY 1;
-- 6) 코멘트 (테이블 + 전 컬럼 — 한글컬럼명/설명을 컬럼정의서에서)
COMMENT ON TABLE  MBER         IS '회원';
COMMENT ON COLUMN MBER.MBER_NO IS '회원번호';
COMMENT ON COLUMN MBER.MBER_NM IS '회원명';
```
- 실행: `sqlplus ${DB_USER}/${DB_PASSWORD}@localhost:1521/XE @ddl/xxx.sql`
- Oracle에서 **user = 스키마**. 식별자 30바이트 이내.

## PostgreSQL 분기

```sql
-- 1) 테이블스페이스 (선택)
CREATE TABLESPACE tbs_app LOCATION '/var/lib/postgresql/tbs_app';
-- 2) database / role(user) / schema + 권한
CREATE DATABASE :app_db TABLESPACE tbs_app;
CREATE ROLE :app_user LOGIN PASSWORD :'app_pwd';
CREATE SCHEMA app AUTHORIZATION :app_user;
GRANT USAGE, CREATE ON SCHEMA app TO :app_user;
-- 3) 테이블 (컬럼정의서 → VARCHAR/NUMERIC/TIMESTAMP)
CREATE TABLE app.mber ( mber_no CHAR(13) NOT NULL, mber_nm VARCHAR(100), CONSTRAINT pk_mber PRIMARY KEY (mber_no) ) TABLESPACE tbs_app;
-- 4) 인덱스 / 5) 시퀀스
CREATE INDEX ix_mber_nm ON app.mber (mber_nm);
CREATE SEQUENCE app.seq_mber START 1 INCREMENT 1;
-- 6) 코멘트 (테이블 + 전 컬럼)
COMMENT ON TABLE  app.mber         IS '회원';
COMMENT ON COLUMN app.mber.mber_no IS '회원번호';
COMMENT ON COLUMN app.mber.mber_nm IS '회원명';
```
- 실행: `psql -h localhost -U ${DB_USER} -d ${DB_NAME} -f ddl/xxx.sql`
- PostgreSQL은 **database/role/schema 분리**. 식별자 63바이트 이내.

## DBMS 분기 대응표

| 객체 | Oracle | PostgreSQL |
|---|---|---|
| 사용자/스키마 | `CREATE USER`(=스키마) | `CREATE ROLE` + `CREATE SCHEMA` |
| 데이터베이스 | 인스턴스(XE) 공유 | `CREATE DATABASE` 별도 |
| 문자/숫자/날짜 | VARCHAR2/NUMBER/DATE | VARCHAR/NUMERIC/TIMESTAMP |
| 채번 | SEQUENCE + .NEXTVAL | SEQUENCE / IDENTITY |
| 권한 | GRANT CONNECT,RESOURCE | GRANT USAGE,CREATE ON SCHEMA |
| 코멘트 | `COMMENT ON TABLE/COLUMN … IS '…'` | `COMMENT ON TABLE/COLUMN … IS '…'`(동일) |

## 절차

1. 산출물(컬럼/테이블정의서·migrations) 로드 → 대상 DBMS 분기 DDL 생성(`ddl/` 저장, drop 동반). DDL에는 **6) 코멘트(COMMENT ON TABLE·전 컬럼)**까지 포함한다(한글 테이블명·컬럼명/설명은 정의서에서).
2. 의존 순서(테이블스페이스→user→테이블→인덱스→제약/시퀀스→**코멘트**)대로 실행한다.
3. 실행 결과(객체 생성/오류)를 점검하고 컬럼정의서와 대조 검증한다(코멘트 누락 여부 포함).
4. 접속·스키마 정보를 3단계(crud-sql-generation)에 전달한다.

## 산출물

- `ddl/{순번}_{객체}.sql`(+ drop), 실행 로그 요약, 생성 객체 목록(정의서 대비 일치 검증)

## 경계

- 표준 타입/길이를 임의 변경하지 않는다(컬럼정의서·표준도메인 준수).
- 운영 DB에 무단 실행하지 않는다(프로비저닝된 개발 컨테이너 대상, 위험 DDL은 사용자 확인).
- 비밀번호는 환경변수/치환변수로 주입(하드코딩 금지).
