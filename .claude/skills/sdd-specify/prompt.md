# SDD Specify Skill — Prompt Logic

## 파라미터 수집

### Step 1: Run ID 입력 요청
```
Run ID를 입력해주세요 (예: /tmp/sdd-workspaces/REQ-001 또는 REQ-001):
```

입력값 검증:
- 비어있지 않은지 확인
- 경로 또는 ID 형식 확인

### Step 2: 경로 구성
입력값이 `/tmp` 또는 `/`로 시작하면 그대로 사용.
그 외에는 기본 workspace 디렉토리에 추가:
```
{workspace_base}/{run_id}
```

기본 workspace: `/tmp/sdd-workspaces`

예시:
```
입력: REQ-001
→ 경로: /tmp/sdd-workspaces/REQ-001

입력: /tmp/sdd-workspaces/REQ-001
→ 경로: /tmp/sdd-workspaces/REQ-001
```

## Python 스크립트 실행

### 호출
```bash
python scripts/confluence/speckit_runner.py run_specify --run_id <경로>
```

### 파라미터
- `--run_id`: Workspace 경로 (필수)

## 생성 파일

Specify 실행 후 생성되는 파일들:

1. **requirements.md**
   - 요구사항 정의 (REQ-FN-001, REQ-NF-001 등)
   - 각 요구사항의 설명, 우선순위, 상태
   - 요구사항별 테스트 케이스 매핑

2. **spec.md**
   - 시스템 전체 구조
   - 주요 컴포넌트 설계 (Controller, Service, DAO)
   - 데이터 흐름 다이어그램
   - API 스펙

3. **edge_cases.md**
   - 모호한 항목 나열
   - 추가 확인이 필요한 질문
   - 위험 요소 및 미결정 사항

## 에러 처리

### 경로 없음
```
Error: Run ID 또는 경로를 입력해주세요
```

### Normalized 문서 없음
```
Error: normalized/ 디렉토리를 찾을 수 없습니다
먼저 `/sdd-normalize`를 실행해주세요

단계:
1. /sdd-collect 실행 → input/ 생성
2. /sdd-normalize 실행 → normalized/ 생성
3. /sdd-specify 실행
```

### Permission 에러
```
Error: 경로에 접근할 수 없습니다
권한을 확인해주세요
```

## 성공 응답

```
✅ Specify 실행 완료

생성된 파일: 3개
├── requirements.md (정의된 요구사항 30개)
├── spec.md (2400 줄)
└── edge_cases.md (명확하지 않은 항목 12개)

저장 위치: /tmp/sdd-workspaces/REQ-001/specs/
```

## 다음 단계

각 파일별 작업:

### requirements.md 검토
```
- [ ] 기능 요구사항 (REQ-FN-*) 모두 포함?
- [ ] 비기능 요구사항 (REQ-NF-*) 포함?
- [ ] 보안 요구사항 (REQ-SEC-*) 포함?
- [ ] 각 요구사항의 우선순위 명확?
```

### spec.md 검토
```
- [ ] 시스템 아키텍처 이해?
- [ ] API 스펙 완전?
- [ ] 데이터 모델 올바름?
- [ ] 통합 포인트 명확?
```

### edge_cases.md 검토 및 처리
```
1. 각 edge case 검토
2. 비즈니스 의사결정 또는 추가 정보 수집
3. requirements.md에 반영
```

### Plan 생성
```
Edge case 처리 후:
/sdd-plan
```

## 검증

생성된 문서의 일관성 확인:
```
1. requirements.md의 모든 요구사항이 spec.md에 반영되었는가?
2. spec.md의 컴포넌트가 실제 구현 가능한가?
3. edge_cases.md의 모든 항목이 해결되었는가?
```
