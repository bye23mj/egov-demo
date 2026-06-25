# GovProject AI Manager API 키 발급 및 권한 설정 가이드

## 1. 개요

본 문서는 **GovProject AI Manager** 자동화 개발에 필요한 API 키, 토큰, Webhook URL, 서비스 계정, 권한 설정 방법을 정리한 가이드이다.

대상 시스템은 다음과 같다.

| 시스템 | 용도 |
|---|---|
| Jira Cloud | 프로젝트, 이슈, 산출물, 일정, 상태 관리 |
| Confluence Cloud | 문서 Space, Page Tree, 산출물, 보고서, AI Context 관리 |
| Slack | 산출물 작성 요청, 지연 알림, 보고 검토 요청 |
| Claude / Anthropic | 문서 검토, 요구사항 분석, 보고서 생성, Context 요약 |
| 내부 시스템 | DB, 파일 저장소, 암호화 키, Secret 관리 |

---

## 2. 필요한 키/토큰 전체 목록

| 구분 | 필요한 인증정보 | 사용 목적 |
|---|---|---|
| Atlassian / Jira | Atlassian API Token | Jira 프로젝트, 이슈, 필드, 댓글, 상태 변경 |
| Atlassian / Confluence | Atlassian API Token | Confluence Space, Page, 첨부파일 생성/조회/수정 |
| Atlassian OAuth 선택 | OAuth 2.0 App Client ID / Secret | 사용자별 권한 위임 방식 연동 |
| Slack | Bot User OAuth Token | 채널 생성, 메시지 발송, 사용자 조회 |
| Slack | Incoming Webhook URL | 특정 채널에 단순 알림 발송 |
| Slack | Signing Secret | Slack 이벤트/인터랙션 요청 검증 |
| Slack | App-Level Token 선택 | Socket Mode 사용 시 필요 |
| Claude / Anthropic | Anthropic API Key | Claude API 호출, 문서 검토, 보고서 생성 |
| 내부 시스템 | DB 접속정보 | 프로젝트, 산출물, 보고 이력 저장 |
| 내부 시스템 | 암호화 키 | 토큰 암호화 저장 |
| 선택 | Git / GitLab / GitHub Token | Markdown 변환본을 Git 저장소에 저장할 경우 |

---

# 3. Atlassian API Token

Jira와 Confluence Cloud는 같은 **Atlassian API Token**을 사용해 REST API를 호출할 수 있다.

## 3.1 사용 대상

```text
Jira REST API
Confluence REST API
Jira 이슈 생성/수정
Jira 상태 변경
Jira 댓글 작성
Confluence Space 생성
Confluence Page Tree 생성
Confluence 첨부파일 조회/다운로드
Confluence 문서 수정
```

## 3.2 발급 방법: 개인 계정 기준

1. Atlassian 계정에 로그인한다.
2. Atlassian Account → Security → API tokens 메뉴로 이동한다.
3. **Create API token**을 클릭한다.
4. 토큰 이름을 입력한다.

예:

```text
govproject-ai-manager-dev
govproject-ai-manager-prod
```

5. 생성된 토큰을 즉시 복사한다.
6. 비밀번호 관리자나 Secret Manager에 저장한다.

> API Token은 생성 후 다시 볼 수 없으므로 생성 직후 반드시 안전한 곳에 저장해야 한다.

## 3.3 발급 방법: 서비스 계정 기준

운영 자동화에는 개인 계정보다 **서비스 계정**을 권장한다.

예:

```text
govproject-bot@company.com
```

서비스 계정 방식 권장 이유:

```text
개인 퇴사/이동 영향 없음
자동화 로그 추적이 쉬움
권한 최소화 가능
운영/개발 토큰 분리 가능
```

## 3.4 사용 방법

Jira/Confluence Cloud REST API 호출 시 보통 아래 형식을 사용한다.

```text
Username: Atlassian 계정 이메일
Password: Atlassian API Token
```

예:

```bash
curl -u "govproject-bot@company.com:ATLASSIAN_API_TOKEN" \
  -H "Accept: application/json" \
  "https://your-domain.atlassian.net/rest/api/3/project"
```

또는 Basic Auth 헤더를 직접 만들 수 있다.

```text
Authorization: Basic base64(email:api_token)
```

## 3.5 Spring Boot 설정 예시

