# SDD Plan Skill — Prompt Logic

## 파라미터 수집

### Step 1: Run ID 입력 요청
```
Run ID를 입력해주세요 (예: /tmp/sdd-workspaces/REQ-001):
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

## Python 스크립트 실행

### 호출
```bash
python scripts/confluence/speckit_runner.py run_plan --run_id <경로>
```

### 파라미터
- `--run_id`: Workspace 경로 (필수)

## 생성 파일

Plan 실행 후 생성되는 파일들:

1. **plan.md**
   - Phase별 일정 (Phase 1-5)
   - Story 분해 (Story 1-N)
   - 마일스톤

2. **component_spec.md**
   - Controller 클래스 설계
   - Service/ServiceImpl 설계
   - DAO/Mapper 설계
   - VO 정의

3. **data_model.md**
   - 테이블 정의 (CREATE TABLE)
   - 컬럼 정의 (데이터타입, 제약조건)
   - Sequence 정의
   - Index 정의

4. **TDD.md**
   - 테스트 전략
   - Unit Test (JUnit 5)
   - Integration Test (Oracle 11g)
   - 테스트 케이스 매트릭스

## 에러 처리

### 경로 없음
```
Error: Run ID 또는 경로를 입력해주세요
```

### Normalized 문서 없음
```
Error: normalized/ 디렉토리를 찾을 수 없습니다
먼저 `/sdd-normalize`를 실행해주세요
```

### Permission 에러
```
Error: 경로에 접근할 수 없습니다
권한을 확인해주세요
```

## 성공 응답

```
✅ Plan 실행 완료

생성된 파일: 4개
├── plan.md (2500 줄)
├── component_spec.md (1800 줄)
├── data_model.md (1200 줄)
└── TDD.md (1500 줄)

저장 위치: /tmp/sdd-workspaces/REQ-001/specs/
```

## 검증

사용자가 생성된 파일들을 확인하도록 안내:
```
Edge Case 검토:
1. plan.md에서 Phase별 일정 확인
2. component_spec.md에서 계층 구조 검증
3. data_model.md에서 ERD 확인
4. TDD.md에서 테스트 범위 검증
```
