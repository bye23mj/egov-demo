# Claude + Jira + Confluence + Slack 기반 Speckit SDD 자동화 워크플로우 기술검토 및 요구사항

## 1. 개요

본 문서는 **Claude + Jira + Confluence + Slack**을 이용하여 프로젝트 문서를 기반으로 **Spec Kit SDD(Spec-Driven Development)** 워크플로우를 자동화하는 방안을 정리한 기술검토 및 요구사항 문서이다.

목표는 Jira Kanban 프로젝트에서 특정 상태, 예를 들어 `내부검토` 상태의 문서를 가져와 Claude/Speckit으로 요구사항을 체계화하고, 생성된 SDD 산출물을 Jira와 Confluence에 동기화한 뒤, 보완된 문서를 다시 Claude로 불러와 계획 수립과 작업 분해까지 자동화하는 것이다.

전체 흐름은 다음과 같다.

```text
Jira Kanban 상태
→ 해당 상태의 문서 수집
→ Claude/Speckit으로 SDD 산출물 생성
→ Jira/Confluence에 결과 등록
→ 담당자가 문서 보완
→ 다시 Claude/Speckit으로 Plan/Task/TDD 생성
```

---

## 2. 핵심 전제

`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`는 일반적으로 **Claude Code 또는 지원되는 AI 코딩 에이전트 작업공간 안에서 실행되는 명령**이다.


```text
Confluence 폴조구조를 파악하여 /Users/ai/vscode/egov-demo/docs/00. confluence 하위로 폴더 생성하여 복사
→ specify init 실행
→ Jira/Confluence 문서를 Markdown으로 배치
→ Claude Code + Spec Kit 명령 실행
→ 생성된 Markdown 산출물 수집
→ Jira/Confluence/Slack에 동기화
```
**Claude Code + Spec Kit Workspace 자동 실행** 방식이 적합.

---

## 3. 자동화 대상 문서

Jira 또는 Confluence에 등록된 다음 문서를 대상으로 한다.

| 문서 | 역할 |
|---|---|
| 요구사항정의서 | 기능/비기능/보안/연계 요구사항 원천 |
| 유스케이스정의서 | 사용자 시나리오, 기본 흐름, 대안 흐름 |
| 컴포넌트정의서 또는 화면정의서 | 화면, 컴포넌트, API, UI 흐름 |
| 테스트케이스정의서 | 검증 조건, 예상 결과, 예외 케이스 |

---

## 4. 최종 생성 산출물

자동화 결과로 다음 Markdown 파일을 생성 또는 갱신한다.

```text
requirements.md
spec.md
edge_cases.md
clarification_questions.md
plan.md
component_spec.md
data_model.md
TDD.md
tasks.md
```

사용자가 언급한 `/speckit.task`는 Spec Kit 기준으로는 일반적으로 **`/speckit.tasks`** 명령을 의미한다.

---

## 5. 전체 워크플로우

```text
1. 클로드에서 confluence-sync 실행 시 상태값을 입력하여 Jira Kanban에서 대상 상태 선택
   예: 내부검토

2. 해당 상태의 문서 이슈 조회

3. Confluence 폴조구조를 파악하여 /Users/ai/vscode/egov-demo/docs/00. confluence 하위로 폴더 생성하여 등록 문서 수집
   - 요구사항정의서
   - 유스케이스정의서
   - 컴포넌트정의서 또는 화면정의서
   - 테스트케이스정의서

4. 문서를 Markdown으로 정규화

5. Claude Code + Spec Kit Workspace 생성

6. /speckit.specify 실행

7. 생성된 requirements.md, spec.md를 Jira 동기화된 요구사항정의서 이슈 댓글로 등록

8. spec.md에서 Edge Case 질문을 추출하여 별도 댓글 또는 Jira Sub-task로 등록

9. 사용자가 Jira/Confluence에서 요구사항정의서 보완

10. 보완 문서를 다시 수집

11. /speckit.plan 실행

12. 생성된 plan.md 및 관련 문서를 Jira/Confluence에 등록

13. component_spec.md, data_model.md, TDD.md 생성 또는 수정

14. 다시 Claude Workspace로 불러와 /speckit.tasks 실행

15. tasks.md를 Jira Task/Sub-task로 변환

16. Slack으로 담당자에게 알림
```

---

## 6. 권장 시스템 아키텍처

```text
[Jira Kanban]
   ↓ 상태 기반 조회
[Workflow Orchestrator]
   ↓
[Document Collector]
   ├─ Jira Attachment Reader
   ├─ Confluence Page Reader
   └─ Confluence Attachment Reader
   ↓
[Markdown Converter]
   ├─ HWPX → Markdown
   ├─ DOCX → Markdown
   ├─ XLSX → Markdown
   └─ PPTX → Markdown
   ↓
[Speckit Workspace Manager]
   ├─ specify init
   ├─ input docs 구성
   ├─ /speckit.specify 실행
   ├─ /speckit.plan 실행
   └─ /speckit.tasks 실행
   ↓
[Artifact Sync Manager]
   ├─ Jira 댓글 등록
   ├─ Jira 첨부파일 등록
   ├─ Confluence 페이지 갱신
   └─ Slack 알림
```

---

## 7. 주요 모듈

