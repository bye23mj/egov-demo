# GovProject AI Manager 개발을 위한 Jira · Confluence · Slack 사전작업 가이드

## 1. 전체 사전작업 요약

GovProject AI Manager 개발 전에 Jira, Confluence, Slack에서 먼저 준비해야 할 항목을 정리한다.

기본 역할 분리는 다음과 같다.

| 도구 | 역할 |
|---|---|
| Jira | 일정, 이슈, 산출물 작성 상태, 개발 진행 상태 관리 |
| Confluence | 공식 산출물 저장소, 보고서 저장소, AI Context 저장소 |
| Slack | 산출물 작성 요청, 지연 알림, 보고 검토 요청 |
| Claude | 문서 검토, 요구사항 분석, Context 생성, 보고서 초안 작성 |
| GovProject AI Manager | 전체 자동화 오케스트레이션 |

전체 준비 순서는 다음과 같다.

```text
1. Atlassian 조직/사이트 권한 확인
2. Jira 프로젝트 생성 및 이슈 유형/워크플로우 설정
3. Confluence Space 생성 및 문서 폴더구조 구성
4. Jira 프로젝트와 Confluence Space 연결
5. Jira Automation 설정
6. Slack Workspace와 Jira Cloud 앱 연결
7. Slack 채널 구성 및 알림 규칙 설정
8. API Token, Webhook, Bot 권한 준비
9. GovProject AI Manager 연동용 서비스 계정 생성
10. 테스트 프로젝트로 전체 흐름 검증
```

프로그램 개발 전에 Jira, Confluence, Slack의 운영 규칙을 먼저 고정해야 한다. 그래야 자동화 프로그램이 어떤 이슈를 만들고, 어떤 문서를 생성하고, 누구에게 알림을 보내야 하는지 명확해진다.

---

# 2. Jira 사전작업

## 2.1 Jira 프로젝트 생성 방식 결정

Jira Cloud 기준으로 프로젝트 유형은 보통 아래 중 하나를 선택한다.

| 구분 | 설명 | 추천 여부 |
|---|---|---|
| Team-managed project | 팀 단위로 빠르게 설정 가능 | 소규모 파일럿에 적합 |
| Company-managed project | 관리자 중심으로 워크플로우, 권한, 필드, 화면을 표준화 가능 | 회사 표준 정부프로젝트 관리에 추천 |

정부프로젝트 관리프로그램은 여러 프로젝트에 동일한 산출물, 일정, 상태 규칙을 적용해야 하므로 **Company-managed project**를 권장한다.

---

## 2.2 Jira 프로젝트 기본 설정

### 생성 예시

```text
Project name: ○○기관 차세대 업무시스템 구축
Project key: GOVPJT
Template: Scrum 또는 Kanban
Project type: Company-managed
Lead: PM
Default assignee: Unassigned 또는 Project Lead
```

### 템플릿 선택 기준

| 프로젝트 성격 | Jira Template |
|---|---|
| 애자일 Sprint 중심 개발 | Scrum |
| 산출물·단계·승인 중심 관리 | Kanban |
| 전자정부 SI 표준 산출물 관리 | Kanban + Roadmap 또는 Timeline |

정부기관 프로젝트는 산출물, 단계, 승인 중심 관리가 중요하므로 **Kanban 기반 관리**를 우선 추천한다. 개발팀이 스프린트 방식으로 운영한다면 Scrum을 사용한다.

---

# 3. Jira Issue Type 설정

GovProject AI Manager에서 자동으로 생성·관리할 수 있도록 Issue Type을 먼저 표준화한다.

## 3.1 권장 Issue Type

| Issue Type | 용도 |
|---|---|
| Epic | 프로젝트 단계 또는 업무영역 |
| Phase | 착수, 요구사항, 설계, 개발, 테스트 등 단계 |
| Deliverable | 산출물 작성 작업 |
| Requirement | 요구사항 |
| Use Case | 유스케이스 |
| Story | 개발 단위 |
| Task | 일반 작업 |
| Bug | 결함 |
| Change Request | 변경요청 |
| Review | 문서/코드/고객 리뷰 |
| Report | 주간보고, 월간보고 |
| Release | 배포 |
| Risk | 위험 |
| Decision | 주요 의사결정 |

