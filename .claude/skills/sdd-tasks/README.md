# SDD Tasks Skill

설계 문서를 기반으로 구현 작업을 분해합니다.

## 사용법

```
/sdd-tasks
```

## 입력 파라미터

| 파라미터 | 설명 | 필수 | 예시 |
|---------|------|------|------|
| run_id | 실행 ID 또는 경로 | ✅ | /tmp/sdd-workspaces/REQ-001 |

## 생성 파일

| 파일 | 내용 |
|------|------|
| **tasks.md** | Story별 Sub-task 분해 (T001~T009 등) |

## 출력

```
✅ Tasks 실행 완료
생성된 파일: 1개
  - tasks.md (총 15개 Sub-task)
```

## 구조

```
Story 1: 사용자 목록 조회
├── T001: 조회 API 작성 (UserController.list)
├── T002: Service 구현 (UserService.getList)
├── T003: DAO 쿼리 작성 (getUserList)
├── T004: Mapper 작성 (selectUserList)
├── T005: 단위 테스트 작성
├── T006: 페이징 기능 추가
├── T007: 정렬 기능 추가
├── T008: 통합 테스트
└── T009: 배포 및 검증

Story 2: 사용자 등록
└── T010~T018 (9개 Sub-task)
```

## 다음 단계

작업 실행:
```
git clone egov-template-portal
apply tasks.md to Spring MVC project
```