| 모듈 | 역할 |
|---|---|
| Jira Sync Module | Kanban 상태 조회, 이슈 조회, 댓글 등록, 첨부 등록, 상태 변경 |
| Confluence Sync Module | 페이지 조회, 산출물 본문 조회, 첨부파일 다운로드, 결과 페이지 갱신 |
| Document Normalizer | HWPX/DOCX/XLSX/PPTX/Confluence Page를 Markdown으로 변환 |
| Speckit Runner | Claude Code 작업공간 생성, `/speckit.*` 명령 실행 |
| Artifact Parser | 생성된 `spec.md`, `plan.md`, `tasks.md` 파싱 |
| Edge Case Extractor | `spec.md`에서 불명확 항목과 질문 추출 |
| Jira Comment Publisher | 결과 문서를 Jira 댓글 또는 첨부파일로 등록 |
| Slack Notifier | 담당자에게 검토/보완 요청 메시지 발송 |
| Audit Logger | 실행 이력, 입력 문서 버전, 생성 파일 버전 저장 |

---

# 8. 단계별 요구사항 및 기술검토

## 8.1 단계 1. Jira Kanban 상태 기반 문서 조회

### 목적

사용자가 지정한 Jira Kanban 상태, 예를 들어 `내부검토`, `요구사항보완`, `설계검토`에 해당하는 문서 이슈를 조회한다.

### 입력

```text
projectKey = GOVPJT
targetStatus = 내부검토
documentTypes = 요구사항정의서, 유스케이스정의서, 컴포넌트정의서, 테스트케이스정의서
```

### JQL 예시

```jql
project = GOVPJT
AND status = "내부검토"
AND issuetype = Deliverable
AND "Document Type" in ("요구사항정의서", "유스케이스정의서", "컴포넌트정의서", "테스트케이스정의서")
ORDER BY updated DESC
```

### 출력 예시

```json
{
  "issueKey": "GOVPJT-101",
  "documentType": "요구사항정의서",
  "status": "내부검토",
  "confluencePageUrl": "...",
  "attachments": ["요구사항정의서_v0.3.hwpx"]
}
```

### 기술검토

가능하다. Jira REST API를 통해 JQL 기반 이슈 검색, 이슈 필드 조회, 첨부파일 메타데이터 조회가 가능하다.

---

## 8.2 단계 2. 등록 문서 수집

### 수집 위치

문서는 세 곳에서 가져올 수 있어야 한다.

```text
1. Jira Issue Attachment
2. Jira Custom Field의 Confluence Page URL
3. Confluence Page Attachment
```

### 요구사항

```text
REQ-DOC-001: 클로드는 Jira 이슈의 첨부파일을 조회할 수 있어야 한다.
REQ-DOC-002: 클로드는 Confluence Page URL을 통해 본문을 조회할 수 있어야 한다.
REQ-DOC-003: 클로드는 Confluence Page의 첨부파일을 다운로드할 수 있어야 한다.
REQ-DOC-004: 클로드는 문서 유형별 필수 문서가 누락된 경우 Jira 댓글과 Slack으로 알림을 발송해야 한다.
```

---

## 8.3 단계 3. Markdown 정규화

### 목적

Claude/Speckit이 안정적으로 이해할 수 있도록 입력 문서를 Markdown으로 변환한다.

### 변환 대상

```text
.hwpx
.docx
.xlsx
.pptx
.pdf 선택
Confluence Page HTML/Storage Format
```

### 출력 구조

```text
workspace/
├─ input/
│  ├─ 01_requirement_definition.md
│  ├─ 02_usecase_definition.md
│  ├─ 03_component_or_screen_definition.md
│  └─ 04_testcase_definition.md
└─ source-metadata.json
```

### source-metadata.json 예시

```json
{
  "projectKey": "GOVPJT",
  "targetStatus": "내부검토",
  "sourceIssues": [
    {
      "issueKey": "GOVPJT-101",
      "documentType": "요구사항정의서",
      "version": "v0.3",
      "updatedAt": "2026-06-11T10:00:00+09:00"
    }
  ]
}
```

### 기술검토

필수 단계이다. Speckit은 파일 기반 워크플로우와 잘 맞기 때문에, Jira/Confluence의 문서를 직접 프롬프트에 붙이는 방식보다 **입력 Markdown 파일로 정규화**하는 방식이 추적성과 재현성이 좋다.

---

## 8.4 단계 4. Claude Speckit Workspace 생성

### 목적

문서 단위로 임시 작업공간을 만들고 Spec Kit 명령을 실행할 준비를 한다.

### 권장 Workspace 구조

```text
speckit-workspaces/
└─ GOVPJT-REQ-001/
   ├─ .specify/
   ├─ specs/
   ├─ input/
   │  ├─ 01_requirement_definition.md
   │  ├─ 02_usecase_definition.md
   │  ├─ 03_component_or_screen_definition.md
   │  └─ 04_testcase_definition.md
   ├─ output/
   └─ source-metadata.json
```

### 초기화 예시

```bash
specify init . --integration claude
```

또는 Codex/Claude Code 환경에 맞게 integration을 지정한다.

### 기술검토

