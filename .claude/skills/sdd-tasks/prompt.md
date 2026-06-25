# SDD Tasks Skill — Prompt Logic

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
python scripts/confluence/speckit_runner.py run_tasks --run_id <경로>
```

### 파라미터
- `--run_id`: Workspace 경로 (필수)

## 생성 파일

Tasks 실행 후 생성되는 파일:

1. **tasks.md**
   - Story별 분해 (Story 1-N)
   - Sub-task 나열 (T001, T002, ...)
   - 각 Sub-task별 담당자, 일정, 우선순위
   - Task 상세 설명

## 작업 구조

```
Story 1: 사용자 목록 조회
├── T001: Controller 작성
├── T002: Service 인터페이스 정의
├── T003: ServiceImpl 구현
├── T004: DAO 인터페이스 정의
├── T005: Mapper XML 작성
├── T006: SQL 쿼리 검증
├── T007: 페이징 기능 추가
├── T008: 단위 테스트 작성
└── T009: 통합 테스트

Story 2: 사용자 등록
└── T010~T018 (9개 Sub-task)
```

## 에러 처리

### 경로 없음
```
Error: Run ID 또는 경로를 입력해주세요
```

### Plan 문서 없음
```
Error: plan.md를 찾을 수 없습니다
먼저 `/sdd-plan`을 실행해주세요
```

### Permission 에러
```
Error: 경로에 접근할 수 없습니다
권한을 확인해주세요
```

## 성공 응답

```
✅ Tasks 실행 완료

생성된 파일: 1개
└── tasks.md (3200 줄)
  ├── Story 1: 사용자 목록 조회 (9개 Sub-task)
  ├── Story 2: 사용자 등록 (9개 Sub-task)
  ├── Story 3: 사용자 수정 (9개 Sub-task)
  └── Story 4: 사용자 삭제 (6개 Sub-task)
  총 33개 Sub-task

저장 위치: /tmp/sdd-workspaces/REQ-001/specs/
```

## 다음 단계

생성된 tasks.md를 기반으로:
```
1. tasks.md 검토 (각 Task의 우선순위, 의존성)
2. 팀 회의: Sub-task 담당자 배정
3. 각 Task별 Branch 생성 (feature/T001-controller 등)
4. Task별 JUnit 테스트 작성 (TDD)
5. 구현 시작

권장 순서:
T001 (Controller) ← 기초
T002-T004 (Service, DAO) ← 비즈니스 로직
T005 (Mapper XML) ← 데이터 계층
T006-T007 (SQL, 페이징) ← 성능
T008-T009 (테스트) ← 검증
```

## 검증

사용자가 확인하도록 안내:
```
Task 검증 체크리스트:
- [ ] 모든 Story가 분해되었는가?
- [ ] 각 Sub-task에 의존성이 정의되었는가?
- [ ] 예상 일정이 현실적인가?
- [ ] 높은 위험 Task는 식별되었는가?
```
