# [요구사항 상세화] GovProject AI Manager 솔루션

> Gemini를 통한 Brainstorming 검증 및 보완 결과
> 작성일: 2026-06-06

---

## 1. 기능 요구사항

### 1.1 Jira 통합 (Jira Integration)
- **REQ-101: 정부기관 표준 프로젝트 템플릿 자동 구성**
  - 신규 프로젝트 생성 시 정부 표준 산출물 단계(분석, 설계, 구현, 시험, 검수)가 반영된 Issue Type 및 Workflow를 자동 설정한다.
  
- **REQ-102: 산출물 연동 커스텀 필드 구성**
  - 각 Task에 '산출물 매핑 ID', '검토 상태', 'HWP 변환 필요 여부' 등의 메타데이터 필드를 자동 추가한다.

### 1.2 Confluence 통합 (Confluence Integration)
- **REQ-201: 표준 산출물 페이지 트리 자동 생성**
  - 프로젝트 승인 시 분석~종료 단계까지의 전체 페이지 구조(Page Tree)를 템플릿 기반으로 자동 생성한다.
  
- **REQ-202: 동적 문서 인덱싱 및 대시보드**
  - Jira 이슈 상태와 동기화된 산출물 작성 현황판을 Confluence 메인 페이지에 구성한다.

### 1.3 Slack 통합 (Slack Integration)
- **REQ-301: 워크플로우 기반 지능형 알림**
  - 단순 변경 알림이 아닌, '기한 2일 전 미작성', '검토 반려' 등 액션이 필요한 시점에만 타겟팅된 알림을 전송한다.
  
- **REQ-302: Slack Slash Command를 통한 요약 보고**
  - `/gov-status` 명령 시 현재 전체 진척률 및 금주 지연 항목 요약을 즉시 응답한다.

### 1.4 자동화 및 AI (Automation & AI)
- **REQ-401: Confluence to Markdown 변환 및 Git 동기화**
  - Confluence 문서를 Markdown으로 변환하여 기술 문서의 버전 관리를 수행한다.
  
- **REQ-402: Claude AI 기반 산출물 품질 검토**
  - 작성된 문서를 Claude API로 전달하여 '용어 표준 준수', '누락된 목차', '논리적 오류'를 검토하고 리포트를 생성한다.
  
- **REQ-403: 주간/월간 보고서 초안(Draft) 자동 생성**
  - 해당 기간 내 완료된 Jira 이슈와 Confluence 업데이트 내역을 취합하여 보고서 양식으로 자동 빌드한다.

---

## 2. 수용조건 (Given-When-Then)

### AC-001: 프로젝트 초기화 자동화
```
Given: 프로젝트명과 PM 정보가 입력됨
When: 초기화 스크립트 실행
Then: Jira 프로젝트 생성(표준 Workflow 적용) 및 Confluence 공간/표준 트리 생성 완료
```

### AC-002: 기한 임박 산출물 지능형 알림
```
Given: 마감 기한이 48시간 남은 '미완료' 상태의 산출물 Task 존재
When: 일일 배치 스케줄러 작동
Then: 담당자에게 Slack DM으로 해당 이슈 링크와 함께 "작성 독려" 알림 발송
```

### AC-003: Claude AI 산출물 검수 프로세스
```
Given: Confluence 페이지 상태가 '검토요청'으로 변경됨
When: Webhook에 의해 AI 검토 모듈 호출
Then: 60초 이내에 Claude의 검토 의견이 해당 페이지 하단 댓글 또는 Slack으로 전달됨
```

### AC-004: 보고서 자동 취합
```
Given: 금주 월~금 사이 종료된 이슈 15개, 신규 이슈 5개 존재
When: 주간보고 생성 명령 호출
Then: 지정된 템플릿(Markdown/Wiki)에 데이터가 매핑된 보고서 초안이 생성됨
```

---

## 3. 미확정 질문에 대한 권장 답변