가능하다. 단, 서버에서 Claude Code CLI를 자동 실행하려면 실행 환경, 인증, 네트워크, 작업 디렉터리 격리, 로그 저장 정책이 필요하다. 운영 서버에서 직접 Claude Code를 실행하기 부담스럽다면 별도 **AI Worker 서버** 또는 **컨테이너 기반 작업 실행기**를 두는 것이 좋다.

---

## 8.5 단계 5. `/speckit.specify` 실행

### 목적

등록 문서를 바탕으로 요구사항을 구조화하고, `requirements.md`, `spec.md`를 생성한다.

### 입력 프롬프트 예시

```text
/speckit.specify

다음 입력 문서를 기반으로 전자정부프레임워크 프로젝트용 요구사항 명세를 체계화한다.

입력 문서:
- input/01_requirement_definition.md
- input/02_usecase_definition.md
- input/03_component_or_screen_definition.md
- input/04_testcase_definition.md

생성 목표:
1. requirements.md 생성
2. spec.md 생성
3. 요구사항 ID를 유지하거나 누락 시 새로 부여
4. 기능 요구사항, 비기능 요구사항, 보안 요구사항, 연계 요구사항 분리
5. 유스케이스와 테스트케이스 간 추적성 생성
6. 모호한 요구사항은 Edge Case 또는 Clarification Question으로 분리
```

### 생성 파일

```text
requirements.md
spec.md
edge_cases.md
clarification_questions.md
```

### 요구사항

```text
REQ-SPEC-001: 시스템은 입력 문서 기반으로 requirements.md를 생성해야 한다.
REQ-SPEC-002: 시스템은 입력 문서 기반으로 spec.md를 생성해야 한다.
REQ-SPEC-003: 시스템은 요구사항 ID, 유스케이스 ID, 테스트케이스 ID 간 연결을 유지해야 한다.
REQ-SPEC-004: 시스템은 모호하거나 누락된 요구사항을 별도 질문 목록으로 분리해야 한다.
```

---

## 8.6 단계 6. Jira 요구사항정의서에 댓글 등록

### 목적

생성된 `requirements.md`, `spec.md`를 Jira의 요구사항정의서 이슈 댓글로 등록한다.

### 등록 방식

두 가지 방식을 병행하는 것이 좋다.

| 방식 | 설명 |
|---|---|
| Jira 댓글 | 요약, 핵심 변경사항, 링크 등록 |
| Jira 첨부파일 | `requirements.md`, `spec.md` 원본 첨부 |
| Confluence Page | 긴 본문은 Confluence에 페이지로 등록하고 Jira 댓글에는 링크만 등록 |

### Jira 댓글 예시

```text
[Claude Speckit 요구사항 체계화 결과]

대상 상태: 내부검토
입력 문서:
- 요구사항정의서 v0.3
- 유스케이스정의서 v0.2
- 화면정의서 v0.4
- 테스트케이스정의서 v0.1

생성 산출물:
- requirements.md
- spec.md
- edge_cases.md

주요 결과:
- 기능 요구사항 34건
- 비기능 요구사항 8건
- 보안 요구사항 5건
- 테스트케이스 연결 29건
- 확인 필요 Edge Case 12건
```

### 기술검토

Jira 댓글 등록은 가능하다. 다만 긴 Markdown을 댓글에 그대로 등록하면 가독성이 떨어진다. 따라서 Jira 댓글에는 요약과 Confluence 링크를 넣고, Markdown 원문은 Jira 첨부파일 또는 Confluence 페이지로 관리하는 것이 좋다.

---

## 8.7 단계 7. Edge Case 질문 별도 등록

### 목적

`spec.md` 또는 `clarification_questions.md`에서 확인 필요 사항을 추출해 별도로 등록한다.

### 등록 방식 추천

| 방식 | 추천도 | 설명 |
|---|---:|---|
| Jira Sub-task 생성 | 높음 | 담당자 배정, 기한, 상태 관리 가능 |
| Jira 댓글 등록 | 보통 | 간단하지만 추적성 약함 |
| Confluence 검토 질문 페이지 생성 | 높음 | 고객/PM 검토 회의에 적합 |
| Slack 알림 | 높음 | 빠른 응답 유도 |

### Edge Case Jira Sub-task 예시

```text
Issue Type: Sub-task
Parent: GOVPJT-101
Summary: [Edge Case 확인] 중복 신청 시 처리 정책 확인
Description:
- 관련 요구사항: REQ-FN-007
- 관련 유스케이스: UC-003
- 질문: 동일 사용자가 같은 민원을 같은 날 중복 신청할 수 있는가?
- 선택지:
  1. 허용
  2. 차단
  3. 경고 후 허용
- Claude 제안: 차단 또는 경고 후 허용 정책 필요
Assignee: 업무담당자
Due Date: 2026-06-14
```

### 요구사항

```text
REQ-EDGE-001: 시스템은 spec.md에서 Edge Case 질문을 추출해야 한다.
REQ-EDGE-002: 시스템은 각 질문에 관련 요구사항 ID를 연결해야 한다.
REQ-EDGE-003: 시스템은 Edge Case 질문을 Jira Sub-task 또는 댓글로 등록해야 한다.
REQ-EDGE-004: 시스템은 Slack으로 담당자에게 확인 요청을 발송해야 한다.
```

---

## 8.8 단계 8. Jira/Confluence 기반 요구사항 보완

### 목적

