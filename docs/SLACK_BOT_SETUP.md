# Slack 봇(sejongDev) 수신 설정 가이드 — 세종개발팀

> 목표: 기존 **sejongDev 앱 + 세종개발팀 채널 + 웹훅(발송)** 에 **봇 토큰(수신)** 을 추가해
> `@sejongDev {명령} + 첨부` 를 받아 **slack-orchestrator** 로 검토를 실행한다.
>
> 인증 구조: **웹훅 = 발송**, **봇(Socket Mode) = 수신/응답/첨부 다운로드**.

---

## 0. 현재 상태 (이미 완료)

- [x] Slack 앱 **sejongDev** 생성
- [x] **세종개발팀** 채널 생성
- [x] **Incoming Webhook** 으로 메시지 발송 (`.env` `SLACK_WEBHOOK_URL`)

이 가이드는 여기에 **수신 기능**을 추가한다.

---

## 1. Bot Token Scopes 추가 → `xoxb-` 발급

1. <https://api.slack.com/apps> → **sejongDev** 앱 선택
2. 좌측 **OAuth & Permissions** → **Scopes → Bot Token Scopes** 에 추가:

| Scope | 용도 |
|---|---|
| `app_mentions:read` | `@sejongDev` 멘션 수신 |
| `channels:history` | 공개 채널 메시지 읽기 |
| `groups:history` | 세종개발팀이 **비공개** 채널이면 필요 |
| `chat:write` | 검토 결과/상태 메시지 발송 |
| `files:read` | 첨부파일 다운로드 |
| `channels:read` | 채널 ID/이름 조회 |
| `users:read` | 작성자 이름 조회(선택) |

3. 상단 **Install to Workspace**(또는 Reinstall) → 승인
4. **Bot User OAuth Token** (`xoxb-...`) 복사 → 2장에서 `.env`에 저장

> ⚠️ 토큰은 절대 커밋 금지. `.env`(gitignore)에만 둔다.

---

## 2. App-Level Token + Socket Mode → `xapp-` 발급 (수신용, 공개 서버 불필요)

로컬/사내망에서 공개 URL 없이 이벤트를 받으려면 **Socket Mode** 를 쓴다(권장).

1. 좌측 **Basic Information → App-Level Tokens → Generate Token and Scopes**
   - Token Name: `sejongdev-socket`
   - Scope: **`connections:write`** 추가 → Generate → **`xapp-...`** 복사
2. 좌측 **Socket Mode → Enable Socket Mode = On**
3. 좌측 **Event Subscriptions → Enable Events = On**
   - **Subscribe to bot events** 에 추가:
     - `app_mention` (멘션 트리거)
     - `message.channels` (채널 일반 메시지도 받으려면, 선택)
   - Socket Mode면 **Request URL 입력 불필요**
4. 변경 후 앱 **재설치**(scope/event 변경 시 필요)

> Socket Mode 대신 **Events API(공개 URL)** 를 쓰려면: Event Subscriptions의 Request URL에
> 공개 HTTPS 엔드포인트(예: 사내 서버/ngrok)를 등록하고 URL 검증(challenge)을 처리해야 한다.
> 공개 서버가 없으면 **Socket Mode가 정답**이다.

---

## 3. 봇을 세종개발팀 채널에 초대

세종개발팀 채널에서:
```
/invite @sejongDev
```
초대해야 봇이 그 채널의 메시지·첨부를 읽을 수 있다.

채널 ID 확인: 채널명 우클릭 → "채널 세부정보 보기" 하단 또는 URL의 `C...` 값.

---

## 4. `.env` 설정

`.env`(gitignore됨)에 추가:
```bash
# Slack 봇 (수신/응답)
SLACK_BOT_TOKEN=xoxb-...            # 1장: Bot User OAuth Token
SLACK_APP_TOKEN=xapp-...            # 2장: App-Level Token (Socket Mode)
SLACK_TEAM_CHANNEL_ID=C...          # 세종개발팀 채널 ID
# (기존) 발송용 웹훅은 그대로 유지
# SLACK_WEBHOOK_URL=...
```

---

## 5. 의존성 설치

```bash
python3 -m pip install slack_bolt slack_sdk
```
- `slack_bolt`: Socket Mode 이벤트 수신 프레임워크
- `slack_sdk`: 첨부 다운로드·메시지 발송 API

---

## 6. 수신 핸들러 실행 (`scripts/slack_bot_receiver.py`)

본 저장소에 스타터가 포함되어 있다. 동작:
1. `app_mention` 수신 → 명령어 파싱
2. 첨부 다운로드(`files:read`, Bearer 토큰)
3. **slack-orchestrator** 흐름으로 라우팅(전문 에이전트 검토)
4. 결과 요약을 같은 스레드로 응답

```bash
# .env 로드 후 실행 (지속 실행: 이벤트 대기)
python3 scripts/slack_bot_receiver.py
```
> 현재 스타터는 **수신·첨부 다운로드·스레드 응답**까지 검증용으로 구현되어 있고,
> 전문 에이전트 검토는 `slack-orchestrator` 스킬(8단계)로 이어 붙이는 지점을 표시해 두었다.

---

## 7. slack-orchestrator 연결 지점

수신 핸들러가 명령+첨부를 확보하면, `slack-orchestrator` 스킬의 8단계로 넘긴다:

| 수신 핸들러 | → slack-orchestrator |
|---|---|
| 멘션 텍스트 | 1) Slack 명령어 확인 |
| 첨부 메타 | 2) 첨부파일명 확인 |
| 다운로드 파일 | 3) 첨부 내용 확인 → `docs/06. slack-review/.../attachments/` |
| (이후) | 4~8) Agent 결정·검토·상태공유·요약·다음액션 |

---

## 8. 검증 순서

1. `python3 scripts/slack_bot_receiver.py` 실행(연결 로그 `⚡️ Bolt app is running` 확인)
2. 세종개발팀에서 `@sejongDev 핑` 입력 → 봇이 스레드로 응답하면 **수신 OK**
3. `@sejongDev 데이터모델링검토` + xlsx 첨부 → 첨부 다운로드 로그 확인
4. 다운로드 경로(`docs/06. slack-review/...`)에 파일 저장 확인

---

## 보안 체크리스트

- [ ] `xoxb-`/`xapp-` 는 `.env`(gitignore)에만. 코드·로그·커밋 노출 금지
- [ ] 최소 권한 scope만 부여(위 표 기준)
- [ ] 첨부의 시크릿/개인정보는 마스킹 후 요약(원문 대량 게시 금지)
- [ ] 봇은 필요한 채널에만 초대
- [ ] 토큰 유출 시 **OAuth & Permissions → Revoke / Rotate**

---

## 트러블슈팅

| 증상 | 원인/조치 |
|---|---|
| 멘션해도 무반응 | 봇 채널 미초대 / `app_mention` 미구독 / 핸들러 미실행 |
| `not_in_channel` | `/invite @sejongDev` |
| `missing_scope` | 필요 scope 추가 후 **재설치** |
| 첨부 다운로드 401 | `files:read` 누락 또는 Bearer 토큰 미사용 |
| Socket 연결 실패 | `xapp-` 토큰/`connections:write`/Socket Mode On 확인 |