| 질문 항목 | 실무 기반 권장 답변 |
|---|---|
| **Q1. Markdown 변환 포맷 유지 수준** | 테이블 및 코드블록은 100% 유지를 목표로 함. 다이어그램은 Mermaid.js 포맷으로 변환하거나 이미지 렌더링 후 링크 삽입 방안 권장. |
| **Q2. 변환 결과 저장 위치** | **Confluence가 Single Source of Truth**. 로컬/Git은 '백업 및 검토용'으로 활용하며, AI 검토 결과도 Confluence 댓글로 기록 권장. |
| **Q3. Jira Automation 수준** | 단순 상태 변경은 Jira Native Automation을 사용하고, 복잡한 데이터 가공 및 외부 API(Claude) 호출은 별도 Middleware(Node.js/Python) 구성 권장. |
| **Q4. 보고서 PM 수정 가능 여부** | **필수 사항**. 시스템은 '초안(Draft)'만 생성하고, PM이 Confluence 상에서 최종 내용을 수정/보완한 후 확정하는 워크플로우 채택. |
| **Q5. 보안 규정 준수 방식** | Atlassian Access 로그 분석 및 IP 화이트리스팅 필수. Claude API 호출 시 개인정보 및 기밀 키워드 마스킹(Masking) 처리 레이어 추가. |
| **Q6. 대규모 문서 처리 성능** | 50페이지 이상의 대규모 문서는 비동기(Async) 큐 방식으로 처리하며, 사용자에게 Slack으로 완료 알림을 전송하는 구조. |
| **Q7. 이슈-문서 간 동기화** | Jira 이슈 ID를 Confluence 페이지 메타데이터에 포함하여 양방향 추적성(Traceability) 확보. |
| **Q8. Claude API 모델 선택** | 문서 분석에는 컨텍스트 창이 큰 `Claude 3.5 Sonnet` 권장. 비용 효율성과 분석 정밀도의 균형이 가장 우수함. |

---

## 4. 누락된 기능 / 리스크 / 제약 사항

### 4.1 전자정부프레임워크(eGov) 환경 고려사항
- **산출물 최종 포맷**: 정부기관은 최종적으로 HWP(한글) 파일을 요구함. Markdown을 HWP로 변환하는 'Pandoc' 기반 파이프라인 또는 XML 조작을 통한 HWP 생성 자동화 검토 필요.
- **공공 클라우드 제약**: 고객사가 공공 클라우드(CSAP 인증) 환경일 경우 외부 API(Claude, Jira Cloud) 호출에 대한 망연계 구간 보안 심사 필요.

### 4.2 보안 고려사항
- **API Token 노출 위험**: Jira/Slack/Anthropic API Key를 환경변수나 Secret Manager(AWS Secrets Manager 등)에서 관리하고 주기적인 로테이션 필요.
- **데이터 프라이버시**: AI 모델 학습에 고객사 데이터가 사용되지 않도록 'Zero Data Retention' 옵션 확인 필수.

### 4.3 성능 및 안정성
- **API Rate Limit**: Atlassian Cloud의 API 호출 제한을 고려하여 지수 백오프(Exponential Backoff) 알고리즘 적용.
- **Webhook 유실 대응**: Webhook 실패 시 재시도 로직(Retry Logic) 및 Dead Letter Queue(DLQ) 구성.

---

## 5. 실무 체크리스트

### [Jira 설정]
- [ ] Issue Type Scheme: '정부산출물', '개발태스크', '결함' 구분
- [ ] Workflow: '대기 -> 작성중 -> 검토요청 -> 반려 -> 완료' 단계 구성
- [ ] Screen: '산출물 구분코드', '관련 법적 근거' 등 필수 필드 배치
- [ ] Components: '사업관리', '현황분석', '요구사항', '설계', '개발', '테스트' 등록
- [ ] Versions: 각 단계별 기준선(Baseline) 버전 정의

