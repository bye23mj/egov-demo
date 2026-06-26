---
name: confluence-integration
description: Use this skill when reading or publishing Confluence pages — searching spaces, fetching page content, creating/updating pages, or uploading attachments (e.g. DB 산출물 xlsx). Provides Confluence Cloud patterns via MCP (recommended) or direct REST. egov-demo 적용판.
origin: ECC api-connector-builder 패턴 + jira-integration 구조 차용
---

# Confluence Integration Skill (egov-demo)

Confluence Cloud 페이지를 조회·발행하고 산출물(xlsx 등)을 첨부한다. **MCP 우선**, 불가 시 직접 REST.
ECC `jira-integration`의 구조와 `api-connector-builder`의 "기존 패턴에 맞춰 커넥터를 추가" 원칙을 따른다.

## When to Activate

- Confluence 스페이스/페이지 검색·본문 조회
- 페이지 생성/수정 (md → 페이지 본문)
- **DB 산출물(xlsx) 첨부 업로드** (`docs/04. db-deliverables` → 산출물 관리 페이지)
- 산출물 관리대장 동기화

## Prerequisites

Atlassian API 토큰은 **계정 단위**라 Jira와 동일 토큰을 공유한다. (`.env`의 `JIRA_TOKEN` 재사용 가능)

### Option A: MCP Server (권장) — mcp-atlassian (Jira+Confluence 통합)

`mcp-atlassian` 하나가 Jira·Confluence를 모두 제공한다. `.mcp.json`(저장소 루트) 참조.

```jsonc
"atlassian": {
  "command": "uvx",
  "args": ["mcp-atlassian==0.21.0"],
  "env": {
    "CONFLUENCE_URL": "https://nsonesoft.atlassian.net/wiki",
    "CONFLUENCE_USERNAME": "<이메일>",
    "CONFLUENCE_API_TOKEN": "<토큰>"
  }
}
```
요구: Python 3.10+, `uv`/`uvx`.

### Option B: 직접 REST (MCP 불가 시)

`.env`에서 로드 (`env_loader.load_env()`):

| 변수 | 설명 |
|---|---|
| `CONFLUENCE_BASE_URL` | `https://nsonesoft.atlassian.net/wiki` |
| `CONFLUENCE_EMAIL` | Atlassian 계정 이메일 (없으면 `JIRA_EMAIL`) |
| `CONFLUENCE_API_TOKEN` | API 토큰 (없으면 `JIRA_TOKEN`) |

> 인증: HTTP Basic `(email, token)`. 토큰은 `.env`(gitignore)에만 두고 커밋 금지.

## MCP Tools Reference (mcp-atlassian)

| 도구 | 용도 |
|---|---|
| `confluence_search` | CQL 검색 (`text ~ "산출물"`, `space.key=...`) |
| `confluence_get_page` | 페이지 본문 조회 |
| `confluence_create_page` | 페이지 생성 (부모 지정 가능) |
| `confluence_update_page` | 페이지 수정 |
| `confluence_add_attachment`* | 첨부 업로드 (지원 버전 확인) |

## Direct REST Reference (Confluence Cloud v1)

```bash
B="$CONFLUENCE_BASE_URL"; A="$CONFLUENCE_EMAIL:$CONFLUENCE_API_TOKEN"
# 스페이스 목록
curl -s -u "$A" "$B/rest/api/space?limit=50"
# CQL 검색
curl -s -u "$A" "$B/rest/api/content/search" --data-urlencode 'cql=title ~ "산출물"' -G
# 페이지 생성 (부모 하위)
curl -s -u "$A" -X POST "$B/rest/api/content" -H 'Content-Type: application/json' -d '{
  "type":"page","title":"제목","space":{"key":"<SPACE>"},
  "ancestors":[{"id":"<부모페이지ID>"}],
  "body":{"storage":{"value":"<p>본문</p>","representation":"storage"}}}'
# 첨부 업로드 (X-Atlassian-Token 필수)
curl -s -u "$A" -X POST "$B/rest/api/content/<페이지ID>/child/attachment" \
  -H 'X-Atlassian-Token: no-check' -F "file=@경로/파일.xlsx"
```

> **주의**: Confluence v2(`/wiki/api/v2/...`)는 일부 인스턴스에서 404 → 본 스킬은 **v1(`/wiki/rest/api`)** 을 기본으로 한다.

## egov-demo 적용 (현행 컨텍스트)

- **대상 페이지**: `661389353` "2026년 해양 프로젝트 산출물 관리" (MZ2026 Pages, 설정 `folder_id`).
- **소스**: `docs/04. db-deliverables/{요구사항}/...` (md 8 + xlsx 26). md → 하위 페이지, xlsx → 첨부.
- **레거시 클라이언트**: `scripts/confluence/api.py`·`sync.py`는 v1 REST 기반 보조 경로. MCP 미사용 시 활용하되, 신규 구현은 본 스킬의 v1 패턴을 따른다.
- 업로드 전 **dry-run으로 대상 구조(페이지 트리·첨부 목록)를 먼저 보고**한 뒤 실제 발행한다(외부 발행 게이트).

## 경계

- 토큰/시크릿을 코드·로그·커밋에 노출하지 않는다 (`.env`만 사용).
- 외부 발행(페이지 생성·첨부)은 되돌리기 어려우므로 dry-run·사용자 확인 후 수행한다.
- 권한 없는 스페이스에 쓰지 않는다 (403 시 중단·보고).

## Related Skills

- [[jira-integration]] — Jira 이슈 연동 (동일 mcp-atlassian)
- [[api-connector-builder]] — 신규 커넥터(첨부 업로드 등) 구현 골격