```yaml
atlassian:
  base-url: https://your-domain.atlassian.net
  email: ${ATLASSIAN_EMAIL}
  api-token: ${ATLASSIAN_API_TOKEN}
  jira:
    base-path: /rest/api/3
  confluence:
    base-path: /wiki/api/v2
```

환경변수:

```bash
export ATLASSIAN_EMAIL=govproject-bot@company.com
export ATLASSIAN_API_TOKEN=xxxxxxxxxxxxxxxx
```

---

# 4. Jira API 권한 준비

Atlassian API Token 자체에는 세부 권한 범위가 붙는 것이 아니라, **토큰을 발급한 계정의 Jira 권한**을 따른다.

따라서 `govproject-bot@company.com` 계정에 Jira 프로젝트 권한을 부여해야 한다.

## 4.1 필요한 Jira 권한

| 권한 | 용도 |
|---|---|
| Browse Projects | 프로젝트/이슈 조회 |
| Create Issues | 산출물 이슈 생성 |
| Edit Issues | 담당자, 기한, 링크, 필드 수정 |
| Transition Issues | 이슈 상태 변경 |
| Add Comments | 자동화 댓글 작성 |
| Link Issues | 요구사항-산출물-개발 이슈 연결 |
| Assign Issues | 담당자 배정 |
| Manage Watchers | PM/PL 알림 대상 관리 |
| Administer Projects 선택 | 프로젝트 설정 자동화 시 필요 |

권장 방식은 **Administer Projects 권한은 최소화**하고, 프로젝트 템플릿은 관리자가 만들어두며, 자동화 계정은 이슈와 문서 운영에 필요한 권한만 갖는 것이다.

---

# 5. Confluence API 권한 준비

Confluence도 Jira와 동일하게 Atlassian API Token을 사용할 수 있다.

## 5.1 필요한 Confluence 권한

| 권한 | 용도 |
|---|---|
| View Space | 문서 조회 |
| Add Pages | 산출물 페이지 생성 |
| Edit Pages | 페이지 내용 갱신 |
| Delete Pages 선택 | 자동 정리 기능이 있을 때만 |
| Add Attachments | Markdown 변환본 또는 원본 첨부 |
| Space Admin 선택 | Space 자동 생성/권한 설정 시 필요 |

## 5.2 권장 운영

```text
Space 생성은 관리자 또는 초기 설정 Wizard에서 수행
일반 운영 중에는 automation-bot이 페이지 생성/수정/첨부만 수행
삭제 권한은 가능하면 제외
```

---

# 6. Atlassian OAuth 2.0 선택

Atlassian API Token 방식은 구현이 간단하지만, 사용자별 권한 위임이나 외부 서비스형 제품으로 만들 경우에는 OAuth 2.0을 고려해야 한다.

## 6.1 API Token 방식과 OAuth 방식 비교

| 방식 | 장점 | 단점 | 추천 상황 |
|---|---|---|---|
| API Token + Basic Auth | 구현 간단, 내부 자동화에 적합 | 서비스 계정 권한 중심, 세밀한 사용자 위임 어려움 | 사내 자동화 MVP |
| OAuth 2.0 | 사용자별 권한 위임, 보안 관리 우수 | 구현 복잡, 앱 등록 필요 | 제품화, 다수 고객사 제공 |
| Forge App | Atlassian 생태계 내 앱 구현 적합 | 개발 구조 제약 | Atlassian 앱으로 배포할 경우 |

현재 요구사항은 회사 내부 정부프로젝트 관리 자동화이므로 **1차 MVP는 API Token + 서비스 계정 방식**을 추천한다.

---

# 7. Slack Bot Token

Slack 자동화를 위해서는 Slack 앱을 만들고 Bot Token을 발급받아야 한다.

## 7.1 사용 대상

```text
Slack 채널 생성
Slack 채널에 사용자 초대
산출물 작성 요청 메시지 발송
기한 초과 알림 발송
주간보고 검토 요청
월간보고 검토 요청
버튼 기반 승인/반려 메시지
```

## 7.2 발급 방법

1. Slack API Apps 페이지로 이동한다.
2. **Create New App**을 클릭한다.
3. **From scratch**를 선택한다.
4. 앱 이름을 입력한다.

예:

```text
GovProject Bot
```

