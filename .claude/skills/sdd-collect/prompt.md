# /sdd-collect - JIRA 문서 수집

사용자로부터 다음 파라미터를 입력받습니다:

```yaml
status: 내부검토
document_types: 요구사항정의서,유스케이스정의서
workspace: /tmp/sdd-workspaces
requirement_id: REQ-001  # (선택)
```

## 필수 입력값 확인

다음 값이 누락되었으면 사용자에게 입력하도록 요청합니다:

- **status**: JIRA Kanban 상태 (예: 내부검토, 보완완료)
- **document_types**: 수집할 문서 종류 (쉼표 구분)
- **workspace**: 저장할 경로

## 파라미터 검증

| 파라미터 | 검증 규칙 |
|---------|---------|
| status | 비어있지 않음 |
| document_types | 비어있지 않음, 쉼표로 구분 가능 |
| workspace | 존재하거나 생성 가능한 경로 |
| requirement_id | 선택사항, 영문자/하이픈으로만 구성 |

## 실행

다음 Python 스크립트를 호출합니다:

```bash
python scripts/confluence-sync.py sdd collect \
  --status "{status}" \
  --document-types "{document_types}" \
  --project-key "GOVPJT" \
  --workspace "{workspace}" \
  {requirement_id_param}
```

여기서:
- `{status}`: 사용자가 입력한 상태
- `{document_types}`: 사용자가 입력한 문서 종류
- `{workspace}`: 사용자가 입력한 저장 위치
- `{requirement_id_param}`: `--requirement-id {requirement_id}` (requirement_id가 있는 경우에만)

## 예시

### 입력
```
상태: 내부검토
문서 종류: 요구사항정의서
저장 위치: /tmp/sdd-workspaces
요구사항 ID: REQ-001
```

### 실행 명령
```bash
python scripts/confluence-sync.py sdd collect \
  --status "내부검토" \
  --document-types "요구사항정의서" \
  --workspace "/tmp/sdd-workspaces" \
  --requirement-id "REQ-001"
```

### 예상 출력
```
📁 SDD 문서 수집 시작
   Run ID: RUN-20260611-K7F
   Workspace: /tmp/sdd-workspaces/RUN-20260611-K7F
   Status: 내부검토

✅ 문서 수집 완료
──────────────────────────────
  수집된 문서: 3개
  저장 위치: /tmp/sdd-workspaces/RUN-20260611-K7F
──────────────────────────────
```

## 에러 처리

- **연결 실패**: JIRA 연결 확인 메시지
- **토큰 만료**: JIRA 토큰 재설정 안내
- **문서 없음**: 해당 상태의 문서가 없음 알림

## 다음 단계

문서 수집 완료 후:
1. `/sdd-normalize` 실행 (문서 정규화)
2. `/sdd-specify` 실행 (Speckit Specify)
