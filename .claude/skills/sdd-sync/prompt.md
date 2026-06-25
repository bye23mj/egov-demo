# SDD Sync Skill — Prompt Logic

## 파라미터 수집

### Step 1: JIRA Issue Key 입력 요청
```
JIRA 이슈 키를 입력해주세요 (예: GOVPJT-101):
```

입력값 검증:
- 형식: `{프로젝트}-{숫자}` (예: GOVPJT-101)
- 이슈가 실제로 존재하는지 확인

### Step 2: Run ID 입력 요청
```
Run ID 또는 Workspace 경로를 입력해주세요 (예: /tmp/sdd-workspaces/REQ-001):
```

입력값 검증:
- 경로 또는 ID 형식 확인
- specs/ 디렉토리 존재 확인

### Step 3: Project Key 입력 요청
```
프로젝트 키를 입력해주세요 (예: GOVPJT):
```

입력값 검증:
- JIRA 프로젝트 키 형식 확인

## Python 스크립트 실행

### 호출
```bash
python scripts/confluence/result_sync_orchestrator.py \
  <issue_key> <specs_dir> <project_key> <run_id>
```

### 파라미터
- `issue_key`: JIRA 이슈 키 (필수)
- `specs_dir`: Specs 디렉토리 경로 (필수)
- `project_key`: JIRA 프로젝트 키 (필수)
- `run_id`: 실행 ID (선택사항, 로깅용)

## Phase 4 실행 단계

### Step 1: JIRA 동기화 (5분)
```
📤 JIRA 결과 업로드 중...

JIRA 이슈 (GOVPJT-101):
├── requirements.md (첨부)
├── spec.md (첨부)
├── edge_cases.md (첨부)
├── plan.md (첨부)
├── component_spec.md (첨부)
├── data_model.md (첨부)
├── TDD.md (첨부)
└── tasks.md (첨부)

주석 추가:
├── Specify 완료 (30개 요구사항)
├── Plan 완료 (4개 Story, 5개 테이블)
└── Tasks 완료 (33개 Sub-task)

서브태스크:
├── T001: Controller 작성
├── T002: Service 구현
├── T003: DAO 구현
├── T004: Mapper 작성
└── T005: 페이징 기능 추가

상태 변환:
└── Backlog → In Progress

✓ JIRA 동기화 완료
```

### Step 2: Confluence 동기화 (3분)
```
📖 Confluence 페이지 생성 중...

명세 영역:
├── GOVPJT - 요구사항 명세 (requirements.md)
├── GOVPJT - 상세 명세 (spec.md)
└── GOVPJT - 모호한 항목 (edge_cases.md)

설계 영역:
├── GOVPJT - 구현 계획 (plan.md)
├── GOVPJT - 컴포넌트 설계 (component_spec.md)
├── GOVPJT - 데이터 모델 (data_model.md)
└── GOVPJT - TDD 전략 (TDD.md)

작업 영역:
└── GOVPJT - Task 분해 (tasks.md)

✓ Confluence 동기화 완료 (7개 페이지)
```

### Step 3: Slack 알림 (1분)
```
📢 Slack 알림 전송 중...

#engineering 채널:
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

✓ Slack 알림 완료
```

### Step 4: 실행 로그 저장
```
✓ phase4-execution.json 저장

내용:
{
  "run_id": "REQ-001",
  "issue_key": "GOVPJT-101",
  "project_key": "GOVPJT",
  "started_at": "2026-06-11T15:40:00Z",
  "completed_at": "2026-06-11T15:45:30Z",
  "duration_seconds": 330,
  "status": "success",
  "jira": {
    "files_attached": 8,
    "comments_added": 3,
    "subtasks_created": 5
  },
  "confluence": {
    "pages_created": 7
  },
  "slack": {
    "message_sent": true
  }
}
```

## 에러 처리

### JIRA 이슈 없음
```
Error: JIRA 이슈를 찾을 수 없습니다 (GOVPJT-101)

확인사항:
1. 이슈 키 확인 (예: GOVPJT-101)
2. 프로젝트 접근 권한 확인
3. JIRA API 토큰 확인
```

### Specs 디렉토리 없음
```
Error: Specs 디렉토리를 찾을 수 없습니다

경로: /tmp/sdd-workspaces/REQ-001/specs/

필수 단계:
1. /sdd-collect 실행
2. /sdd-normalize 실행
3. /sdd-specify 실행
4. /sdd-plan 실행
5. /sdd-tasks 실행
```

### JIRA 권한 부족
```
Error: JIRA 이슈에 대한 쓰기 권한이 없습니다

해결:
1. JIRA 프로젝트 관리자 확인
2. 이슈 편집 권한 확인
3. API 토큰 재발급
```

### Confluence 연결 실패
```
Warning: Confluence 동기화 스킵 (CONFLUENCE_TOKEN 미설정)

설정 방법:
export CONFLUENCE_TOKEN="your-api-token"

또는 별도로 Confluence 페이지 생성 필요
```

### Slack 연결 실패
```
Warning: Slack 알림 스킵 (SLACK_WEBHOOK_URL 미설정)

설정 방법:
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

또는 수동 알림 필요
```

## 성공 응답

```
✅ Phase 4 완료

JIRA 동기화:
✓ 8개 파일 첨부
✓ 3개 주석 추가
✓ 5개 서브태스크 생성
✓ 상태 변경: In Progress

Confluence 동기화:
✓ 7개 페이지 생성
✓ Requirements, Specification, Planning, Component Design, Data Model, TDD, Tasks

Slack 알림:
✓ #engineering 채널로 보고

실행 시간: 330초 (5분 30초)
저장 위치: /tmp/sdd-workspaces/REQ-001/specs/phase4-execution.json

다음 단계:
1. Confluence에서 생성된 문서 검토
2. JIRA에서 Sub-task 확인 및 담당자 배정
3. Feature branch 생성 및 개발 시작
```

## 유효성 검사

실행 전 다음을 확인합니다:

```
✓ JIRA 이슈 존재 여부 (GOVPJT-101)
✓ Specs 디렉토리 존재 (requirements.md 등)
✓ JIRA 쓰기 권한
✓ Confluence 토큰 (선택)
✓ Slack Webhook URL (선택)
```

## 복구 전략

실패한 경우 재시도:

```
1. 환경변수 확인
2. 권한 확인
3. JIRA 이슈 상태 확인
4. 이미 첨부된 파일 확인
5. 부분 수동 완료
```

**주의**: 파일을 다시 첨부하면 중복될 수 있습니다.
