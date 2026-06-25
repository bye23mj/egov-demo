# Phase 4: Result Synchronization — egov-demo

> **생성된 SDD 결과를 JIRA/Confluence/Slack에 자동 동기화**
>
> Phase 3까지 생성된 모든 명세, 설계, 작업 문서를 조직의 협업 도구에 동기화합니다.

---

## 1. Phase 4 개요

### 목표

```
명세 → 설계 → 작업 분해
        ↓
    Phase 4
    (동기화)
        ↓
JIRA + Confluence + Slack
```

- 생성된 문서를 JIRA 이슈에 첨부
- Confluence에 자동 페이지 생성
- Slack으로 팀 알림
- 추적 가능한 실행 로그 저장

### 특징

| 기능 | 설명 |
|------|------|
| **JIRA 동기화** | 8개 마크다운 첨부 + 주석 + 서브태스크 |
| **Confluence 동기화** | 7개 페이지 자동 생성 (명세/설계/작업) |
| **Slack 알림** | 팀 채널로 완료 보고 |
| **실행 로그** | phase4-execution.json으로 추적 |

---

## 2. 아키텍처

### 모듈 구조

```
result_sync_orchestrator.py
├── JiraResultUploader
│   ├── upload_specification_results()
│   ├── upload_planning_results()
│   └── upload_tasks_results()
├── ConfluenceAutoPublisher
│   ├── publish_specification()
│   ├── publish_planning()
│   └── publish_tasks()
└── SlackNotifier
    ├── notify_pipeline_complete()
    ├── notify_error()
    └── _send()
```

### 데이터 흐름

```
specs/
├── requirements.md ──┐
├── spec.md          ├─→ JIRA 첨부
├── edge_cases.md    ├─→ Confluence 페이지
├── plan.md          ├─→ Slack 알림
├── component_spec.md│
├── data_model.md    │
├── TDD.md           │
└── tasks.md ────────┘

결과:
└── phase4-execution.json
```

---

## 3. 사용 방법

### 3.1 환경 설정

#### JIRA (필수)

```bash
export JIRA_EMAIL="bye23mj@gmail.com"
export JIRA_TOKEN="your-api-token"
```

#### Confluence (선택)

```bash
export CONFLUENCE_URL="https://your-instance.atlassian.net"
export CONFLUENCE_EMAIL="your-email@example.com"
export CONFLUENCE_TOKEN="your-api-token"
```

#### Slack (선택)

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

### 3.2 CLI로 실행

```bash
# Phase 4 동기화 실행
python scripts/confluence/result_sync_orchestrator.py \
  GOVPJT-101 \
  /tmp/sdd-workspaces/REQ-001/specs \
  GOVPJT \
  REQ-001

# 또는 Claude Code 스킬 사용
/sdd-sync
  Issue Key: GOVPJT-101
  Run ID: /tmp/sdd-workspaces/REQ-001
  Project Key: GOVPJT
```

### 3.3 Python에서 직접 호출

```python
from scripts.confluence.result_sync_orchestrator import ResultSyncOrchestrator

orchestrator = ResultSyncOrchestrator()
result = orchestrator.sync_all_results(
    issue_key="GOVPJT-101",
    specs_dir="/tmp/sdd-workspaces/REQ-001/specs",
    run_id="REQ-001",
    project_key="GOVPJT"
)

print(f"상태: {result['status']}")
print(f"실행 시간: {result['execution_log']['duration_seconds']}초")
```

---

## 4. 세부 기능

### 4.1 JIRA 동기화 (JiraResultUploader)

#### 명세 업로드

```python
uploader = JiraResultUploader()
result = uploader.upload_specification_results(
    issue_key="GOVPJT-101",
    specs_dir="/tmp/sdd-workspaces/REQ-001/specs",
    run_id="REQ-001"
)
```

**동작**:
- `requirements.md` 첨부 (30개 요구사항)
- `spec.md` 첨부 (2400줄)
- `edge_cases.md` 첨부 (12개 확인 항목)
- 주석 추가: "✅ Specify 완료"

#### 설계 업로드

```python
result = uploader.upload_planning_results(
    issue_key="GOVPJT-101",
    specs_dir="/tmp/sdd-workspaces/REQ-001/specs",
    run_id="REQ-001"
)
```

**동작**:
- `plan.md` 첨부 (5개 Phase, 4개 Story)
- `component_spec.md` 첨부 (Controller/Service/DAO 설계)
- `data_model.md` 첨부 (5개 테이블, ERD)
- `TDD.md` 첨부 (테스트 전략)
- 주석 추가: "✅ Plan 완료"

#### 작업 업로드