---

## 3.2 Issue Type Scheme 구성

프로젝트별로 동일한 Issue Type을 쓰려면 **Issue Type Scheme**을 만들어 회사 표준으로 관리한다.

```text
Scheme name: GOV Standard Issue Type Scheme

포함 Issue Type:
- Epic
- Phase
- Deliverable
- Requirement
- Use Case
- Story
- Task
- Bug
- Change Request
- Review
- Report
- Release
- Risk
- Decision
```

---

# 4. Jira Workflow 설정

GovProject AI Manager는 Jira 상태를 기준으로 산출물 작성 요청, 문서 변환, Claude 검토, 보고서 생성을 자동 실행한다. 따라서 Workflow 설계가 가장 중요하다.

---

## 4.1 산출물 Workflow

대상 Issue Type:

```text
Deliverable
Review
Report
```

권장 상태:

```text
작성대기
→ 작성요청
→ 작성중
→ 내부검토
→ 보완요청
→ 고객검토
→ 승인
→ 기준선등록
```

### 상태별 의미

| 상태 | 의미 | 자동화 |
|---|---|---|
| 작성대기 | 아직 작성 요청 전 | 일정 도래 대기 |
| 작성요청 | 담당자에게 작성 요청 완료 | Slack 작성 요청 발송 |
| 작성중 | 담당자가 문서 작성 중 | 기한 추적 |
| 내부검토 | PM/PL 검토 단계 | Slack 검토 요청 |
| 보완요청 | 수정 필요 | 담당자에게 재요청 |
| 고객검토 | 고객 또는 발주기관 검토 | 고객검토 이력 기록 |
| 승인 | 공식 승인 | Confluence 승인 상태 반영 |
| 기준선등록 | 변경관리 대상 전환 | 이후 변경은 Change Request 처리 |

---

## 4.2 개발 Workflow

대상 Issue Type:

```text
Requirement
Use Case
Story
Task
Bug
Change Request
```

권장 상태:

```text
Backlog
→ 요구사항확인
→ 설계중
→ 개발중
→ 코드리뷰
→ 단위테스트
→ 통합테스트
→ 배포대기
→ 배포완료
→ 종료
```

### 상태별 자동 참조 문서

| Jira 상태 | 자동 참조 문서 | Claude Context |
|---|---|---|
| 요구사항확인 | 요구사항정의서, 회의록, 요구사항추적표 | 요구사항 검토 Context |
| 설계중 | 유스케이스명세서, 화면설계서, API설계서, DB설계서 | 설계 검토 Context |
| 개발중 | 상세설계서, 프로그램설계서, 표준코딩가이드 | 개발 Context |
| 단위테스트 | 단위테스트케이스, 요구사항추적표 | 단위테스트 Context |
| 통합테스트 | 통합테스트시나리오, 인터페이스설계서 | 통합테스트 Context |
| 배포대기 | 배포계획서, 운영전환계획서 | 배포점검 Context |

---

## 4.3 보고 Workflow

대상 Issue Type:

```text
Report
```

권장 상태:

```text
작성예정
→ 작성요청
→ 초안작성
→ PM검토
→ 보완
→ 제출완료
```

보고 항목은 별도 Issue Type으로 두는 것이 좋다. 그래야 주간보고와 월간보고를 Jira 일정, 문서, Slack 알림과 연결하기 쉽다.

---

# 5. Jira Custom Field 설정

GovProject AI Manager 연동을 위해 다음 필드를 권장한다.

| 필드명 | 타입 | 용도 |
|---|---|---|
| Project Phase | Select | 착수, 현황분석, 요구사항, 분석, 설계, 구현, 테스트, 운영전환, 검수 |
| Deliverable Type | Select | 요구사항정의서, 화면설계서, API설계서 등 |
| Requirement ID | Text | REQ-FN-001 등 |
| Use Case ID | Text | UC-001 등 |
| Screen ID | Text | SCR-001 등 |
| API ID | Text | API-001 등 |
| Program ID | Text | PGM-001 등 |
| Test Case ID | Text | TC-001 등 |
| Confluence Page URL | URL | 공식 문서 링크 |
| Markdown Context URL | URL | 변환된 AI Context 링크 |
| Document Owner | User Picker | 산출물 작성자 |
| Reviewer | User Picker | 검토자 |
| Approval Status | Select | 작성중, 검토중, 승인 등 |
| Due Date | Date | 산출물 기한 |
| Report Period | Text | 2026-W23, 2026-06 |
| Slack Channel | Text | 알림 채널 |
| Claude Review Status | Select | 미검토, 검토완료, 보완필요 |
| Baseline Version | Text | 기준선 버전 |

