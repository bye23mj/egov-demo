# SDD Sync Skill

생성된 명세/설계/작업을 JIRA/Confluence/Slack에 자동 동기화합니다.

## 사용법

```
/sdd-sync
```

## 입력 파라미터

| 파라미터 | 설명 | 필수 | 예시 |
|---------|------|------|------|
| issue_key | JIRA 이슈 키 | ✅ | GOVPJT-101 |
| run_id | 실행 ID 또는 Workspace 경로 | ✅ | /tmp/sdd-workspaces/REQ-001 |
| project_key | JIRA 프로젝트 키 | ✅ | GOVPJT |

## 동작

### Step 1: JIRA 동기화
- 생성된 문서 첨부 (requirements.md, spec.md, edge_cases.md, plan.md, component_spec.md, data_model.md, TDD.md, tasks.md)
- 완료 주석 추가 (Specify, Plan, Tasks)
- 서브태스크 자동 생성
- 이슈 상태 전환 (In Progress)

### Step 2: Confluence 동기화
- 명세 페이지 생성 (Requirements, Specification, Edge Cases)
- 설계 페이지 생성 (Plan, Component Design, Data Model, TDD)
- 작업 페이지 생성 (Task Breakdown)
- 라벨 및 메타데이터 추가

### Step 3: Slack 알림
- 파이프라인 완료 보고
- 통계 정보 (요구사항, Story, Sub-task, 테이블)
- 생성 파일 목록
- 다음 단계 안내

## 생성 파일

| 위치 | 파일 | 내용 |
|------|------|------|
| **JIRA** | 이슈 첨부 | 8개 마크다운 문서 |
| **Confluence** | /SDD/{프로젝트}/ | 7개 페이지 자동 생성 |
| **Slack** | #engineering | 완료 보고 메시지 |
| **로컬** | specs/phase4-execution.json | 실행 로그 |

## 출력

```
✅ Phase 4 실행 완료

JIRA 동기화:
✓ 8개 파일 첨부 (GOVPJT-101)
✓ 3개 주석 추가
✓ 5개 서브태스크 생성
✓ 상태 변경: In Progress

Confluence 동기화:
✓ 7개 페이지 생성
✓ REQUIREMENTS, SPEC, PLANNING 영역

Slack 알림:
✓ #engineering 채널로 보고

실행 로그: phase4-execution.json
```

## 환경변수 (선택사항)

```bash
# Slack 알림 활성화
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Confluence 설정 (confluence-sync.py와 동일)
export CONFLUENCE_URL="https://your-instance.atlassian.net"
export CONFLUENCE_EMAIL="your-email@example.com"
export CONFLUENCE_TOKEN="your-api-token"
```

## 사전 요구사항

1. **JIRA 설정**
   - JIRA_EMAIL, JIRA_TOKEN 환경변수 설정
   - 이슈에 대한 쓰기 권한

2. **Confluence 설정 (선택)**
   - CONFLUENCE_TOKEN 환경변수 설정
   - Confluence Space 접근 권한

3. **Slack 설정 (선택)**
   - SLACK_WEBHOOK_URL 환경변수 설정
   - Slack Webhook 권한

## 예시

```
Issue Key: GOVPJT-101
Run ID: /tmp/sdd-workspaces/REQ-001
Project Key: GOVPJT

✅ Phase 4 (Sync) 완료
├── JIRA: 8개 파일 첨부 + 주석 + 서브태스크
├── Confluence: 7개 페이지 생성
└── Slack: 완료 보고 전송
```

## 동작 흐름

```
/sdd-sync (Phase 4 시작)
   ↓
JIRA 이슈 확인
   ↓
specs/ 디렉토리에서 모든 생성 파일 로드
   ↓
JIRA에 첨부 + 주석 + 서브태스크 추가
   ↓
Confluence에 페이지 자동 생성
   ↓
Slack으로 완료 보고
   ↓
phase4-execution.json 저장
   ↓
✅ 완료
```

## 다음 단계

1. **팀 회의**
   - JIRA 이슈에서 Sub-task 확인
   - 담당자 배정

2. **개발 시작**
   - Feature branch 생성 (feature/T001-controller)
   - TDD 기반 구현

3. **Confluence 문서 활용**
   - 설계 검증
   - 컴포넌트 아키텍처 확인
   - 데이터 모델 검증

## 주의사항

- **이슈 권한**: JIRA 이슈에 대한 편집 권한 필수
- **Confluence 선택**: Confluence URL 미설정 시 페이지 생성 스킵
- **Slack 선택**: Webhook URL 미설정 시 알림 스킵
- **복구 불가**: 한 번 실행하면 JIRA 이슈에 첨부되므로 신중하게 실행

## 문제 해결

### JIRA 연결 실패
```bash
# 환경변수 확인
echo $JIRA_EMAIL
echo $JIRA_TOKEN

# 권한 확인
# → JIRA 프로젝트의 이슈에 대한 편집 권한 확인
```

### Confluence 페이지 생성 미작동
```bash
# CONFLUENCE_TOKEN 환경변수 설정
export CONFLUENCE_TOKEN="your-token"
```

### Slack 알림 미작동
```bash
# SLACK_WEBHOOK_URL 확인
# → Slack App 관리에서 Webhook URL 재생성
```
