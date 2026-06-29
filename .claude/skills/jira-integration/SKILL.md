---
name: jira-integration
description: Use this skill when retrieving Jira tickets, analyzing requirements, updating ticket status, adding comments, or transitioning issues. Provides Jira API patterns via MCP or direct REST calls.
origin: ECC
---

# Jira Integration Skill (egov-demo)

Jira 이슈를 조회·분석·업데이트한다. **MCP 우선** — 저장소 루트 `.mcp.json`의 `atlassian`(mcp-atlassian)이 Jira+Confluence를 함께 제공한다. MCP 불가 시에만 REST 폴백.

## 사용 시점

- 티켓 조회로 요구사항 파악, 테스트 가능한 수용기준 추출
- 진행 코멘트 추가, 상태 전이(To Do → In Progress → Done)
- PR/브랜치 연결, JQL 검색

## MCP 도구 (mcp-atlassian)

| 도구 | 용도 |
|---|---|
| `jira_search` | JQL 검색 (예: `project = MZ2026 AND status = "In Progress"`) |
| `jira_get_issue` | 이슈 상세 조회 (키: `MZ2026-1234`) |
| `jira_create_issue` / `jira_update_issue` | 이슈 생성 / 필드 수정 |
| `jira_transition_issue` | 상태 전이 (전이 전 `jira_get_transitions` 먼저 호출 — ID는 워크플로우마다 다름) |
| `jira_add_comment` | 코멘트 추가 |
| `jira_create_issue_link` / `jira_get_issue_development_info` | 이슈 링크 / 연결 PR·브랜치 조회 |

## REST 폴백 (MCP 불가 시)

인증은 `.env`의 `JIRA_EMAIL`/`JIRA_TOKEN`(`env_loader.load_env()` 자동 로드). 베이스 `JIRA_BASE_URL`. 인증 헤더 `-u "$JIRA_EMAIL:$JIRA_TOKEN"`.

| 작업 | 엔드포인트 (v3) |
|---|---|
| 티켓 조회 | `GET /rest/api/3/issue/{key}` |
| 코멘트 조회/추가 | `GET\|POST /rest/api/3/issue/{key}/comment` (본문은 ADF `doc` 포맷) |
| 전이 목록/실행 | `GET\|POST /rest/api/3/issue/{key}/transitions` |
| JQL 검색 | `GET /rest/api/3/search/jql` ⚠️ 구 `/search`는 **410 폐기** (`scripts/confluence/jira_api.py` 반영) |

## 티켓 분석 (조회 후 추출 항목)

- **테스트 가능 요구사항**: 기능 요구사항, 수용기준, 사용자 역할/권한, 데이터·연계 지점
- **필요 테스트 유형**: Unit / Integration / E2E / API
- **엣지·오류 시나리오**: 잘못된 입력, 미인가 접근, 타임아웃, 동시성/경합, 경계값, null, 상태 전이

**구조화 출력**: 티켓키·요약·상태·우선순위 / 요구사항 목록 / 수용기준 체크리스트 / 테스트 시나리오(Happy·Error·Edge) / 필요 테스트데이터 / 의존성.

## 티켓 업데이트

| 워크플로우 단계 | Jira 업데이트 |
|---|---|
| 작업 시작 | "In Progress" 전이 + 브랜치명 코멘트 |
| 테스트 작성/통과 | 커버리지 요약 코멘트 |
| PR 생성 | PR 링크 코멘트 + 이슈 링크 |
| PR 머지 | "Done"/"In Review" 전이 |

코멘트 원칙: 진행하며 수시 업데이트, 간결하게, 복사 대신 링크(PR·테스트리포트), 수용기준 모호 시 코딩 전 확인.

## 보안·문제해결

- 토큰 하드코딩 금지 → `.env`/시크릿 매니저, `.gitignore` 등록, 노출 시 즉시 재발급, 최소권한.
- `401` 토큰 만료 → 재발급 / `403` 권한 부족 / `404` 키·URL 확인 / `spawn uvx ENOENT` → `uvx` 전체경로 또는 PATH 설정 / 타임아웃 → VPN·방화벽.

## egov-demo 적용 노트

- **환경변수**: egov `.env`는 `JIRA_BASE_URL`·`JIRA_EMAIL`·`JIRA_TOKEN` (ECC의 `JIRA_URL`/`JIRA_API_TOKEN`과 동일 의미).
- **프로젝트**: `MZ2026` (2026 한국해양교통안전공단 산출물관리).
- **Confluence 연동**: [[confluence-integration]] (동일 mcp-atlassian).
