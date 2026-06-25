# SDD Specify Skill

정규화된 문서를 기반으로 요구사항을 체계화합니다.

## 사용법

```
/sdd-specify
```

## 입력 파라미터

| 파라미터 | 설명 | 필수 | 예시 |
|---------|------|------|------|
| run_id | 실행 ID 또는 경로 | ✅ | REQ-001 또는 /tmp/sdd-workspaces/REQ-001 |

## 예시

```
Run ID: /tmp/sdd-workspaces/REQ-001
```

또는

```
Run ID: REQ-001
```

## 동작

1. 정규화된 Markdown 파일 로드
2. Claude Speckit `/specify` 명령 자동 실행
3. 요구사항 추출 및 분류 (기능/비기능/보안/연계)
4. 유스케이스와 테스트케이스 연결
5. 생성 파일 저장

## 생성 파일

| 파일 | 내용 |
|------|------|
| **requirements.md** | 요구사항 정의 (REQ-FN-001, REQ-NF-001 등) |
| **spec.md** | 상세 명세 (시스템 아키텍처, 컴포넌트 설계) |
| **edge_cases.md** | 모호한 항목 및 확인 질문 |

## 출력

```
✅ Specify 실행 완료
생성된 파일: 3개
  - requirements.md
  - spec.md
  - edge_cases.md
```

## 다음 단계

1. Edge Case 검토 및 보완
2. `/sdd-plan` 실행 (설계 계획)
3. `/sdd-tasks` 실행 (작업 분해)
