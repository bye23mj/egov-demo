# /sdd-normalize - 문서 정규화

사용자로부터 다음 파라미터를 입력받습니다:

```yaml
workspace: /tmp/sdd-workspaces
requirement_id: REQ-001
```

## 필수 입력값 확인

다음 값이 누락되었으면 사용자에게 입력하도록 요청합니다:

- **workspace**: Workspace 저장 위치 (기본: /tmp/sdd-workspaces)
- **requirement_id**: 요구사항 ID (예: REQ-001)

## 파라미터 검증

| 파라미터 | 검증 규칙 |
|---------|---------|
| workspace | 존재하는 경로 |
| requirement_id | 영문자/숫자/하이픈으로만 구성 |

## 경로 구성

입력된 파라미터를 조합하여 다음 경로를 생성합니다:

```
full_path = {workspace}/{requirement_id}
input_dir = {full_path}/input
normalized_dir = {full_path}/normalized
```

### 예시

```
workspace: /tmp/sdd-workspaces
requirement_id: REQ-001

결과:
  full_path: /tmp/sdd-workspaces/REQ-001
  input_dir: /tmp/sdd-workspaces/REQ-001/input
  normalized_dir: /tmp/sdd-workspaces/REQ-001/normalized
```

## 실행

다음 Python 스크립트를 호출합니다:

```bash
python scripts/confluence-sync.py sdd normalize \
  --run-id "{full_path}"
```

## 예시

### 입력
```
저장 위치: /tmp/sdd-workspaces
요구사항 ID: REQ-001
```

### 경로 구성
```
/tmp/sdd-workspaces/REQ-001/input → 정규화
↓
/tmp/sdd-workspaces/REQ-001/normalized
```

### 실행 명령
```bash
python scripts/confluence-sync.py sdd normalize \
  --run-id "/tmp/sdd-workspaces/REQ-001"
```

### 예상 출력
```
🔄 문서 정규화 시작
   경로: /tmp/sdd-workspaces/REQ-001

⚙️  정규화 중...
   ✓ 요구사항정의서_v0.3.docx → Markdown
   ✓ 테스트케이스_v0.1.xlsx → Markdown Table

✅ 문서 정규화 완료
──────────────────────────────
  총 파일: 2개
  성공: 2개
  저장 위치: /tmp/sdd-workspaces/REQ-001/normalized
──────────────────────────────
```

## 에러 처리

- **디렉터리 없음**: `/tmp/sdd-workspaces/REQ-001/input` 디렉터리 확인 메시지
- **빈 디렉터리**: 정규화할 파일이 없음 알림
- **변환 실패**: 각 파일별 실패 원인 표시

## 다음 단계

문서 정규화 완료 후:
1. `/sdd-specify` 실행 (Speckit Specify)
2. `/sdd-plan` 실행 (Speckit Plan)
3. `/sdd-tasks` 실행 (Speckit Tasks)
