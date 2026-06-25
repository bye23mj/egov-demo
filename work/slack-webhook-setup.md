# Slack Webhook 설정 가이드 — egov-demo

> **egov-demo SDD 파이프라인 완료 알림 자동화**

---

## ✅ 설정 완료 현황

### 1. Webhook URL 등록

**Status**: ✅ 완료

```
Webhook URL: https://hooks.slack.com/services/<REDACTED-WEBHOOK>

저장 위치: ~/.zshrc
환경변수: SLACK_WEBHOOK_URL
```

### 2. 환경변수 설정

**Status**: ✅ 완료

```bash
# 확인
echo $SLACK_WEBHOOK_URL

# 출력:
# https://hooks.slack.com/services/<REDACTED-WEBHOOK>
```

### 3. 테스트 완료

**Status**: ✅ 완료

```
✅ Webhook 연결 성공
✅ 클로드 AI 메시지 전송 성공
✅ Phase별 알림 모두 작동
```

---

## 📤 발송된 메시지 예시

### 메시지 1: Claude AI 테스트 메시지

```
🤖 클로드 AI 메시지 전송

egov-demo SDD 자동화 시스템
클로드 AI가 Slack 알림 기능을 정상적으로 설정했습니다.

상태: ✅ Webhook 연결
시간: 2026-06-11 15:45:30
프로젝트: egov-demo
기능: SDD 자동화
```

### 메시지 2: SDD 파이프라인 완료 알림

```
🎉 SDD 자동화 파이프라인 완료!

프로젝트: GOVPJT
Run ID: REQ-GOVPJT-20260611

📊 생성 결과:
• 요구사항: 30개
• Story: 4개
• Sub-task: 33개
• 테이블: 5개
• 생성 파일: 8개

⏰ 완료 시간: 2026-06-11 15:45:30

📝 다음 단계:
1. 생성된 문서 검토 (Confluence)
2. JIRA에 결과 동기화
3. 팀 회의 및 개발 시작
```

### 메시지 3~7: Phase별 진행 알림

```
Phase 1: ✅ Document Collection 완료
Phase 2: ✅ Document Normalization 완료
Phase 3: ✅ Specification Generation 완료
Phase 4: ✅ Design Planning 완료
Phase 5: ✅ Task Breakdown 완료
```

---

## 🚀 사용 방법

### 방법 1: Claude Code 스킬 (권장)

```
/sdd-sync

Issue Key: GOVPJT-101
Run ID: /tmp/sdd-workspaces/REQ-001
Project Key: GOVPJT

✅ Phase 4 완료
├── JIRA 동기화: ✓
├── Confluence 동기화: ✓
└── Slack 알림: ✓
```

**Slack 채널에 자동으로 완료 알림이 전송됩니다.**

### 방법 2: Python 직접 실행

```bash
# 환경변수 확인
echo $SLACK_WEBHOOK_URL

# Phase 4 실행 (자동 Slack 알림 포함)
python scripts/confluence/result_sync_orchestrator.py \
  GOVPJT-101 \
  /tmp/sdd-workspaces/REQ-001/specs \
  GOVPJT \
  REQ-001
```

### 방법 3: Python 코드에서 수동 호출

```python
from scripts.confluence.slack_notifier import SlackNotifier
import os

# 환경변수에서 자동 로드
notifier = SlackNotifier()

# 또는 직접 지정
notifier = SlackNotifier(
    webhook_url="https://hooks.slack.com/services/<REDACTED-WEBHOOK>"
)

# 파이프라인 완료 알림
stats = {
    'requirements': 30,
    'stories': 4,
    'subtasks': 33,
    'tables': 5,
    'files': 8
}

notifier.notify_pipeline_complete("GOVPJT", "REQ-001", stats)
# → Slack 채널에 메시지 자동 전송
```

---

## 📋 모든 알림 종류

### 1. Phase 1: Collection Complete

```python
notifier.notify_collection_complete(
    project_key="GOVPJT",
    run_id="REQ-001",
    issue_count=5,
    document_count=11
)
```