담당자가 Edge Case 질문과 Claude 결과를 기반으로 요구사항정의서를 보완한다.

### 사용자 작업

```text
1. Jira 댓글 확인
2. Edge Case Sub-task 확인
3. Confluence 요구사항정의서 수정
4. Page Properties 상태 변경
   내부검토 → 보완완료
5. Jira 상태 변경
   내부검토 → 요구사항보완완료
```

### 자동화 조건

보완 완료 상태가 되면 다음 단계가 자동 실행된다.

```jql
project = GOVPJT
AND status = "요구사항보완완료"
AND issuetype = Deliverable
AND "Document Type" = "요구사항정의서"
```

---

## 8.9 단계 9. `/speckit.plan` 실행

### 목적

보완된 요구사항을 바탕으로 기술 구현 계획을 수립한다.

### 입력 문서

```text
requirements.md
spec.md
보완된 요구사항정의서.md
유스케이스정의서.md
컴포넌트정의서.md
테스트케이스정의서.md
```

### 입력 프롬프트 예시

```text
/speckit.plan

다음 문서를 기반으로 전자정부프레임워크 기반 구현 계획을 수립한다.

기술 기준:
- Java 17
- Spring Boot 또는 전자정부프레임워크
- Controller-Service-Mapper 구조
- MyBatis
- PostgreSQL 또는 Oracle
- JUnit5
- Mockito
- MockMvc
- 통합 테스트 포함
- 요구사항 ID와 테스트케이스 ID 추적성 유지

생성 대상:
- plan.md
- component_spec.md
- data_model.md
- TDD.md
```

### 생성 파일

```text
plan.md
component_spec.md
data_model.md
TDD.md
contracts/api-spec.md 또는 openapi.yaml
```

---

## 8.10 단계 10. Plan 결과 Jira/Confluence 등록

### 목적

생성된 계획 문서를 Jira와 Confluence에 등록한다.

### 등록 대상

| 생성 파일 | 등록 위치 |
|---|---|
| `plan.md` | Jira 댓글 + Confluence 설계계획 페이지 |
| `component_spec.md` | Confluence 컴포넌트정의서 또는 화면정의서 |
| `data_model.md` | Confluence 데이터모델 문서 |
| `TDD.md` | Confluence 테스트전략 또는 테스트케이스정의서 |
| `openapi.yaml` | API설계서 첨부 또는 Git 저장소 |

### 요구사항

```text
REQ-PLAN-001: 시스템은 plan.md를 Jira 댓글 또는 첨부파일로 등록해야 한다.
REQ-PLAN-002: 시스템은 component_spec.md를 Confluence 컴포넌트정의서에 반영해야 한다.
REQ-PLAN-003: 시스템은 data_model.md를 데이터모델 문서에 반영해야 한다.
REQ-PLAN-004: 시스템은 TDD.md를 테스트케이스정의서 또는 테스트전략 문서에 반영해야 한다.
```

---

## 8.11 단계 11. component_spec.md, data_model.md, TDD.md 생성/수정

### component_spec.md 구성

```markdown
# Component Specification

## 1. 개요

## 2. 관련 요구사항

| 요구사항 ID | 설명 | 관련 유스케이스 |
|---|---|---|

## 3. 컴포넌트 목록

| Component ID | Component Name | 역할 | 관련 화면 | 관련 API |
|---|---|---|---|---|

## 4. Controller 설계

## 5. Service 설계

## 6. Mapper/Repository 설계

## 7. DTO 설계

## 8. 예외 처리

## 9. 권한/보안

## 10. 추적성
```

### data_model.md 구성

```markdown
# Data Model

## 1. ERD 개요

## 2. 테이블 목록

| Table ID | Table Name | 설명 | 관련 요구사항 |
|---|---|---|---|

## 3. 테이블 상세

## 4. 관계 정의

## 5. 인덱스

## 6. 이력/감사 컬럼

## 7. 개인정보/암호화 대상

## 8. 테스트 데이터
```

### TDD.md 구성

```markdown
# TDD Strategy

## 1. 테스트 원칙

## 2. 요구사항별 테스트 매핑

| 요구사항 ID | 테스트케이스 ID | 테스트 유형 | 예상 결과 |
|---|---|---|---|

## 3. Controller Test

## 4. Service Unit Test

## 5. Mapper Integration Test

## 6. API Integration Test

## 7. Edge Case Test

## 8. 테스트 우선순위
```

---

## 8.12 단계 12. `/speckit.tasks` 실행

### 목적

구현 가능한 작업 단위로 분해한다.

### 입력 파일

```text
spec.md
plan.md
component_spec.md
data_model.md
TDD.md
```

### 명령

```text
/speckit.tasks
```

### 생성 결과

```text
tasks.md
```

### tasks.md 예시

```markdown
# Tasks

## Story 1: 민원 신청서 작성

- [ ] T001 REQ-FN-001 Controller 테스트 작성
- [ ] T002 REQ-FN-001 Service 테스트 작성
- [ ] T003 REQ-FN-001 Mapper 테스트 작성
- [ ] T004 Request/Response DTO 작성
- [ ] T005 Controller 구현
- [ ] T006 Service 구현
- [ ] T007 Mapper XML 작성
- [ ] T008 예외 처리 구현
- [ ] T009 API 통합 테스트 작성
- [ ] T010 Confluence API설계서 갱신
```

