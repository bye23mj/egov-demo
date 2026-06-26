# Atlassian (Jira × Confluence) 연계 가이드 — egov-demo

> ECC-main 패턴(MCP 우선) 적용판. Jira 프로젝트 **MZ2026**(2026년 한국해양교통안전공단 산출물관리) + Confluence 산출물 페이지 연계.

## 1. 구성 요약

| 계층 | 자산 | 비고 |
|---|---|---|
| 스킬 | `.claude/skills/jira-integration` (origin:ECC) | Jira 조회·코멘트·상태전이 |
| 스킬 | `.claude/skills/confluence-integration` | 페이지·첨부 발행 (신규) |
| 스킬 | `.claude/skills/api-connector-builder` (origin:ECC) | 신규 커넥터 구현 골격 |
| MCP | `.mcp.json` → `atlassian` (mcp-atlassian) | Jira+Confluence 통합, **권장 경로** |
| REST(레거시) | `scripts/confluence/*` | MCP 미사용 시 보조. `.env` 토큰 사용 |
| 설정 | `.env` + `env_loader.py` | 토큰은 `.env`(gitignore)에서만 |

## 2. 인증 (.env)

Atlassian API 토큰은 **계정 단위**라 Jira/Confluence 공용이다.

```bash
JIRA_BASE_URL=https://nsonesoft.atlassian.net
JIRA_EMAIL=<이메일>
JIRA_TOKEN=<Atlassian API 토큰>          # Confluence도 이 토큰 공용
CONFLUENCE_BASE_URL=https://nsonesoft.atlassian.net/wiki
CONFLUENCE_EMAIL=<이메일>
# CONFLUENCE_API_TOKEN 미설정 시 JIRA_TOKEN 사용 (config.py 폴백)
```
- 토큰 발급: <https://id.atlassian.com/manage-profile/security/api-tokens>
- `.env`는 `.gitignore` 처리됨. 커밋 금지.
- 모든 Jira/Confluence 파이썬은 `env_loader.load_env()`로 `.env`를 자동 로드한다(`confluence` 패키지 import 시 자동).

## 3. MCP 사용 (권장)

```bash
# 사전: Python 3.10+, uv/uvx
uvx mcp-atlassian==0.21.0   # 동작 확인
```
`.mcp.json`의 `atlassian` 서버가 `${JIRA_EMAIL}`·`${JIRA_TOKEN}`을 주입받아 Jira+Confluence MCP 도구를 노출한다.
도구: `jira_search`/`jira_get_issue`/`jira_add_comment`/`confluence_search`/`confluence_create_page` 등.

## 4. REST(레거시) 사용

```python
import sys; sys.path.insert(0, "scripts")
import env_loader; env_loader.load_env()
from confluence.jira_api import JiraAPI
from confluence.api import ConfluenceAPI

j = JiraAPI(); j.test_connection()
issues = j.get_issues_by_jql("project=MZ2026", fields=["summary","status"])

c = ConfluenceAPI(); c.test_connection()
```

## 5. 적용된 수정 (ECC 정리)

| 대상 | 변경 |
|---|---|
| `jira_api.py:get_issues_by_jql` | 구 `/rest/api/3/search`(410 폐기) → **`/search/jql`**(토큰 페이지네이션) |
| `api.py:test_connection` | v2 `spaces`(404) → **v1 `/wiki/rest/api/space`** |
| `config.py:get_token` | `.env`의 `CONFLUENCE_API_TOKEN`/`JIRA_TOKEN` 인식 + 저장소 루트 `.env` 탐색 |

## 6. 검증 상태 (2026-06-26)

- Jira: 인증 200, `project=MZ2026` 이슈 9건 조회 ✅
- Confluence: 연결 200, 산출물 페이지 **661389353** "2026년 해양 프로젝트 산출물 관리" 접근 ✅

## 7. 다음 작업 — 산출물 업로드

`docs/04. db-deliverables`(md 8 + xlsx 26)를 페이지 `661389353` 하위에 발행:
- md → 하위 페이지(`confluence_create_page` 또는 REST)
- xlsx → 첨부(`POST /wiki/rest/api/content/{id}/child/attachment`, `X-Atlassian-Token: no-check`)
- **dry-run으로 페이지 트리·첨부 목록 보고 후 실제 발행** (외부 발행 게이트)