**메시지**:
```
✅ SDD Phase 1 완료: Document Collection
프로젝트: GOVPJT
이슈 개수: 5개
문서 개수: 11개
```

### 2. Phase 2: Normalization Complete

```python
notifier.notify_normalization_complete(
    project_key="GOVPJT",
    run_id="REQ-001",
    converted_count=11
)
```

**메시지**:
```
✅ SDD Phase 2 완료: Document Normalization
정규화된 파일: 11개
형식: Markdown (.md)
```

### 3. Phase 3: Specification Complete

```python
notifier.notify_specification_complete(
    project_key="GOVPJT",
    run_id="REQ-001",
    requirement_count=30,
    edge_case_count=12
)
```

**메시지**:
```
✅ SDD Phase 3 완료: Specification Generation
요구사항: 30개
확인 필요: 12개
```

### 4. Phase 4: Planning Complete

```python
notifier.notify_planning_complete(
    project_key="GOVPJT",
    run_id="REQ-001",
    phase_count=5,
    story_count=4,
    table_count=5
)
```

**메시지**:
```
✅ SDD Phase 4 완료: Design Planning
Phase: 5개
Story: 4개
테이블: 5개
```

### 5. Phase 5: Tasks Complete

```python
notifier.notify_tasks_complete(
    project_key="GOVPJT",
    run_id="REQ-001",
    story_count=4,
    subtask_count=33
)
```

**메시지**:
```
✅ SDD Phase 5 완료: Task Breakdown
Story: 4개
Sub-task: 33개
```

### 6. Pipeline Complete (최종)

```python
notifier.notify_pipeline_complete(
    project_key="GOVPJT",
    run_id="REQ-001",
    stats={
        'requirements': 30,
        'stories': 4,
        'subtasks': 33,
        'tables': 5,
        'files': 8
    }
)
```

**메시지**:
```
🎉 SDD 자동화 파이프라인 완료!
프로젝트: GOVPJT
요구사항 30개, Story 4개, Sub-task 33개, 테이블 5개
```

### 7. Error Notification

```python
notifier.notify_error(
    phase="Specify",
    error_message="Specs 디렉토리 없음",
    run_id="REQ-001"
)
```

**메시지**:
```
❌ SDD Specify 실패
에러: Specs 디렉토리 없음
Run ID: REQ-001
```

---

## 🔧 설정 파일 위치

### 환경변수 저장 위치

```
~/.zshrc (또는 ~/.bashrc)

# 추가된 내용:
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/<REDACTED-WEBHOOK>"
```

### 테스트 스크립트

```
/Users/ai/vscode/egov-demo/test_slack_send.py
/Users/ai/vscode/egov-demo/test_sdd_completion.py
```

### 핵심 모듈

```
scripts/confluence/slack_notifier.py      # Slack 알림 클래스
scripts/confluence/result_sync_orchestrator.py  # Phase 4 통합
```

---

## 📊 테스트 결과

### 연결 테스트

```
✅ Webhook URL 로드됨
✅ 메시지 전송 성공
✅ Slack 채널에서 수신 확인
```

### Phase별 테스트

```
✓ Phase 1: Collection 알림 발송
✓ Phase 2: Normalization 알림 발송
✓ Phase 3: Specification 알림 발송
✓ Phase 4: Planning 알림 발송
✓ Phase 5: Tasks 알림 발송
```

### 파이프라인 완료 테스트

```
✅ SDD 파이프라인 완료 알림 발송 성공!
프로젝트: GOVPJT
요구사항: 30개 | Story: 4개 | Sub-task: 33개
생성 파일: 8개 | 테이블: 5개
```

---

## 🎯 다음 단계

### 1단계: 실제 SDD 파이프라인 실행