### Jira 변환

`tasks.md`를 Jira Task/Sub-task로 변환한다.

| tasks.md | Jira |
|---|---|
| Story 1 | Jira Story |
| T001~T010 | Jira Sub-task |
| 요구사항 ID | Custom Field |
| 테스트케이스 ID | Custom Field |
| 파일 경로 | Description |
| 담당자 | Component/Rule 기반 자동 배정 |

---

# 9. 권장 Jira 상태 설계

## 9.1 방식 A. Kanban Status에 Claude 단계 포함

```text
문서작성대기
→ 문서작성중
→ 내부검토
→ Claude_Specify
→ 요구사항보완
→ 보완완료
→ Claude_Plan
→ 설계보완
→ Claude_Tasks
→ 개발대기
→ 개발중
→ 테스트중
→ 완료
```

### 장점

```text
보드에서 전체 흐름이 눈에 보인다.
```

### 단점

```text
상태가 너무 많아져 보드 운영이 복잡해질 수 있다.
```

## 9.2 방식 B. Kanban Status는 단순화하고 Claude 상태는 Custom Field로 관리

```text
Jira Status: 내부검토

Claude SDD Status:
- READY_TO_SPECIFY
- SPECIFY_RUNNING
- SPECIFY_DONE
- NEEDS_CLARIFICATION
- PLAN_RUNNING
- PLAN_DONE
- TASKS_RUNNING
- TASKS_DONE
```

### 추천

실무적으로는 **방식 B**가 더 안정적이다. Kanban 상태가 너무 많아지면 PM/팀원이 보드에서 흐름을 파악하기 어려워진다. Jira 상태는 업무 중심으로 단순히 두고, Claude 자동화 진행상태는 Custom Field로 관리하는 것이 좋다.

---

# 10. Jira Custom Field 요구사항

아래 필드를 추가하는 것을 권장한다.

| 필드명 | 타입 | 예시 |
|---|---|---|
| Document Type | Select | 요구사항정의서 |
| Document Phase | Select | 요구사항 |
| Claude SDD Status | Select | SPECIFY_DONE |
| Speckit Workspace ID | Text | GOVPJT-REQ-001 |
| Generated Requirements URL | URL | Confluence 링크 |
| Generated Spec URL | URL | Confluence 링크 |
| Generated Plan URL | URL | Confluence 링크 |
| Edge Case Count | Number | 12 |
| Requirement Count | Number | 34 |
| Test Case Count | Number | 29 |
| Last Claude Run At | DateTime | 2026-06-11 14:00 |
| Claude Run Result | Select | SUCCESS/FAILED |
| Source Document Version | Text | req-v0.3 |
| Baseline Version | Text | v0.2 |

---

# 11. Confluence 문서 구조

```text
프로젝트 Space
├─ 02_요구사항
│  ├─ 요구사항정의서
│  ├─ 유스케이스정의서
│  ├─ 요구사항추적표
│  └─ Claude_Specify_Result
│     ├─ requirements.md
│     ├─ spec.md
│     └─ edge_cases.md
│
├─ 04_설계
│  ├─ 컴포넌트정의서
│  ├─ 화면정의서
│  ├─ 데이터모델정의서
│  └─ Claude_Plan_Result
│     ├─ plan.md
│     ├─ component_spec.md
│     └─ data_model.md
│
├─ 06_테스트
│  ├─ 테스트케이스정의서
│  └─ TDD.md
│
└─ 99_AI_Context
   ├─ specify
   ├─ plan
   └─ tasks
```

긴 Markdown은 Jira 댓글에 모두 넣기보다 Confluence 페이지로 저장하고, Jira에는 요약과 링크를 넣는 방식이 좋다.

---

# 12. Slack 알림 흐름

## 12.1 Specify 완료 알림

```text
[Claude SDD] 요구사항 체계화 완료

프로젝트: GOVPJT
대상 상태: 내부검토
대상 문서: 요구사항정의서, 유스케이스정의서, 컴포넌트정의서, 테스트케이스정의서

생성 결과:
- requirements.md
- spec.md
- edge_cases.md

확인 필요 Edge Case: 12건
Jira: GOVPJT-101
Confluence: Claude_Specify_Result
```

## 12.2 보완 요청 알림

```text
[요구사항 보완 요청]

GOVPJT-101 요구사항정의서에 Claude가 확인 질문을 등록했습니다.

확인 필요:
- 중복 신청 처리 정책
- 관리자 승인 조건
- 첨부파일 용량 제한
- 개인정보 마스킹 기준

기한: 2026-06-14
```

---

# 13. 기술 검토 결과

## 13.1 구현 가능 여부