이 필드들은 요구사항부터 검수까지의 추적성을 유지하기 위한 핵심 필드다.

```text
요구사항 ID
→ 유스케이스 ID
→ 화면 ID
→ API ID
→ 프로그램 ID
→ 테스트케이스 ID
→ 검수 승인 ID
```

---

# 6. Jira Components / Versions 설정

## 6.1 Components

권장 Component:

```text
사업관리
현황분석
요구사항
분석
설계
개발
테스트
감리_보안_품질
운영전환
검수_종료
보고
AI_Context
공통
인프라
연계
보안
```

## 6.2 Versions

릴리즈와 검수 단계를 추적하기 위해 Version을 설정한다.

```text
v0.1_착수
v0.2_요구사항기준선
v0.3_기본설계기준선
v0.4_상세설계기준선
v1.0_개발완료
v1.1_통합테스트
v1.2_UAT
v1.3_운영전환
v2.0_검수완료
```

---

# 7. Jira Permission / Role 설정

권한은 자동화 프로그램이 정상 동작하면서도 문서·이슈를 과도하게 수정하지 못하도록 분리해야 한다.

## 7.1 권장 Project Role

| Role | 권한 |
|---|---|
| Project Admin | 프로젝트 설정 관리 |
| PM | 전체 이슈/산출물 관리 |
| PL | 설계/개발/테스트 관리 |
| Analyst | 요구사항/분석 산출물 작성 |
| Developer | 개발 이슈, 코드리뷰, 단위테스트 |
| QA | 테스트케이스, 결함관리 |
| Document Owner | 산출물 작성 |
| Reviewer | 산출물 검토 |
| Viewer | 조회 |
| Automation Bot | 이슈 생성, 댓글 작성, 상태 변경, 링크 추가 |

## 7.2 Automation Bot 권장 권한

GovProject AI Manager용 서비스 계정 또는 API 계정에는 다음 권한이 필요하다.

```text
Browse Projects
Create Issues
Edit Issues
Transition Issues
Add Comments
Link Issues
Assign Issues
Manage Watchers
View Development Tools
```

관리자 권한은 최소화한다. Bot 계정이 프로젝트 전체 설정을 바꾸지 않도록, 프로젝트 운영 자동화에 필요한 권한만 부여한다.

---

# 8. Jira Automation 설정

## 8.1 산출물 작성 요청 자동화

### Trigger

```text
Scheduled: 매일 09:00
```

### Condition

```text
Project Phase 시작일 = 오늘
또는 Due Date - 3일
```

### Action

```text
1. Deliverable 이슈 생성
2. 담당자 Assign
3. Confluence Page Link 추가
4. Slack Webhook 호출
```

---

## 8.2 상태 변경 시 Slack 알림

### Trigger

```text
Issue transitioned
```

### Condition

```text
Issue Type = Deliverable
Status = 작성요청 또는 보완요청 또는 승인
```

### Action

```text
Slack 메시지 발송
Jira Comment 추가
```

---

## 8.3 승인 완료 시 기준선 등록

### Trigger

```text
Issue transitioned to 승인
```

### Action

```text
1. Confluence 문서 상태를 승인으로 표시
2. Markdown 변환 요청
3. Claude Context 생성 요청
4. Jira 상태를 기준선등록으로 전환
```

---

# 9. Confluence 사전작업

## 9.1 Space 생성

프로젝트별 Space를 만들거나, 회사 공통 Space 아래 프로젝트 Root Page를 만드는 방식을 선택한다.

| 방식 | 장점 | 단점 | 추천 |
|---|---|---|---|
| 프로젝트별 Space | 권한 분리, 검색 분리, 관리 명확 | Space가 많아짐 | 대형 정부사업 추천 |
| 공통 Space + 프로젝트 Root Page | 관리 단순 | 권한 분리 어려움 | 소형 프로젝트 추천 |