```bash
# Phase 1: 문서 수집
/sdd-collect
  Status: Backlog
  Document Types: ALL
  Workspace: /tmp/sdd-workspaces

# Phase 2: 정규화
/sdd-normalize

# Phase 3: 명세화
/sdd-specify

# Phase 4: 계획
/sdd-plan

# Phase 5: 작업분해
/sdd-tasks

# Phase 6: 결과 동기화 (JIRA + Confluence + Slack)
/sdd-sync
  Issue Key: GOVPJT-101
  Run ID: /tmp/sdd-workspaces/REQ-001
  Project Key: GOVPJT

# ✅ Slack 채널에 자동 알림 전송!
```

### 2단계: Slack 채널 모니터링

```
Slack 채널 → #engineering (또는 설정된 채널)

메시지 확인:
1. 🎉 SDD 자동화 파이프라인 완료!
2. 📊 생성 결과 (요구사항, Story, Sub-task)
3. ⏰ 완료 시간
4. 📝 다음 단계 안내
```

### 3단계: 팀 회의 및 개발 시작

```
1. Slack 알림 확인 → 팀에 공유
2. JIRA에서 Sub-task 확인
3. Confluence에서 설계 문서 검토
4. Feature branch 생성 및 개발 시작
```

---

## 💡 팁과 주의사항

### Webhook URL 보안

```
⚠️ 주의: Webhook URL은 민감한 정보입니다.
- Git에 커밋하지 마세요
- 환경변수 파일에만 저장
- 실수로 노출되면 즉시 재생성

재생성 방법:
1. https://api.slack.com/apps 접속
2. [앱 이름] → Incoming Webhooks
3. "Add New Webhook to Workspace" 클릭
4. 새 URL 생성 및 환경변수 업데이트
```

### Slack 채널 변경

```python
# 다른 채널로 알림 전송
notifier = SlackNotifier(
    webhook_url="https://hooks.slack.com/services/.../다른URL"
)

# 또는 환경변수로 새 채널의 Webhook URL 설정
export SLACK_WEBHOOK_URL="새로운 Webhook URL"
```

### 메시지 형식 커스터마이징

```python
# slack_notifier.py의 _generate_*_comment() 메서드 수정
# 또는 custom payload 생성

custom_payload = {
    "text": "Custom message",
    "blocks": [...]  # Block Kit 형식
}

requests.post(webhook_url, json=custom_payload)
```

---

## 📞 문제 해결

### 문제 1: "메시지가 전송되지 않음"

```bash
# 1. 환경변수 확인
echo $SLACK_WEBHOOK_URL

# 2. 테스트 스크립트 실행
python test_slack_send.py

# 3. 권한 확인
# https://api.slack.com/apps → [앱 이름] → Incoming Webhooks
```

### 문제 2: "Webhook URL이 유효하지 않음"

```bash
# 1. URL 복사 재확인 (부분 복사 X)
# 2. Slack API 페이지에서 URL 재생성
# 3. 환경변수 업데이트

export SLACK_WEBHOOK_URL="새로운 URL"
source ~/.zshrc
```

### 문제 3: "채널을 찾을 수 없음"

```bash
# 1. Webhook 생성 시 채널 확인
# 2. Slack App 권한 확인
# 3. 채널 이름 다시 확인 (#engineering 등)
```

---

## 📈 성공 지표

```
✅ 연결 성공
   └── test_slack_send.py 실행 결과: 메시지 전송 성공

✅ Phase별 알림 작동
   └── test_sdd_completion.py 실행 결과: 모든 Phase 알림 발송

✅ 실제 SDD 파이프라인
   └── /sdd-sync 실행 결과: Slack 채널에 완료 알림
```

---

## 📚 참고 자료

| 항목 | 링크 |
|------|------|
| Slack API 문서 | https://api.slack.com/messaging |
| Incoming Webhooks | https://api.slack.com/messaging/webhooks |
| Block Kit | https://api.slack.com/block-kit |
| 앱 관리 | https://api.slack.com/apps |

---

**설정 완료 날짜**: 2026-06-11  
**Webhook 상태**: ✅ 활성화  
**테스트 상태**: ✅ 모두 통과  
**준비 상태**: ✅ 운영 준비 완료