| 항목 | 가능 여부 | 비고 |
|---|---:|---|
| Jira Kanban 상태 기반 문서 조회 | 가능 | JQL + REST API |
| Jira 첨부파일 다운로드 | 가능 | Attachment API |
| Confluence Page/Attachment 조회 | 가능 | Confluence REST API |
| 문서 Markdown 변환 | 가능 | 별도 변환 모듈 필요 |
| Claude/Speckit 명령 실행 | 가능 | Claude Code/AI Worker 방식 권장 |
| requirements.md/spec.md 생성 | 가능 | Speckit specify |
| Jira 댓글 등록 | 가능 | ADF 변환 필요 가능성 있음 |
| Edge Case 질문 분리 | 가능 | 파서/프롬프트 규칙 필요 |
| Plan 생성 | 가능 | Speckit plan |
| component/data/TDD 문서 생성 | 가능 | plan 결과 후 후처리 |
| tasks.md 생성 | 가능 | `/speckit.tasks` |
| tasks.md → Jira Task 생성 | 가능 | 파서 필요 |
| Slack 알림 | 가능 | Slack Bot Token 필요 |

## 13.2 핵심 기술 이슈

| 이슈 | 설명 | 대응 |
|---|---|---|
| Claude Project 직접 자동화 | 웹 UI 직접 자동화는 불안정 | Claude Code CLI/Worker 방식 권장 |
| Jira 댓글 길이 제한 | 긴 Markdown 댓글은 부적합 | Confluence 저장 + Jira 링크 |
| Jira ADF 형식 | 댓글에 ADF 필요 가능성 | Markdown → ADF 변환기 구현 |
| 문서 버전 추적 | 입력 문서가 바뀌면 재현성 문제 | source-metadata.json 저장 |
| Edge Case 추출 품질 | LLM 출력이 흔들릴 수 있음 | 출력 JSON Schema 강제 |
| 요구사항 ID 유지 | ID가 바뀌면 추적성 붕괴 | 기존 ID 우선 유지 규칙 |
| 파일 충돌 | 여러 번 실행 시 결과 덮어쓰기 | Run ID, baseline version 사용 |
| 보안 | 문서에 개인정보 포함 가능 | 마스킹/접근권한/로그 제한 |

---

# 14. 필수 기능 요구사항

## 14.1 Jira 연동 요구사항

```text
JIRA-001: 시스템은 Jira 프로젝트 키와 Kanban 상태를 입력받아 대상 이슈를 조회해야 한다.
JIRA-002: 시스템은 문서 유형별 이슈를 필터링해야 한다.
JIRA-003: 시스템은 Jira 이슈의 첨부파일을 다운로드할 수 있어야 한다.
JIRA-004: 시스템은 Jira 이슈 댓글을 등록할 수 있어야 한다.
JIRA-005: 시스템은 생성된 Markdown 파일을 Jira 이슈에 첨부할 수 있어야 한다.
JIRA-006: 시스템은 Edge Case 질문을 Jira Sub-task로 생성할 수 있어야 한다.
JIRA-007: 시스템은 tasks.md 항목을 Jira Task/Sub-task로 변환할 수 있어야 한다.
JIRA-008: 시스템은 Claude SDD Status 필드를 갱신해야 한다.
```

## 14.2 Confluence 연동 요구사항

```text
CONF-001: 시스템은 Confluence Page URL을 기반으로 본문을 조회해야 한다.
CONF-002: 시스템은 Page Attachment를 다운로드해야 한다.
CONF-003: 시스템은 생성된 Markdown 파일을 Confluence Page로 등록해야 한다.
CONF-004: 시스템은 기존 산출물 페이지를 갱신하거나 새 버전으로 저장해야 한다.
CONF-005: 시스템은 99_AI_Context 하위에 실행 결과를 저장해야 한다.
CONF-006: 시스템은 요구사항/설계/테스트 산출물 간 링크를 생성해야 한다.
```

## 14.3 Claude/Speckit 요구사항

```text
AI-001: 시스템은 Speckit Workspace를 자동 생성해야 한다.
AI-002: 시스템은 입력 문서를 input 디렉터리에 구성해야 한다.
AI-003: 시스템은 /speckit.specify 실행을 지원해야 한다.
AI-004: 시스템은 /speckit.plan 실행을 지원해야 한다.
AI-005: 시스템은 /speckit.tasks 실행을 지원해야 한다.
AI-006: 시스템은 생성 파일을 파싱하고 결과를 저장해야 한다.
AI-007: 시스템은 실행 실패 시 로그와 원인을 Jira/Slack에 알려야 한다.
AI-008: 시스템은 실행 결과를 Run ID 단위로 추적해야 한다.
```

## 14.4 문서 변환 요구사항

```text
DOC-001: 시스템은 HWPX 문서를 Markdown으로 변환해야 한다.
DOC-002: 시스템은 DOCX 문서를 Markdown으로 변환해야 한다.
DOC-003: 시스템은 XLSX 문서를 Markdown Table로 변환해야 한다.
DOC-004: 시스템은 PPTX 문서를 슬라이드별 Markdown으로 변환해야 한다.
DOC-005: 시스템은 변환 결과에 원본 문서명, 버전, 페이지 정보를 포함해야 한다.
DOC-006: 시스템은 변환 실패 문서를 별도 오류 목록으로 분리해야 한다.
```

## 14.5 Slack 요구사항

```text
SLACK-001: 시스템은 Speckit 실행 시작/완료/실패 알림을 발송해야 한다.
SLACK-002: 시스템은 Edge Case 질문이 생성되면 담당자에게 알림을 보내야 한다.
SLACK-003: 시스템은 요구사항 보완 완료 요청을 발송해야 한다.
SLACK-004: 시스템은 Plan/Tasks 생성 완료 시 PM/PL에게 알림을 보내야 한다.
```