```python
result = uploader.upload_tasks_results(
    issue_key="GOVPJT-101",
    specs_dir="/tmp/sdd-workspaces/REQ-001/specs",
    run_id="REQ-001"
)
```

**동작**:
- `tasks.md` 첨부 (33개 Sub-task)
- 서브태스크 자동 생성 (T001~T005 샘플)
- 주석 추가: "✅ Tasks 완료"
- 이슈 상태 변경: `Backlog` → `In Progress`

### 4.2 Confluence 동기화 (ConfluenceAutoPublisher)

#### 명세 페이지 생성

```python
publisher = ConfluenceAutoPublisher()
result = publisher.publish_specification(
    specs_dir="/tmp/sdd-workspaces/REQ-001/specs",
    project_key="GOVPJT",
    requirement_id="REQ-001"
)
```

**생성 페이지**:
```
SDD - GOVPJT (REQ-001)
├── GOVPJT - 요구사항 명세
│   └── requirements.md 내용
├── GOVPJT - 상세 명세
│   └── spec.md 내용
└── GOVPJT - 모호한 항목
    └── edge_cases.md 내용
```

#### 설계 페이지 생성

```python
result = publisher.publish_planning(
    specs_dir="/tmp/sdd-workspaces/REQ-001/specs",
    project_key="GOVPJT",
    requirement_id="REQ-001"
)
```

**생성 페이지**:
```
SDD - GOVPJT (REQ-001) - 설계
├── GOVPJT - 구현 계획 (plan.md)
├── GOVPJT - 컴포넌트 설계 (component_spec.md)
├── GOVPJT - 데이터 모델 (data_model.md)
└── GOVPJT - TDD 전략 (TDD.md)
```

#### 작업 페이지 생성

```python
result = publisher.publish_tasks(
    specs_dir="/tmp/sdd-workspaces/REQ-001/specs",
    project_key="GOVPJT",
    requirement_id="REQ-001"
)
```

**생성 페이지**:
```
SDD - GOVPJT (REQ-001) - 작업
└── GOVPJT - Task 분해 (tasks.md)
    ├── Story 1: 사용자 관리 (T001~T009)
    ├── Story 2: 게시판 관리 (T010~T018)
    ├── Story 3: 댓글 기능 (T019~T027)
    └── Story 4: 검색 기능 (T028~T033)
```

### 4.3 Slack 알림 (SlackNotifier)

#### 파이프라인 완료 알림

```python
notifier = SlackNotifier()
stats = {
    'requirements': 30,
    'stories': 4,
    'subtasks': 33,
    'tables': 5,
    'files': 8
}
notifier.notify_pipeline_complete("GOVPJT", "REQ-001", stats)
```

**메시지 형식**:
```
🎉 SDD 자동화 파이프라인 완료!

프로젝트: GOVPJT
Run ID: REQ-001

📊 생성 결과:
• 요구사항: 30개
• Story: 4개
• Sub-task: 33개
• 테이블: 5개
• 생성 파일: 8개

⏰ 완료 시간: 2026-06-11 15:45:30

📝 다음 단계:
1. 생성된 문서 검토 (Confluence)
2. 담당자 배정 (JIRA)
3. 개발 시작 (Feature branch)
```

#### 에러 알림

```python
notifier.notify_error(
    phase="Specify",
    error_message="Specs 디렉토리 없음",
    run_id="REQ-001"
)
```

---

## 5. 실행 결과 분석

### 5.1 Execution Log

```json
{
  "run_id": "REQ-001",
  "issue_key": "GOVPJT-101",
  "project_key": "GOVPJT",
  "started_at": "2026-06-11T15:40:00Z",
  "completed_at": "2026-06-11T15:45:30Z",
  "duration_seconds": 330,
  "status": "success",
  "jira": {
    "specification": {
      "requirements": true,
      "spec": true,
      "edge_cases": true,
      "comment": true
    },
    "planning": {
      "plan": true,
      "component_spec": true,
      "data_model": true,
      "tdd": true,
      "comment": true
    },
    "tasks": {
      "tasks": true,
      "subtasks_created": 5,
      "comment": true
    }
  },
  "confluence": {
    "specification": {
      "requirements": "PAGE-ABC123",
      "spec": "PAGE-DEF456",
      "edge_cases": "PAGE-GHI789"
    },
    "planning": {
      "plan": "PAGE-JKL012",
      "component_spec": "PAGE-MNO345",
      "data_model": "PAGE-PQR678",
      "tdd": "PAGE-STU901"
    },
    "tasks": "PAGE-VWX234"
  },
  "slack": {
    "message_sent": true
  }
}
```