5. 사용할 Workspace를 선택한다.
6. **OAuth & Permissions** 메뉴로 이동한다.
7. Bot Token Scopes를 추가한다.
8. **Install to Workspace**를 클릭한다.
9. 발급된 **Bot User OAuth Token**을 복사한다.

Bot Token은 보통 아래 형태이다.

```text
xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxx
```

## 7.3 필요한 Slack Bot Scopes

| Scope | 용도 |
|---|---|
| `chat:write` | 메시지 발송 |
| `chat:write.public` | 봇이 참여하지 않은 공개 채널에 메시지 발송이 필요한 경우 |
| `channels:read` | 공개 채널 목록 조회 |
| `channels:manage` | 공개 채널 생성/관리 |
| `groups:read` | 비공개 채널 조회 |
| `groups:write` 또는 관련 권한 | 비공개 채널 관리가 필요한 경우 |
| `users:read` | 사용자 조회 |
| `users:read.email` | 이메일 기준 사용자 매핑 |
| `im:write` | DM 발송 |
| `incoming-webhook` | Incoming Webhook 사용 |
| `commands` | Slash Command 사용 시 |
| `links:read`, `links:write` 선택 | 링크 unfurl 또는 커스텀 링크 처리 |
| `reactions:write` 선택 | 처리 완료 반응 표시 |

최소 MVP라면 다음 정도로 시작한다.

```text
chat:write
channels:read
users:read
users:read.email
im:write
incoming-webhook
```

채널 자동 생성을 하려면 추가로 다음이 필요하다.

```text
channels:manage
```

## 7.4 Spring Boot 설정 예시

```yaml
slack:
  bot-token: ${SLACK_BOT_TOKEN}
  signing-secret: ${SLACK_SIGNING_SECRET}
  default-channel: gov-project-doc-request
```

환경변수:

```bash
export SLACK_BOT_TOKEN=xoxb-xxxxxxxx
export SLACK_SIGNING_SECRET=xxxxxxxx
```

---

# 8. Slack Incoming Webhook URL

단순 알림만 보낼 경우 Bot Token보다 Incoming Webhook이 더 간단하다.

## 8.1 사용 대상

```text
산출물 작성 요청
문서 변환 완료 알림
Claude 검토 완료 알림
주간보고 생성 알림
월간보고 생성 알림
```

## 8.2 발급 방법

1. Slack App 설정으로 이동한다.
2. **Incoming Webhooks** 메뉴를 연다.
3. **Activate Incoming Webhooks**를 On으로 변경한다.
4. **Add New Webhook to Workspace**를 클릭한다.
5. 메시지를 보낼 채널을 선택한다.
6. Webhook URL을 복사한다.

Webhook URL 예:

```text
https://hooks.slack.com/services/<TEAM>/<CHANNEL>/<TOKEN>
```

## 8.3 사용 예시

```bash
curl -X POST \
  -H 'Content-type: application/json' \
  --data '{"text":"[산출물 작성 요청] 요구사항정의서 작성이 필요합니다."}' \
  https://hooks.slack.com/services/...
```

---

# 9. Slack Signing Secret

Slack에서 버튼 클릭, 모달, Slash Command, Event Subscription을 사용할 경우 **Signing Secret**이 필요하다.

## 9.1 사용 대상

```text
Slack 버튼 클릭 검증
승인/반려 인터랙션 처리
Slash Command 요청 검증
Slack Event Subscription 검증
```

## 9.2 확인 방법

1. Slack App 설정으로 이동한다.
2. **Basic Information** 메뉴를 연다.
3. **App Credentials** 섹션을 확인한다.
4. **Signing Secret** 값을 복사한다.

## 9.3 주의

Signing Secret은 사용자가 보낸 요청이 실제 Slack에서 온 것인지 검증하는 데 사용한다.  
운영 시스템에서는 반드시 검증해야 한다.

---

# 10. Jira Cloud for Slack 앱

이것은 GovProject Bot과 별개로 설치하는 공식 앱이다.

## 10.1 사용 대상

```text
Slack에서 Jira 이슈 미리보기
Slack 메시지에서 Jira 이슈 생성
Jira 프로젝트 알림 구독
/jira connect 사용
/jira notify 사용
```

## 10.2 설치 방법

