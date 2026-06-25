# SDD Plan Skill

요구사항을 기반으로 구현 계획 및 설계 문서를 생성합니다.

## 사용법

```
/sdd-plan
```

## 입력 파라미터

| 파라미터 | 설명 | 필수 | 예시 |
|---------|------|------|------|
| run_id | 실행 ID 또는 경로 | ✅ | /tmp/sdd-workspaces/REQ-001 |

## 생성 파일

| 파일 | 내용 |
|------|------|
| **plan.md** | Phase별 구현 계획 및 일정 |
| **component_spec.md** | Controller/Service/DAO/Mapper 설계 |
| **data_model.md** | 테이블 정의 및 ERD |
| **TDD.md** | 테스트 전략 및 테스트 케이스 |

## 출력

```
✅ Plan 실행 완료
생성된 파일: 4개
```

## 다음 단계

작업 분해:
```
/sdd-tasks
```
