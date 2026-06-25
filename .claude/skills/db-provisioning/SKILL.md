---
name: db-provisioning
description: 공공DB 인프라 프로비저닝 스킬. Docker로 대상 DBMS(Oracle/PostgreSQL) 컨테이너를 생성·기동·상태점검·정리한다. ECC docker-patterns를 베이스로 한다. 트리거 - "DB 컨테이너 생성", "Oracle/PostgreSQL 기동", "DB 프로비저닝", "docker DB".
allowed-tools: Read, Write, Grep, Glob, Bash
---

# db-provisioning (공공DB 인프라 프로비저닝)

> ECC `docker-patterns` 스킬을 베이스로, **대상 DBMS(Oracle/PostgreSQL) 컨테이너 프로비저닝**에 특화한다.
> 원본: [`../docker-patterns/SKILL.md`](../docker-patterns/SKILL.md) 를 필요 시 참조한다.

## 사용 시점

- dba-orchestrator 1단계(인프라 프로비저닝)
- "DB 컨테이너 생성/기동", "Oracle/PostgreSQL 띄워줘"를 요청받을 때

## 대상 DBMS (필수 선행)

`대상 DBMS: Oracle | PostgreSQL` 를 확정한다. da-agent 산출물의 DBMS 또는 사용자 지정값. 기본 **Oracle 11g**.

## 보안 원칙 (security.md 준수)

- DB 비밀번호는 **환경변수**로 주입한다(`.env`, 하드코딩·커밋 금지).
- `.env`는 `.gitignore`에 포함되어야 한다.
- 컨테이너는 **로컬/개발용**을 전제로 한다. 운영 DB 프로비저닝은 범위 밖.

## Oracle 분기 (기본: 11g XE)

`docker-compose.db.yml` (Oracle):
```yaml
services:
  oracle:
    image: wnameless/oracle-xe-11g-r2     # 프로젝트 표준
    ports: ["1521:1521"]
    environment:
      ORACLE_ALLOW_REMOTE: "true"
    volumes: ["oracle_data:/u01/app/oracle"]
    healthcheck:
      test: ["CMD","sqlplus","-L","${DB_USER}/${DB_PASSWORD}@localhost:1521/XE"]
      interval: 10s
      timeout: 5s
      retries: 5
volumes: { oracle_data: {} }
```
- 접속: `jdbc:oracle:thin:@localhost:1521:XE`, 상태점검 `nc -zv localhost 1521`

## PostgreSQL 분기

`docker-compose.db.yml` (PostgreSQL):
```yaml
services:
  postgres:
    image: postgres:16
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: "${DB_USER}"
      POSTGRES_PASSWORD: "${DB_PASSWORD}"
      POSTGRES_DB: "${DB_NAME}"
    volumes: ["pg_data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL","pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
volumes: { pg_data: {} }
```
- 접속: `postgresql://localhost:5432/${DB_NAME}`, 상태점검 `nc -zv localhost 5432`

## 절차

1. 대상 DBMS 확정 → 해당 분기 compose 작성.
2. `.env`에 `DB_USER/DB_PASSWORD/DB_NAME`(PostgreSQL) 정의(미커밋).
3. 기동: `docker compose -f docker-compose.db.yml up -d`
4. 상태점검: `docker ps`, 포트 확인, healthcheck 통과 대기.
5. 접속 정보를 2단계(db-object-creation)에 전달한다.

## 관리 명령

| 작업 | Oracle | PostgreSQL |
|---|---|---|
| 기동 | `docker compose -f docker-compose.db.yml up -d` | 동일 |
| 상태 | `docker ps \| grep oracle` / `nc -zv localhost 1521` | `docker ps \| grep postgres` / `nc -zv localhost 5432` |
| 접속 | `sqlplus ${DB_USER}/${DB_PASSWORD}@localhost:1521/XE` | `psql -h localhost -U ${DB_USER} ${DB_NAME}` |
| 정지 | `docker compose -f docker-compose.db.yml down` | 동일 |
| 데이터 보존 | named volume(`oracle_data`) 유지 | named volume(`pg_data`) 유지 |

## 산출물

- `docker-compose.db.yml`(대상 DBMS 분기), `.env.example`(키 목록만, 값 제외)
- 기동·상태점검 결과 요약, 접속 정보(비밀번호 제외)

## 경계

- 비밀번호 하드코딩·커밋 금지(환경변수).
- 운영 DB·클라우드 프로비저닝은 범위 밖(로컬/개발 컨테이너 한정).
- 데이터 볼륨을 임의 삭제하지 않는다(`down -v` 금지, 명시 요청 시에만).
