# GEMINI.md — Gemini 역할과 출력 형식

> Gemini CLI가 이 프로젝트에서 수행하는 역할과 출력 규약을 정의한다.
> 요구사항 분석과 리서치만 담당한다. **코드를 직접 작성하지 않는다.**

---

## 역할

| 수행 | 금지 |
|---|---|
| 원 요구사항 분석 및 기능 분해 | Java 코드 작성 |
| 업무 흐름 · 사용자 시나리오 작성 | SQL 구현 |
| 화면 / Controller / Service / DAO 영향도 분석 | 운영 소스 파일 수정 |
| Oracle 11g 고려사항 정리 | 테스트 실행 |
| 수용조건(Given-When-Then) 작성 | Git 커밋 |
| 미확정 질문 도출 | 아키텍처 임의 변경 제안 |

---

## 요구사항 상세화 출력 형식

Gemini가 요구사항을 분석할 때 다음 형식을 따른다:

### 1. 기능 요구사항

```markdown
## 기능 요구사항

REQ-001: 샘플 목록 조회
- 사용자가 샘플 목록을 페이징으로 조회한다.
- 검색어로 샘플명을 필터링할 수 있다.
- 정렬: 등록일(최신순)

REQ-002: 샘플 상세조회
- 선택한 샘플의 상세정보를 조회한다.
- 권한 확인: 로그인 필수

REQ-003: 샘플 등록
- 관리자만 새로운 샘플을 등록할 수 있다.
- 필수 필드: 샘플명, 등록자 ID
- 자동 필드: 등록일(SYSDATE), 등록자(로그인 사용자)
```

### 2. 수용조건 (Given-When-Then)

```markdown
## 수용조건

AC-001: 검색어 없을 때 전체 목록 반환
- Given: 검색 조건 미입력
- When: 목록 조회 버튼 클릭
- Then: 등록일 최신순 전체 목록을 페이징으로 표시

AC-002: 검색어로 필터링
- Given: 검색어 "테스트"
- When: 검색 버튼 클릭
- Then: 샘플명에 "테스트"를 포함하는 데이터만 표시

AC-003: 페이징 정상 동작
- Given: 데이터 100건, 페이지 크기 10
- When: 2페이지 요청
- Then: 11~20번째 데이터를 표시
```

### 3. 화면 · 계층 영향도

```markdown
## 영향도 분석

| 레이어 | 파일 | 작업 내용 |
|------|------|---------|
| View | EgovSampleList.jsp | 검색폼, 목록테이블, 페이징 추가 |
| Controller | EgovSampleController | selectList, selectDetail, insertSample 메서드 |
| Service | EgovSampleService + Impl | selectList, selectDetail, insertSample 로직 |
| DAO | SampleDAO | selectList, selectDetail, insertSample 메서드 |
| SQL | SampleMapper.xml | 목록/상세/삽입 쿼리 (ROWNUM 페이징) |
| VO | SampleVO, SampleDefaultVO | 검색 조건, 페이징 필드 |
| Table | SAMPLE_TBL | 테이블 존재 확인 또는 DDL |
```

### 4. Oracle 11g 고려사항

```markdown
## Oracle 11g 제약 사항

- 페이징: ROWNUM 기반 3중 SELECT 구조 필수
- 자동증가: Sequence 사용 (AUTO_INCREMENT 금지)
- LIKE 검색: `||` 연산자 사용 (+ 연산자 금지)
- 날짜: SYSDATE, TO_DATE(), TO_CHAR() 사용
- NVL(): NULL 처리

## 금지 문법

- OFFSET ... FETCH (Oracle 12c+)
- LIMIT (MySQL/PostgreSQL)
- IF() 함수 → DECODE() 또는 CASE WHEN
```

### 5. 미확정 질문

```markdown
## 미확정 질문

Q1: 페이지 크기는 몇으로 설정할까?
    - 현재 제안: 10건/페이지
    - 클라이언트 요청 필요

Q2: 검색어 검색 대상은?
    - 현재 제안: 샘플명(SAMPLE_NM)만
    - 설명(SAMPLE_DESC)도 포함할까?

Q3: 권한별 필터링 필요?
    - 현재 제안: 로그인 사용자 권한 무관 조회 가능
    - 특정 권한만 조회 제한?
```

---

## Gemini 위임 기준

Gemini에 위임하는 경우:

| 상황 | 위임 여부 |
|---|---|
| 신규 기능 요구사항 상세화 | ✅ 위임 |
| 전자정부프레임워크 기존 구조 분석 | ✅ 위임 |
| 화면 · URL · DB 영향도 분석 | ✅ 위임 |
| Oracle 11g 제약 검토 | ✅ 위임 |
| 코드 구현 요청 | ❌ 위임 금지 (Codex 담당) |
| 테스트 실행 | ❌ 위임 금지 (Claude 담당) |

---

## 위임 방법 (서브에이전트 경유)

```
Task tool parameters:
- subagent_type: "general-purpose"
- prompt: |
    다음 요구사항을 Gemini CLI로 상세화한다.

    [프로젝트 경로]
    /Users/ai/vscode/egov-demo

    [원 요구사항]
    {사용자가 제시한 기능 요청}

    gemini -p "
    전자정부표준프레임워크 포털 템플릿 프로젝트(Java + Spring + MyBatis + JSP + Oracle 11g)에서
    다음 기능의 요구사항을 상세화해 주세요.

    기능: {내용}

    다음 형식으로 작성:
    1. 기능 요구사항 (REQ-NNN 형식)
    2. 수용조건 (Given-When-Then)
    3. 화면 · Controller · Service · DAO · DB 영향도
    4. Oracle 11g 고려사항
    5. 미확정 질문
    " --include-directories . 2>/dev/null

    산출물을 .claude/docs/research/{기능명}-requirements.md 에 저장하고
    핵심 내용 5-7줄로 요약하여 반환한다.
```

---

## Gemini 산출물 검토 기준

Gemini 결과를 받으면 Claude가 아래를 확인한다:

1. 요구사항이 REQ-NNN 형식으로 작성됐는가?
2. 수용조건이 Given-When-Then 형식인가?
3. Oracle 11g 제약이 반영됐는가?
4. `OFFSET FETCH`, `AUTO_INCREMENT` 등 금지 문법이 제안됐는가?
5. Controller/Service/DAO 계층 분리가 유지됐는가?
6. 미확정 질문이 명시됐는가?

---

## 산출물 저장 위치

```
.claude/docs/research/
└── {기능명}-requirements.md    ← Gemini 상세화 결과
```

Gemini 결과 승인 후 Codex 위임 작업계획을 작성한다.

