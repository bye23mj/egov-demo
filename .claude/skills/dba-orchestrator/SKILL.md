---
name: dba-orchestrator
description: 공공DB 데이터베이스관리자(DBA) 파이프라인 오케스트레이터. da-agent 산출물을 받아 인프라 프로비저닝(Docker Oracle/PostgreSQL) → DB 객체 생성(DB·user·테이블스페이스·테이블·인덱스) → 기본 CRUD SQL 제공을 순차 위임으로 조율한다. 대상 DBMS(Oracle/PostgreSQL)로 분기한다. 트리거 - "DB 구축", "DB 생성", "DBA 파이프라인", "DB 프로비저닝/객체생성/CRUD". 후속 작업 - 재실행, 부분 재구축, user/테이블 추가, 인덱스 보강, CRUD 재생성, 이전 결과 개선 요청 시에도 반드시 이 스킬을 사용.
allowed-tools: Read, Write, Grep, Glob, Bash, Skill
---

# DBA Orchestrator (공공DB 구축 파이프라인)

da-agent(설계)의 산출물을 입력으로, 실제 DB를 구축·운영하는 DBA의 3단계를 순차 위임으로 조율한다. 판단 주체·원칙은 `dba-agent` 에이전트가, 절차·조율은 이 스킬이 정의한다.

## 실행 모드: 서브 위임 (순차 파이프라인)

- 각 단계를 `Skill` 도구로 호출하고 산출물(파일·실행로그)로 결과를 수집한다.
- 팀 모드가 아니다 — 프로비저닝→객체생성→CRUD가 순차 의존하므로 **순차 실행 + 게이트**한다.

## 사용 시점

- da-agent 산출물(`docs/04. db-deliverables/{요구사항번호}/`)로 실제 DB를 구축할 때
- "DB 구축/프로비저닝/객체생성/CRUD 생성"을 요청받을 때
- **후속**: 부분 재구축, user/테이블 추가, 인덱스 보강, CRUD 재생성 등

## 스킬 구성

| 단계 | 호출 | skill | 입력 | 출력 |
|---|---|---|---|---|
| 1. 인프라 프로비저닝 | Skill | `db-provisioning` | 대상 DBMS | `docker-compose.db.yml`, 접속정보 |
| 2. DB 객체 생성 | Skill | `db-object-creation` | da-agent 산출물·접속정보 | `ddl/*.sql`, 생성객체 목록 |
| 3. 기본 CRUD 제공 | Skill | `crud-sql-generation` | 컬럼정의서·생성객체 | `sql/{테이블}_crud.sql` |

> 1단계는 ECC `docker-patterns`, 2·3단계는 `postgres-patterns`·`database-migrations`(현지화 `db-migrations`)를 참고 베이스로 한다. ECC 원본은 보존되어 있다.

## 입력 (da-agent 연계)

```text
docs/04. db-deliverables/{요구사항번호}/
├── {요구사항번호}-테이블정의서.xlsx     # 2 객체생성 입력
├── {요구사항번호}-컬럼정의서.xlsx       # 2·3 입력
└── migrations/*.up/.down.sql            # 2 객체생성 우선 활용
```
- **대상 DBMS**: da-agent 모델링의 `대상 DBMS`(Oracle/PostgreSQL). 기본 Oracle 11g. 전 단계에 일관 전달.

## 작업공간 (절대 경로)

```text
docs/05. db-build/{요구사항번호}/
├── docker-compose.db.yml                # 1 프로비저닝
├── .env.example                         # 1 (키만, 값 제외)
├── ddl/{순번}_{객체}.sql (+ drop)        # 2 객체생성
├── build-objects.md                     # 2 생성객체·검증 결과
└── sql/{테이블}_crud.sql                 # 3 CRUD
```
- 비밀번호는 `.env`(미커밋)로 주입. 중간 산출물·실행로그를 보존한다.

## 워크플로우

### Phase 0: 컨텍스트 확인
`docs/05. db-build/{요구사항번호}/` 존재 여부로 분기.
- **미존재** → 초기 구축. Phase 1.
- **존재 + 부분 요청** → 부분 재구축(해당 단계만, 하위 의존 재검증).
- **존재 + 새 입력** → 기존 폴더 보관 이동 후 Phase 1.

### Phase 1~3: 단계 위임 (게이트)
1. **프로비저닝**: `db-provisioning` → 컨테이너 기동·healthcheck 통과 확인. **미통과 시 2단계 보류**(게이트).
2. **객체 생성**: `db-object-creation` → 의존 순서대로 DDL 실행, 컬럼정의서와 대조 검증. **불일치/오류 시 3단계 보류**(게이트), da-agent 산출물로 환류.
3. **CRUD 제공**: `crud-sql-generation` → 테이블별 CRUD SQL(+선택 Mapper) 생성.

### Phase 4: 정리
1. 생성 객체·CRUD 산출물 목록을 취합한다.
2. 오류/미결 0건 확인(남으면 명시).
3. 작업공간 보존, 접속 정보(비밀번호 제외)·다음 액션을 보고한다.

## 데이터 흐름

```text
da-agent 산출물(테이블/컬럼정의서·migrations)
        │
   Skill─ db-provisioning ─→ docker compose (Oracle|PostgreSQL) [healthcheck 게이트]
        │
   Skill─ db-object-creation ─→ ddl/ 실행 → 생성객체 (정의서 대조 게이트)
        │
   Skill─ crud-sql-generation ─→ sql/{테이블}_crud.sql
        ↓
   [DBA: Phase 4 취합·보고]
```

## 에러 핸들링

| 상황 | 전략 |
|---|---|
| 컨테이너 기동/healthcheck 실패 | 로그 확인·1회 재기동. 재실패 시 2단계 보류·원인 보고 |
| da-agent 산출물 부재 | 중단, 산출물 경로 요청(추측 DDL 금지) |
| DDL 실행 오류 | 해당 객체 drop 후 재실행 1회. 재실패 시 정의서 대조·환류, 후속 보류 |
| 정의서 ↔ 생성객체 불일치 | 불일치 명시, da-agent로 환류 후 재실행 |
| 대상 DBMS 불명확 | 기본 Oracle 11g 가정·명시, 필요 시 사용자 확인 |
| 비밀번호 미설정 | `.env` 키 요청, 하드코딩 금지 |

## 테스트 시나리오

### 정상 흐름
1. `docs/04. db-deliverables/FR-019/`(대상 DBMS: Oracle) 산출물 존재.
2. Phase 0: 작업공간 미존재 → 초기 구축.
3. 1 프로비저닝(healthcheck 통과) → 2 객체생성(정의서 일치) → 3 CRUD 생성.
4. Phase 4: 생성 객체·CRUD 산출물 보고, 오류 0건.

### 에러 흐름
1. 2단계에서 FK 참조 테이블 미생성으로 DDL 오류.
2. 게이트 작동 → 생성 순서(부모→자식) 재정렬 후 재실행.
3. 정의서 일치 확인 → 3단계 진행, Phase 4에서 "생성순서 정정" 명시.

## 경계

- 운영 DB·클라우드에 무단 실행하지 않는다(로컬/개발 컨테이너 대상).
- 표준 타입/길이를 임의 변경하지 않는다(컬럼정의서·표준도메인 준수).
- 비밀번호 하드코딩·커밋 금지(환경변수).
- 데이터 볼륨을 임의 삭제하지 않는다.
- 중간 산출물을 삭제하지 않는다(감사 추적 보존).