---

# 15. 권장 데이터 모델

## 15.1 sdd_run

```sql
CREATE TABLE sdd_run (
    run_id              VARCHAR(50) PRIMARY KEY,
    project_key         VARCHAR(50) NOT NULL,
    target_status       VARCHAR(100) NOT NULL,
    jira_issue_key      VARCHAR(50) NOT NULL,
    phase               VARCHAR(50) NOT NULL,
    command             VARCHAR(50) NOT NULL,
    status              VARCHAR(30) NOT NULL,
    workspace_path      VARCHAR(500),
    started_at          TIMESTAMP,
    finished_at         TIMESTAMP,
    error_message       TEXT
);
```

## 15.2 sdd_source_document

```sql
CREATE TABLE sdd_source_document (
    id                  BIGSERIAL PRIMARY KEY,
    run_id              VARCHAR(50) NOT NULL,
    jira_issue_key      VARCHAR(50),
    confluence_page_id  VARCHAR(100),
    document_type       VARCHAR(100),
    source_file_name    VARCHAR(300),
    source_version      VARCHAR(50),
    markdown_path       VARCHAR(500),
    checksum            VARCHAR(128)
);
```

## 15.3 sdd_generated_artifact

```sql
CREATE TABLE sdd_generated_artifact (
    id                  BIGSERIAL PRIMARY KEY,
    run_id              VARCHAR(50) NOT NULL,
    artifact_type       VARCHAR(100) NOT NULL,
    file_name           VARCHAR(300) NOT NULL,
    file_path           VARCHAR(500) NOT NULL,
    jira_comment_id     VARCHAR(100),
    jira_attachment_id  VARCHAR(100),
    confluence_page_id  VARCHAR(100),
    created_at          TIMESTAMP
);
```

## 15.4 sdd_edge_case

```sql
CREATE TABLE sdd_edge_case (
    id                  BIGSERIAL PRIMARY KEY,
    run_id              VARCHAR(50) NOT NULL,
    requirement_id      VARCHAR(100),
    usecase_id          VARCHAR(100),
    question            TEXT NOT NULL,
    suggested_options   TEXT,
    jira_issue_key      VARCHAR(50),
    status              VARCHAR(30) DEFAULT 'OPEN'
);
```

---

# 16. API 설계 예시

## 16.1 Specify 실행

```http
POST /api/sdd/specify
```

```json
{
  "projectKey": "GOVPJT",
  "targetStatus": "내부검토",
  "documentTypes": [
    "요구사항정의서",
    "유스케이스정의서",
    "컴포넌트정의서",
    "테스트케이스정의서"
  ],
  "jiraIssueKey": "GOVPJT-101"
}
```

## 16.2 Plan 실행

```http
POST /api/sdd/plan
```

```json
{
  "projectKey": "GOVPJT",
  "jiraIssueKey": "GOVPJT-101",
  "sourceRunId": "RUN-20260611-001",
  "techStack": {
    "language": "Java 17",
    "framework": "전자정부프레임워크",
    "database": "PostgreSQL",
    "persistence": "MyBatis",
    "test": ["JUnit5", "Mockito", "MockMvc"]
  }
}
```

## 16.3 Tasks 실행

```http
POST /api/sdd/tasks
```

```json
{
  "projectKey": "GOVPJT",
  "jiraIssueKey": "GOVPJT-101",
  "sourceRunId": "RUN-20260611-002",
  "createJiraTasks": true
}
```

---

# 17. 실행 순서 상세

## 17.1 Specify 자동화 시퀀스

```text
사용자 또는 스케줄러
→ POST /api/sdd/specify
→ Jira에서 내부검토 문서 이슈 조회
→ Jira/Confluence 문서 다운로드
→ Markdown 변환
→ Speckit Workspace 생성
→ /speckit.specify 실행
→ requirements.md, spec.md 생성 확인
→ Edge Case 질문 추출
→ Jira 댓글 등록
→ Jira 첨부 등록
→ Confluence 결과 페이지 생성
→ Slack 알림
```

## 17.2 Plan 자동화 시퀀스

```text
요구사항 보완 완료
→ POST /api/sdd/plan
→ 보완된 문서 재수집
→ Markdown 변환
→ 기존 spec.md와 병합
→ /speckit.plan 실행
→ plan.md 생성
→ component_spec.md, data_model.md, TDD.md 생성/수정
→ Jira/Confluence 등록
→ Slack 알림
```

## 17.3 Tasks 자동화 시퀀스

```text
Plan 검토 완료
→ POST /api/sdd/tasks
→ spec.md, plan.md, component_spec.md, data_model.md, TDD.md 로딩
→ /speckit.tasks 실행
→ tasks.md 생성
→ tasks.md 파싱
→ Jira Story/Task/Sub-task 생성
→ Slack 개발대기 알림
```

---

# 18. Claude 프롬프트 규칙

Claude/Speckit에 넣을 시스템 규칙 또는 `CLAUDE.md`에는 아래 내용을 넣는 것이 좋다.

