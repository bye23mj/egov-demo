---
name: db-migrations
description: 공공데이터베이스 스키마 변경관리 스킬. 대상 DBMS(Oracle/PostgreSQL)에 따라 안전·가역(롤백 가능)·무중단 마이그레이션을 작성한다. 표준용어 영문약어명·표준도메인을 준수하고 변경 시 메타데이터·산출물과 동기화한다. 트리거 - "스키마 변경", "마이그레이션", "테이블/컬럼 변경", "DDL 작성".
allowed-tools: Read, Write, Grep, Glob, Bash
---

# db-migrations (공공DB 스키마 변경관리)

> ECC `database-migrations` 스킬의 안전·가역·무중단 원칙을 공공데이터베이스 기준으로 현지화하고, **대상 DBMS에 따라 Oracle / PostgreSQL로 분기**한다.
> 방법론 원본(범용·다양한 ORM 포함): [`../database-migrations/SKILL.md`](../database-migrations/SKILL.md) 를 필요 시 참조한다.

## 사용 시점

- 테이블/컬럼 생성·변경·삭제, 인덱스/제약 변경
- 데이터 백필·전환(backfill/transform)
- 무중단 스키마 변경 계획
- da-agent 5단계(변경관리)에서 호출

## 대상 DBMS 선택 (필수 선행)

작업 시작 시 **대상 DBMS**를 확정한다. 입력 `{요구사항번호}-db-modeling.md`의 `대상 DBMS` 항목 또는 사용자 지정값을 사용한다. 기본값은 본 프로젝트 표준인 **Oracle 11g**다.

```text
대상 DBMS: Oracle | PostgreSQL
```

## 공통 원칙 (ECC 현지화)

1. **가역성**: 모든 마이그레이션은 `up`(적용) / `down`(롤백) 쌍으로 작성한다.
2. **무중단**: 컬럼 추가는 NULL 허용 또는 기본값과 함께, 삭제·이름변경은 다단계(확장→이행→축소)로 한다.
3. **표준 준수**: 컬럼명은 표준용어 영문약어명, 타입·길이는 표준도메인(metadata-agent 결과)을 따른다.
4. **동기화**: 변경 시 컬럼정의서·테이블정의서(xlsx)와 기관 메타데이터를 함께 갱신하고, 설계 결정은 `db-decision-records`로 ADR을 남긴다.
5. **개인정보**: 개인정보/민감 컬럼 변경은 영향 범위와 암호화 도메인(예: 암호화번호V256)을 함께 검토한다.

## DBMS 분기 대응표

| 항목 | Oracle 11g | PostgreSQL |
|---|---|---|
| 가변 문자 | `VARCHAR2(n)` | `VARCHAR(n)` |
| 숫자 | `NUMBER(p,s)` | `NUMERIC(p,s)` |
| 날짜시간 | `DATE`, `TIMESTAMP` | `TIMESTAMP` |
| 자동 채번 | `SEQUENCE` + `SEQ.NEXTVAL`(트리거) | `IDENTITY`/`SERIAL`/`SEQUENCE` |
| 페이징 | `ROWNUM` 3중 서브쿼리 | `LIMIT n OFFSET m` |
| DDL 트랜잭션 | DDL 시 암묵 COMMIT(롤백 불가) → 단계 분리 필수 | 트랜잭션 DDL 가능(BEGIN…COMMIT) |
| 식별자 길이 | 30바이트 이내(11g) | 63바이트 이내 |
| 컬럼 추가 | `ALTER TABLE t ADD (c VARCHAR2(n))` | `ALTER TABLE t ADD COLUMN c VARCHAR(n)` |
| 무중단 인덱스 | `CREATE INDEX … ONLINE` | `CREATE INDEX CONCURRENTLY …` |

> Oracle은 DDL이 암묵 커밋되어 단일 트랜잭션 롤백이 어렵다. 따라서 **확장→백필→축소**를 별도 마이그레이션 단계로 분리하고 각 단계의 보상(down) 스크립트를 명시한다.

## 작성 절차

1. 대상 DBMS 확정 → 해당 분기 문법 선택.
2. 변경 유형(추가/변경/삭제/백필)별로 `up`/`down` DDL을 작성한다.
3. 무중단 필요 시 다단계로 쪼갠다(확장→이행→축소).
4. 마이그레이션 파일을 `migrations/`에 순번_설명.sql로 저장한다(실행은 backend-impl 담당, **이 스킬은 작성까지**).
5. 컬럼/테이블정의서·메타데이터 동기화 항목을 체크리스트로 남기고 ADR을 기록한다.

## 산출물

- `migrations/{순번}_{설명}.up.sql`, `migrations/{순번}_{설명}.down.sql` (대상 DBMS 문법)
- 변경 요약 + 동기화 체크리스트(정의서·메타데이터·ADR)

## 경계

- **실 DB에 실행하지 않는다** (DDL 작성까지가 범위).
- 표준 타입/길이를 임의 변경하지 않는다(metadata-agent 결과 준수).