### [Confluence 설정]
- [ ] Space Blueprint: 단계별 페이지 템플릿(분석정의서, 설계서 등) 사전 등록
- [ ] Content Formatting Macros: 상태 바(Status Bar), 인라인 이슈 표시 설정
- [ ] Restricted Page: 기밀 문서(인프라 정보 등) 접근 제어 그룹 설정
- [ ] Page Hierarchies: 00_사업관리 ~ 99_AI_Context 폴더 구조 자동 생성
- [ ] 메타데이터 템플릿: 모든 문서 상단에 프로젝트, 문서유형, 담당자, 상태 자동 입력

### [Slack 설정]
- [ ] App Scopes: `chat:write`, `commands`, `incoming-webhook` 권한 확인
- [ ] Channel Architecture: `#pjt-알림`, `#pjt-보고`, `#pjt-긴급` 채널 분리
- [ ] Bot Token: Jira Cloud for Slack 앱 설치 및 설정
- [ ] Webhook: 보고서 자동 생성 시 Slack 채널에 알림 전송
- [ ] Custom Slash Commands: `/gov-status`, `/gov-weekly` 등 커스텀 명령어 등록

### [자동화 설정]
- [ ] Middleware 서버 (Node.js/Python) 배포 환경 확보
- [ ] Claude API Quota 및 결제 수단 확인
- [ ] CI/CD: Markdown 변환 후 Git Repository 자동 푸시 스크립트 검증
- [ ] Batch Scheduler: cron 또는 CI/CD 파이프라인으로 주간/월간 보고서 생성 스케줄 설정
- [ ] 모니터링: API 호출 실패, 변환 오류 등에 대한 알림 및 로깅 구성

---

## 6. 권장 개선 사항

### Priority 1 (필수)
1. **API Token 보안 관리**: Secret Manager 도입 (AWS Secrets, Vault 등)
2. **Markdown 변환 엔진**: Pandoc + 커스텀 후처리 스크립트
3. **Jira Middleware**: 복잡한 자동화를 위한 별도 서버 구성
4. **Claude API 마스킹**: 개인정보/기밀정보 자동 마스킹 레이어

### Priority 2 (권장)
5. **HWP 변환**: Pandoc + LibreOffice 조합으로 최종 산출물 생성
6. **비동기 처리**: 대규모 문서는 큐(Queue) 기반으로 처리
7. **감사 로그**: 모든 API 호출 및 문서 변경 로깅
8. **모니터링 대시보드**: Grafana/Datadog로 API 성능 추적

### Priority 3 (선택)
9. **다국어 지원**: 한글/영문 Markdown 변환 최적화
10. **고급 검색**: Confluence 문서 전문 검색(Full-text Search) 강화

---

## 7. 개발 일정 재검토

| Phase | 기존 기간 | 재검토 기간 | 변경사항 |
|---|---|---|---|
| **1. 사전작업 검증** | 1주 | **1.5주** | Jira/Confluence/Slack 고도화 시간 추가 |
| **2. 핵심 기능** | 3주 | **3주** | 변경 없음 |
| **3. Markdown 변환** | 2주 | **2.5주** | HWP 변환 파이프라인 추가 |
| **4. 보고서 생성** | 2주 | **2주** | 변경 없음 |
| **5. 테스트 & 최적화** | 2주 | **2.5주** | 보안/감사 테스트 강화 |
| **총 기간** | **10주** | **11.5주** | **+1.5주** |

---

## 결론

GovProject AI Manager는 **정부기관 표준을 준수**하면서 **AI 자동화를 통한 생산성 향상**을 동시에 달성할 수 있는 솔루션입니다.

**성공 조건**:
1. Jira/Confluence/Slack의 정부 표준 설정 고착화
2. API Token 및 보안 관리의 엄격한 준수
3. Claude AI 활용 시 개인정보 보호
4. 최종 산출물 HWP 변환 자동화

---

**검증자**: Gemini CLI  
**검증일**: 2026-06-06  
**상태**: 완료 및 승인 권장