```markdown
# GovProject SDD Automation Rules

## 1. Traceability

모든 산출물은 다음 추적성을 유지해야 한다.

Requirement ID
→ Use Case ID
→ Screen/Component ID
→ API ID
→ Table ID
→ Test Case ID
→ Jira Issue Key

## 2. Requirement ID Rule

기존 문서에 요구사항 ID가 있으면 절대 변경하지 않는다.
누락된 경우에만 새 ID를 생성한다.

형식:
- REQ-FN-001
- REQ-NF-001
- REQ-SEC-001
- REQ-IF-001
- REQ-DATA-001

## 3. Edge Case Rule

모호하거나 정책 결정이 필요한 항목은 본문에 임의로 확정하지 않는다.
반드시 edge_cases.md에 질문으로 분리한다.

## 4. Output Rule

다음 파일을 생성한다.

Specify 단계:
- requirements.md
- spec.md
- edge_cases.md

Plan 단계:
- plan.md
- component_spec.md
- data_model.md
- TDD.md

Tasks 단계:
- tasks.md

## 5. TDD Rule

구현 작업보다 테스트 작업을 먼저 생성한다.
각 테스트는 관련 Requirement ID를 포함해야 한다.
```

---

# 19. MVP 구현 범위

처음부터 전체 자동화를 다 만들기보다 3단계로 나누는 것이 안전하다.

## 19.1 MVP 1단계: Specify 자동화

```text
Jira 내부검토 문서 조회
→ 문서 Markdown 변환
→ /speckit.specify 실행
→ requirements.md/spec.md 생성
→ Jira 댓글/첨부 등록
→ Edge Case 질문 등록
```

## 19.2 MVP 2단계: Plan 자동화

```text
보완 완료 문서 재수집
→ /speckit.plan 실행
→ plan.md 생성
→ component_spec.md/data_model.md/TDD.md 생성
→ Jira/Confluence 등록
```

## 19.3 MVP 3단계: Tasks 자동화

```text
/speckit.tasks 실행
→ tasks.md 생성
→ Jira Task/Sub-task 생성
→ Slack 담당자 알림
```

---

# 20. 주요 위험과 대응

| 위험 | 내용 | 대응 |
|---|---|---|
| 문서 품질 낮음 | 입력 문서가 부실하면 spec도 부실 | `/speckit.clarify`, checklist 단계 추가 |
| Edge Case 누락 | Claude가 질문을 충분히 못 뽑을 수 있음 | Edge Case 전용 프롬프트와 JSON Schema |
| Jira 댓글 과다 | 긴 문서 댓글은 가독성 낮음 | Confluence 저장 + Jira 링크 | 
| 상태 동기화 오류 | Jira/Confluence/Slack 상태 불일치 | Run ID와 상태 필드 운영 |
| 보안 문서 유출 | Claude 입력에 개인정보 포함 가능 | 마스킹, 접근권한, 로그 제한 |
| Speckit 실행 실패 | CLI/인증/환경 문제 | Worker 격리, 재시도, 실패 알림 |
| 추적성 붕괴 | 요구사항 ID가 바뀜 | ID 유지 규칙 강제 |

---

# 21. 최종 권장 워크플로우

사용자가 제시한 흐름을 보완하면 아래 순서가 가장 안정적이다.

```text
1. Jira Kanban에서 대상 상태 선택
   예: 내부검토

2. 대상 문서 수집
   - 요구사항정의서
   - 유스케이스정의서
   - 컴포넌트/화면정의서
   - 테스트케이스정의서

3. Markdown 변환 및 Speckit Workspace 구성

4. /speckit.specify 실행

5. 생성 결과 등록
   - requirements.md
   - spec.md
   - edge_cases.md

6. Jira 요구사항정의서 이슈에 댓글/첨부/Confluence 링크 등록

7. Edge Case 질문을 Jira Sub-task로 등록

8. 담당자가 Jira/Confluence에서 요구사항정의서 보완

9. 보완 완료 상태 감지

10. /speckit.plan 실행

11. 생성 결과 등록
   - plan.md
   - component_spec.md
   - data_model.md
   - TDD.md

12. PM/PL 검토

13. /speckit.tasks 실행

14. tasks.md를 Jira Task/Sub-task로 변환

15. 개발 착수
```

---

# 22. 결론

이 워크플로우는 충분히 구현 가능하다.

핵심 설계 포인트는 다음과 같다.

```text
1. Jira/Confluence 문서를 Markdown으로 정규화한다.
2. Claude Project 웹 UI가 아니라 Claude Code + Spec Kit 작업공간을 서버/Worker에서 실행한다.
3. 생성 산출물은 Jira 댓글에 전체 본문을 넣기보다 Confluence Page와 Jira 첨부파일로 관리한다.
4. Jira 댓글에는 요약, 링크, 검토 요청을 중심으로 등록한다.
5. Edge Case는 별도 Jira Sub-task로 만들어 추적한다.
6. 요구사항 ID는 절대 임의 변경하지 않고 추적성을 유지한다.
7. Run ID와 Source Document Version을 저장하여 재현성과 감사 이력을 확보한다.
```

최종적으로 이 구조를 적용하면 다음 흐름을 자동화할 수 있다.

```text
요구사항 문서
→ Speckit Specify
→ 요구사항 체계화
→ Edge Case 질문
→ 요구사항 보완
→ Speckit Plan
→ 컴포넌트/데이터/TDD 설계
→ Speckit Tasks
→ Jira 개발 작업 생성
→ 개발 착수
```