### 5.2 실행 결과 검증

```bash
# 1. 로컬 로그 확인
cat /tmp/sdd-workspaces/REQ-001/specs/phase4-execution.json

# 2. JIRA 확인
# → GOVPJT-101에 8개 파일 첨부됨
# → 3개 주석 추가됨
# → 5개 서브태스크 생성됨
# → 상태: In Progress

# 3. Confluence 확인
# → /SDD/GOVPJT (REQ-001)/ 아래 7개 페이지 생성됨

# 4. Slack 확인
# → #engineering 채널에 완료 보고 메시지
```

---

## 6. 트러블슈팅

### 문제 1: JIRA 이슈 없음

**증상**:
```
Error: JIRA 이슈를 찾을 수 없습니다 (GOVPJT-101)
```

**원인**:
- 이슈 키 오타
- JIRA 프로젝트 접근 권한 없음
- API 토큰 만료

**해결**:
```bash
# 1. 이슈 키 확인
echo "GOVPJT-101"  # 정확한 형식

# 2. 권한 확인
# → JIRA 프로젝트 관리자에 문의

# 3. 토큰 재발급
# → Atlassian API 토큰 페이지
```

### 문제 2: Specs 디렉토리 없음

**증상**:
```
Error: Specs 디렉토리를 찾을 수 없습니다
```

**원인**:
- Phase 1~5 미실행

**해결**:
```bash
# Phase 순차 실행
/sdd-collect      # Phase 1
/sdd-normalize    # Phase 2
/sdd-specify      # Phase 3
/sdd-plan         # Phase 4
/sdd-tasks        # Phase 5
/sdd-sync         # Phase 6 (결과 동기화)
```

### 문제 3: Confluence 페이지 생성 실패

**증상**:
```
Warning: Confluence 동기화 스킵 (CONFLUENCE_TOKEN 미설정)
```

**원인**:
- Confluence 토큰 미설정

**해결**:
```bash
export CONFLUENCE_TOKEN="your-api-token"
export CONFLUENCE_URL="https://your-instance.atlassian.net"

# 또는 스킬 재실행
/sdd-sync
```

### 문제 4: Slack 알림 미작동

**증상**:
```
Warning: Slack 알림 스킵 (SLACK_WEBHOOK_URL 미설정)
```

**원인**:
- Slack Webhook URL 미설정

**해결**:
```bash
# 1. Slack App 관리에서 Webhook URL 생성
# https://api.slack.com/messaging/webhooks

# 2. 환경변수 설정
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# 3. 스킬 재실행
/sdd-sync
```

---

## 7. 다음 단계

### Phase 4 완료 후

```
1️⃣ Confluence 문서 검토
   └── JIRA 이슈 열기 → Confluence 링크 클릭

2️⃣ JIRA Sub-task 확인
   └── GOVPJT-101 → Sub-task 탭 (T001~T005 확인)

3️⃣ 팀 회의 (1시간)
   └── Sub-task 담당자 배정, 일정 조율

4️⃣ Feature Branch 생성
   └── feature/T001-controller
   └── feature/T002-service-impl
   └── ...

5️⃣ TDD 기반 개발 시작
   └── Red → Green → Refactor
```

### Phase 5: 구현 (Optional)

```
각 Sub-task별로 TDD 기반 구현

예: T001 - Controller 작성
1. test_EgovSampleController.java (Red - 테스트 실패)
2. EgovSampleController.java 구현 (Green - 테스트 통과)
3. 코드 리팩토링 (Refactor)
4. Pull Request

예상 기간: 2주~1개월 (팀 규모, 복잡도 에 따라)
```

---

## 8. 참고

### 파일 목록

| 파일 | 역할 |
|------|------|
| `jira_result_uploader.py` | JIRA 동기화 (첨부, 주석, 서브태스크) |
| `confluence_auto_publisher.py` | Confluence 페이지 자동 생성 |
| `slack_notifier.py` | Slack 알림 |
| `result_sync_orchestrator.py` | Phase 4 통합 조율자 |

### API 참고

| API | 역할 |
|-----|------|
| `JiraAPI.attach_file()` | JIRA에 파일 첨부 |
| `JiraAPI.create_comment()` | JIRA 주석 추가 |
| `JiraAPI.create_subtask()` | JIRA 서브태스크 생성 |
| `JiraAPI.transition_issue()` | JIRA 상태 변경 |
| `ConfluenceAPI.create_page()` | Confluence 페이지 생성 |
| `SlackNotifier.notify_*()` | Slack 메시지 전송 |

---

**마지막 업데이트**: 2026-06-11  
**버전**: 1.0.0