정부기관 프로젝트는 산출물과 권한이 중요하므로 **프로젝트별 Space**를 권장한다.

예시:

```text
Space name: ○○기관 차세대 업무시스템 구축
Space key: GOVPJT
```

---

## 9.2 Confluence 문서 폴더구조 생성

Confluence는 실제 파일시스템 폴더가 아니라 **Page Tree 구조**로 관리한다. 프로젝트 생성 시 아래 Page Tree를 자동 생성한다.

```text
프로젝트명
├─ 00_사업관리
├─ 01_현황분석
├─ 02_요구사항
├─ 03_분석
├─ 04_설계
├─ 05_개발
├─ 06_테스트
├─ 07_감리_보안_품질
├─ 08_운영전환
├─ 09_검수_종료
├─ 10_보고
└─ 99_AI_Context
```

상세 구조:

```text
10_보고
├─ 주간보고
└─ 월간보고

99_AI_Context
├─ requirements
├─ analysis
├─ design
├─ development
├─ test
├─ integration-test
├─ deployment
├─ weekly-report
└─ monthly-report
```

---

# 10. Confluence 페이지 템플릿 준비

자동 생성할 문서는 템플릿화해야 한다.

## 10.1 필수 템플릿

| 템플릿 | 용도 |
|---|---|
| 사업수행계획서 Template | 착수 단계 |
| 회의록 Template | 고객 인터뷰, 정기회의 |
| 요구사항정의서 Template | 요구사항 도출 |
| 요구사항추적표 Template | 추적성 관리 |
| 유스케이스명세서 Template | 분석 단계 |
| 화면설계서 Template | 설계 단계 |
| API설계서 Template | 설계/개발 연계 |
| DB설계서 Template | 설계 단계 |
| 테스트계획서 Template | 테스트 단계 |
| 결함관리대장 Template | 테스트/품질 |
| 주간보고 Template | 매주 보고 |
| 월간보고 Template | 매월 보고 |
| Claude Context Template | AI 활용 |

## 10.2 공통 메타데이터 표준

모든 Confluence 문서 상단에 아래 표를 넣는 것을 권장한다.

```markdown
| 항목 | 값 |
|---|---|
| 프로젝트 | GOVPJT |
| 문서유형 | 요구사항정의서 |
| 단계 | 요구사항 정의 |
| 담당자 | 홍길동 |
| 검토자 | 김PM |
| 관련 Jira | GOVPJT-123 |
| 상태 | 작성중 |
| 기준선 버전 | v0.2 |
| 최종수정일 | 2026-06-06 |
```

---

# 11. Jira와 Confluence 연결 방법

## 11.1 기본 연결 절차

```text
1. Jira와 Confluence가 같은 Atlassian Cloud 사이트에 있는지 확인
2. Jira 프로젝트 생성
3. Confluence Space 생성
4. Jira 프로젝트의 왼쪽 메뉴에서 Pages / Docs / Project pages 메뉴 확인
5. 연결할 Confluence Space 선택
6. Jira 이슈에서 Confluence 페이지 링크 추가
7. Confluence 페이지에서 Jira Issue Macro 또는 Jira 링크 사용
```

---

## 11.2 Jira 이슈에서 Confluence 문서 연결

운영 방식:

```text
Jira Deliverable 이슈
→ Confluence 산출물 페이지 링크
→ 첨부 원본 문서
→ Markdown 변환본
→ Claude Context 페이지
```

예시:

| Jira 이슈 | 연결 문서 |
|---|---|
| GOVPJT-101 요구사항정의서 작성 | 02_요구사항/요구사항정의서 |
| GOVPJT-102 요구사항추적표 작성 | 02_요구사항/요구사항추적표 |
| GOVPJT-201 화면설계서 작성 | 04_설계/화면설계서 |
| GOVPJT-301 테스트계획서 작성 | 06_테스트/테스트계획서 |
| GOVPJT-901 주간보고 작성 | 10_보고/주간보고/2026-W23_주간보고 |

---

# 12. Confluence 문서 자동 생성 방법

## 12.1 수동 방식