1. Slack App Directory에서 **Jira Cloud**를 검색한다.
2. 앱을 설치한다.
3. Atlassian 사이트를 선택한다.
4. Jira 계정으로 인증한다.
5. Slack 채널에서 아래 명령어를 실행한다.

```text
/jira connect
```

6. 연결할 Jira 프로젝트를 선택한다.

## 10.3 자동화 한계

```text
앱 설치는 관리자 승인이 필요함
채널별 /jira connect는 수동 작업이 필요할 수 있음
공식 앱의 연결 상태를 GovProject AI Manager가 완전히 제어하기 어려움
```

따라서 다음 구조를 추천한다.

```text
Jira Cloud for Slack 공식 앱
→ Jira 이슈 미리보기, Slack에서 Jira 이슈 생성

GovProject Bot
→ 산출물 작성 요청, 지연 알림, Claude 검토, 보고 자동화
```

---

# 11. Claude / Anthropic API Key

Claude를 프로그램에서 직접 호출하려면 Anthropic API Key가 필요하다.

## 11.1 사용 대상

```text
Markdown 문서 요약
요구사항 누락 검토
설계 문서 품질 검토
테스트케이스 누락 검토
주간보고 초안 생성
월간보고 요약
Claude Context 생성
```

## 11.2 발급 방법

1. Anthropic Console에 접속한다.
2. 계정 또는 조직을 생성한다.
3. Billing 설정을 확인한다.
4. API Keys 메뉴로 이동한다.
5. **Create Key**를 클릭한다.
6. 키 이름을 입력한다.

예:

```text
govproject-ai-manager-dev
govproject-ai-manager-prod
```

7. 생성된 API Key를 복사한다.
8. Secret Manager에 저장한다.

## 11.3 Spring Boot 설정 예시

```yaml
anthropic:
  api-key: ${ANTHROPIC_API_KEY}
  model: claude-sonnet-4-5
```

환경변수:

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

운영에서는 개발/운영 키를 반드시 분리한다.

---

# 12. 선택: GitHub / GitLab Token

Markdown 변환 결과나 Claude Context를 Git 저장소에 버전관리하려면 GitHub 또는 GitLab Token이 필요하다.

## 12.1 사용 대상

```text
Markdown 변환본 저장
AI Context 버전관리
산출물 기준선 관리
보고서 이력 관리
```

## 12.2 필요한 권한

GitHub 기준:

```text
repo
contents:read
contents:write
pull_requests:write 선택
```

GitLab 기준:

```text
read_repository
write_repository
api 선택
```

정부기관 프로젝트에서는 문서 보안이 중요하므로 외부 GitHub보다 사내 GitLab 또는 내부 Git 저장소를 권장한다.

---

# 13. 내부 저장소 / DB / 암호화 키

## 13.1 DB 접속정보

필요 항목:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USERNAME
DB_PASSWORD
```

저장 데이터:

```text
프로젝트 정보
산출물 정보
Jira 이슈 매핑
Confluence 페이지 매핑
Slack 채널 매핑
문서 변환 이력
Claude 검토 이력
보고서 생성 이력
```

## 13.2 암호화 키

API Token을 DB에 저장해야 한다면 반드시 암호화한다.

권장 환경변수:

```text
APP_ENCRYPTION_KEY
```

권장 방식:

```text
AWS KMS
Azure Key Vault
GCP Secret Manager
HashiCorp Vault
Kubernetes Secret
사내 Secret Manager
```

---

# 14. 환경변수 목록 예시

개발/운영 서버에는 아래 환경변수를 준비한다.

```bash
# Atlassian
ATLASSIAN_BASE_URL=https://your-domain.atlassian.net
ATLASSIAN_EMAIL=govproject-bot@company.com
ATLASSIAN_API_TOKEN=xxxxxxxx

# Jira
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_API_BASE=/rest/api/3

# Confluence
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_API_BASE=/api/v2

# Slack
SLACK_BOT_TOKEN=xoxb-xxxxxxxx
SLACK_SIGNING_SECRET=xxxxxxxx
SLACK_DEFAULT_CHANNEL=gov-project-doc-request
SLACK_WEBHOOK_DOC_REQUEST=https://hooks.slack.com/services/...
SLACK_WEBHOOK_REPORT=https://hooks.slack.com/services/...

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-5

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=govproject
DB_USERNAME=govproject
DB_PASSWORD=xxxxxxxx

