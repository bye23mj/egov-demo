# SDD Collect Skill

JIRA에서 문서를 수집하여 Workspace를 생성합니다.

## 사용법

```
/sdd-collect
```

## 입력 파라미터

| 파라미터 | 설명 | 필수 | 예시 |
|---------|------|------|------|
| status | Kanban 상태 | ✅ | 내부검토 |
| document_types | 문서 종류 (쉼표 구분) | ✅ | 요구사항정의서,유스케이스정의서 |
| workspace | 저장 위치 | ✅ | /tmp/sdd-workspaces |
| requirement_id | 요구사항 ID (선택) | ❌ | REQ-001 |

## 예시

```
status: 내부검토
document_types: 요구사항정의서
workspace: /tmp/sdd-workspaces
requirement_id: REQ-001
```

## 동작

1. JIRA 상태별 문서 조회
2. 첨부파일 다운로드
3. Workspace 구조 생성
4. 메타데이터 저장

## 출력

```
✅ 문서 수집 완료
Run ID: RUN-20260611-ABC
저장 위치: /tmp/sdd-workspaces/RUN-20260611-ABC
```

## 관련 문서

- [SDD Workflow Guide](../../../scripts/SDD_WORKFLOW.md)