초기에는 PM 또는 관리자가 직접 Page Tree를 생성할 수 있다.

```text
Confluence Space 접속
→ Create
→ Page 생성
→ 상위/하위 페이지 구성
→ 템플릿 적용
→ Jira 링크 삽입
```

## 12.2 자동 방식

GovProject AI Manager에서 Confluence REST API를 사용해 자동 생성한다.

자동 생성 대상:

```text
1. Space 생성 또는 프로젝트 Root Page 생성
2. 00_사업관리 ~ 99_AI_Context 페이지 생성
3. 각 단계별 산출물 페이지 생성
4. 주간보고/월간보고 하위 페이지 생성
5. Jira 이슈 링크 삽입
6. 담당자/상태/기한 메타데이터 삽입
```

---

# 13. Confluence 권한 설정

## 13.1 권장 권한 그룹

| 그룹 | 권한 |
|---|---|
| project-admins | 전체 관리 |
| project-pm | 문서 생성, 수정, 승인 |
| project-pl | 설계/개발 문서 수정 |
| project-analysts | 요구사항/분석 문서 수정 |
| project-developers | 개발/테스트 문서 수정 |
| project-qa | 테스트/결함 문서 수정 |
| project-viewers | 조회 |
| automation-bot | 페이지 생성, 수정, 첨부파일 조회, 댓글 작성 |

## 13.2 문서 승인 정책

Confluence 자체 승인 기능이 부족한 경우, Jira 상태를 승인 기준으로 삼는다.

```text
Confluence 문서 작성
→ Jira Deliverable 상태 = 내부검토
→ PM 검토
→ Jira 상태 = 승인
→ 시스템이 Confluence 문서 상단 상태를 승인으로 갱신
→ Markdown 변환
→ 기준선 등록
```

---

# 14. Slack 사전작업

## 14.1 Slack 앱 설치

Jira Cloud for Slack 앱을 설치한다.

설치 순서:

```text
1. Slack Workspace 관리자 권한 확인
2. Slack App Directory에서 Jira Cloud 검색
3. Jira Cloud 앱 설치
4. Atlassian 사이트 선택
5. Jira 계정 인증
6. Slack 채널과 Jira 프로젝트 연결
7. 알림 이벤트 선택
8. 테스트 이슈 생성 후 Slack 알림 확인
```

---

# 15. Jira에서 Slack 사용하는 법

## 15.1 Slack 채널과 Jira 프로젝트 연결

Slack 채널에서 다음 명령을 사용한다.

```text
/jira connect
```

흐름:

```text
Slack 채널 접속
→ /jira connect 입력
→ Atlassian 사이트 선택
→ Jira 프로젝트 선택
→ 알림 받을 이벤트 선택
→ 연결 완료
```

## 15.2 개인 알림 설정

```text
/jira notify
```

## 15.3 도움말 확인

```text
/jira help
```

---

# 16. Slack 채널 구성

프로젝트별로 아래 채널을 생성한다.

```text
#govpjt-announcement
#govpjt-doc-request
#govpjt-requirements
#govpjt-design
#govpjt-dev
#govpjt-test
#govpjt-release
#govpjt-report
#govpjt-risk-issue
#govpjt-ai-context
```

## 16.1 채널별 용도

| 채널 | 용도 |
|---|---|
| `#govpjt-announcement` | 공식 공지 |
| `#govpjt-doc-request` | 산출물 작성 요청 |
| `#govpjt-requirements` | 요구사항 논의 |
| `#govpjt-design` | 설계 검토 |
| `#govpjt-dev` | 개발 진행 |
| `#govpjt-test` | 테스트/결함 |
| `#govpjt-release` | 배포 |
| `#govpjt-report` | 주간보고/월간보고 |
| `#govpjt-risk-issue` | 위험/이슈 |
| `#govpjt-ai-context` | Markdown 변환, Claude Context 생성 알림 |

---

# 17. Slack 알림 이벤트 설정

## 17.1 Jira Cloud 앱 알림

채널별로 다음 이벤트를 구독한다.