# Security
APP_ENCRYPTION_KEY=xxxxxxxx
```

---

# 15. 권장 키 관리 정책

## 15.1 개발/운영 키 분리

```text
dev
staging
prod
```

환경별로 별도 토큰을 사용한다.

## 15.2 서비스 계정 분리

권장 계정:

```text
govproject-jira-bot@company.com
govproject-confluence-bot@company.com
govproject-report-bot@company.com
```

작게 시작할 때는 하나의 계정으로도 가능하지만, 운영에서는 분리하는 것이 좋다.

## 15.3 최소 권한 원칙

```text
Jira Admin 권한은 가급적 제외
Confluence Delete 권한은 제외
Slack Admin 권한은 초기 설정 후 제거
Claude API Key는 서버에서만 사용
프론트엔드에 토큰 노출 금지
```

## 15.4 토큰 저장 금지 위치

```text
소스코드
Git 저장소
Confluence 문서
Slack 메시지
Jira 이슈 댓글
로그 파일
프론트엔드 localStorage
```

## 15.5 저장 권장 위치

```text
환경변수
Kubernetes Secret
Vault
AWS Secrets Manager
Azure Key Vault
GCP Secret Manager
사내 보안 저장소
```

---

# 16. 발급 체크리스트

## 16.1 Atlassian

```text
[ ] 서비스 계정 생성
[ ] Jira 프로젝트 접근 권한 부여
[ ] Confluence Space 접근 권한 부여
[ ] API Token 생성
[ ] Token 만료일 기록
[ ] 개발/운영 Token 분리
[ ] Secret Manager 저장
[ ] Jira API 호출 테스트
[ ] Confluence API 호출 테스트
```

## 16.2 Slack

```text
[ ] Slack App 생성
[ ] Bot Token Scopes 추가
[ ] Workspace 설치
[ ] Bot User OAuth Token 복사
[ ] Incoming Webhook 활성화
[ ] 채널별 Webhook 생성
[ ] Signing Secret 저장
[ ] 테스트 채널에 메시지 발송
[ ] Jira Cloud for Slack 앱 설치
[ ] /jira connect 테스트
```

## 16.3 Claude

```text
[ ] Anthropic Console 계정 생성
[ ] Billing 설정 확인
[ ] API Key 생성
[ ] 개발/운영 Key 분리
[ ] Secret Manager 저장
[ ] 간단한 Prompt 호출 테스트
[ ] 사용량 제한/비용 모니터링 설정
```

## 16.4 내부 시스템

```text
[ ] DB 계정 생성
[ ] 파일 저장소 접근키 생성
[ ] 암호화 키 생성
[ ] 로그 마스킹 설정
[ ] 토큰 접근 권한 제한
[ ] 백업 정책 확인
```

---

# 17. 자동화 개발 시 우선순위

가장 먼저 필요한 키는 아래 4개다.

```text
1. ATLASSIAN_EMAIL
2. ATLASSIAN_API_TOKEN
3. SLACK_BOT_TOKEN 또는 SLACK_WEBHOOK_URL
4. ANTHROPIC_API_KEY
```

1차 MVP는 다음 조합으로 충분하다.

```text
Atlassian API Token
+ Slack Incoming Webhook
+ Anthropic API Key
```

2차 확장부터는 다음을 추가한다.

```text
Slack Bot Token
Slack Signing Secret
Atlassian OAuth 2.0
Git 저장소 Token
Secret Manager 연동
```

---

# 18. 최종 권장 발급 방식

## 18.1 MVP 단계

```text
Atlassian 서비스 계정 1개
→ Jira + Confluence API Token 발급

Slack App 1개
→ Incoming Webhook + Bot Token 발급

Anthropic API Key 1개
→ Claude 문서검토/보고 자동화에 사용
```

## 18.2 운영 단계

```text
Atlassian 서비스 계정 분리
→ jira-bot, confluence-bot, report-bot

Slack App 권한 최소화
→ 채널별 Webhook 또는 Bot 권한 분리

Claude API Key 환경별 분리
→ dev, staging, prod

Secret Manager 적용
→ 모든 토큰 암호화 저장
```

이렇게 준비하면 Jira, Confluence, Slack 사전작업 자동화와 Claude 기반 문서관리 자동화를 안정적으로 개발할 수 있다.