| 채널 | Jira 이벤트 |
|---|---|
| `#govpjt-doc-request` | Deliverable 생성, 상태 변경, 기한 임박 |
| `#govpjt-requirements` | Requirement 생성/변경, 승인 요청 |
| `#govpjt-design` | 설계 관련 Issue 변경 |
| `#govpjt-dev` | Story/Task 개발중, 코드리뷰, 완료 |
| `#govpjt-test` | Bug 생성/변경, 테스트 이슈 |
| `#govpjt-release` | Release, 배포대기, 배포완료 |
| `#govpjt-report` | Report 생성, PM검토, 제출완료 |
| `#govpjt-risk-issue` | Risk, Issue, Change Request |

## 17.2 GovProject AI Manager 자체 알림

Jira Cloud 앱만으로 부족한 알림은 별도 Slack Bot 또는 Incoming Webhook으로 보낸다.

예:

```text
[산출물 작성 요청]
[산출물 지연 알림]
[Claude 검토 완료]
[문서 Markdown 변환 완료]
[주간보고 초안 생성]
[월간보고 초안 생성]
```

---

# 18. Slack에서 Jira 이슈 생성

Slack 메시지 또는 스레드에서 Jira 이슈를 생성할 수 있다.

운영 예:

```text
Slack에서 고객 이슈 논의
→ 메시지 More actions
→ Create work item from Jira Cloud
→ Project = GOVPJT
→ Issue Type = Change Request 또는 Bug
→ 생성
→ Jira 이슈 링크가 Slack 스레드에 남음
```

---

# 19. Slack 메시지 작성 규칙

자동화를 위해 Slack 메시지 형식을 표준화한다.

## 19.1 산출물 작성 요청

```text
[산출물 작성 요청]
프로젝트:
단계:
문서:
담당자:
기한:
Confluence:
Jira:
요청사항:
```

## 19.2 이슈 등록 요청

```text
[이슈 등록]
프로젝트:
유형: Bug / Risk / Change Request
내용:
영향도:
긴급도:
관련 문서:
관련 Jira:
```

## 19.3 회의 결정사항

```text
[결정사항]
일시:
회의명:
결정 내용:
결정자:
관련 요구사항:
관련 Jira:
후속 작업:
```

이 형식을 지키면 Claude나 자동화 프로그램이 Slack 내용을 구조화하기 쉬워진다.

---

# 20. 서비스 계정 및 API Token 준비

GovProject AI Manager 연동을 위해 별도 서비스 계정을 준비한다.

## 20.1 Atlassian 서비스 계정

```text
계정명: govproject-bot@company.com
용도:
- Jira 이슈 생성/수정
- Jira 댓글 작성
- Confluence 페이지 생성/수정
- Confluence 첨부파일 조회
- Automation 실행 로그 기록
```

## 20.2 Slack Bot 계정

```text
Bot name: GovProject Bot
권한:
- channels:read
- chat:write
- chat:write.public
- users:read
- groups:read
- im:write
- incoming-webhook
```

실제 Slack 앱 권한은 회사 보안 정책과 Slack 앱 심사 기준에 맞춰 최소 권한으로 설정한다.

---

# 21. 프로젝트 생성 전 체크리스트

## 21.1 Jira 체크리스트

```text
[ ] Jira Company-managed 프로젝트 생성
[ ] Issue Type Scheme 생성
[ ] Workflow Scheme 생성
[ ] 산출물 Workflow 생성
[ ] 개발 Workflow 생성
[ ] 보고 Workflow 생성
[ ] Custom Field 생성
[ ] Screen Scheme에 Custom Field 배치
[ ] Permission Scheme 설정
[ ] Project Role 설정
[ ] Automation Bot 권한 부여
[ ] Components 생성
[ ] Versions 생성
[ ] Jira Automation 기본 Rule 생성
```

## 21.2 Confluence 체크리스트

```text
[ ] 프로젝트 Space 생성
[ ] 00_사업관리 ~ 99_AI_Context Page Tree 생성
[ ] 10_보고/주간보고 생성
[ ] 10_보고/월간보고 생성
[ ] 산출물 템플릿 등록
[ ] 주간보고 템플릿 등록
[ ] 월간보고 템플릿 등록
[ ] 문서 상단 메타데이터 표준 적용
[ ] Jira Issue Macro 사용 확인
[ ] Automation Bot 페이지 생성/수정 권한 부여
[ ] 첨부파일 권한 확인
```

## 21.3 Slack 체크리스트

```text
[ ] Jira Cloud for Slack 앱 설치
[ ] 프로젝트별 Slack 채널 생성
[ ] /jira connect로 Jira 프로젝트 연결
[ ] /jira notify 개인 알림 설정
[ ] 채널별 Jira 이벤트 구독 설정
[ ] GovProject Bot 앱 생성
[ ] Incoming Webhook 설정
[ ] 산출물 작성 요청 메시지 테스트
[ ] 지연 알림 테스트
[ ] 주간보고 초안 생성 알림 테스트
```

## 21.4 연동 체크리스트

```text
[ ] Jira 이슈에서 Confluence 문서 링크 열림
[ ] Confluence 문서에서 Jira 이슈 표시 가능
[ ] Slack에서 Jira 이슈 키 입력 시 미리보기 표시
[ ] Slack에서 Jira 이슈 생성 가능
[ ] Jira 상태 변경 시 Slack 알림 수신
[ ] Confluence 문서 변경 감지 가능
[ ] 문서 첨부파일 다운로드 가능
[ ] Markdown 변환 결과 저장 가능
[ ] Claude Context 생성 가능
[ ] 주간보고 자동 생성 가능
[ ] 월간보고 자동 요약 가능
```

---

# 22. 추천 초기 구축 순서

가장 안정적인 순서는 아래와 같다.

```text
1. Jira 표준 Issue Type / Workflow / Field 확정
2. Confluence 문서구조와 산출물 템플릿 확정
3. Slack 채널과 알림 규칙 확정
4. Jira ↔ Confluence 연결 테스트
5. Jira ↔ Slack 연결 테스트
6. Confluence 첨부파일 수집 테스트
7. Markdown 변환 테스트
8. Claude Context 생성 테스트
9. 주간보고 생성 테스트
10. 월간보고 생성 테스트
```

---

# 23. 실제 운영 예시

## 23.1 요구사항 단계

```text
1. Jira Phase = 요구사항 정의 시작
2. 시스템이 Deliverable 이슈 생성
   - 요구사항정의서
   - 요구사항추적표
   - 요구사항승인서
3. Slack으로 분석가에게 작성 요청
4. 분석가가 Confluence에 문서 작성
5. 시스템이 문서 변경 감지
6. Markdown 변환
7. Claude가 요구사항 누락/모호성 검토
8. PM에게 검토 결과 Slack 알림
9. 승인 후 기준선 등록
```

## 23.2 주간보고

```text
1. 매주 금요일 10:00 배치 실행
2. Jira 이번 주 완료/진행/지연 이슈 조회
3. Confluence 이번 주 작성 문서 조회
4. Slack 주요 결정사항 수집
5. Claude가 주간보고 초안 생성
6. Confluence 10_보고/주간보고에 페이지 생성
7. PM에게 Slack 검토 요청
8. PM 수정 후 제출완료
```

## 23.3 월간보고

```text
1. 매월 마지막 영업일 10:00 배치 실행
2. 해당 월 주간보고 전체 조회
3. Jira 월간 완료/지연/결함/변경요청 통계 조회
4. Claude가 월간보고 초안 생성
5. Confluence 10_보고/월간보고에 페이지 생성
6. PM 검토 후 제출완료
```

---

# 24. 결론

프로그램 개발 전에 반드시 정리해야 할 것은 다음 세 가지다.

```text
1. Jira 표준
   - Issue Type
   - Workflow
   - Custom Field
   - Permission
   - Automation

2. Confluence 표준
   - Space 구조
   - 산출물 Page Tree
   - 문서 템플릿
   - Jira 링크 규칙
   - AI Context 저장 위치

3. Slack 표준
   - 채널 구조
   - Jira 연결
   - 알림 이벤트
   - 작성 요청 메시지 형식
   - Bot/Webhook 권한
```

이 사전작업이 완료되어야 GovProject AI Manager가 안정적으로 작동한다.

즉, **Jira에서 일정과 상태를 만들고, Confluence에서 문서 구조를 만들고, Slack에서 작성 요청과 알림 경로를 만든 뒤**, 그 위에 Claude 기반 문서 변환·검토·보고 자동화를 얹는 순서가 가장 안전하다.
