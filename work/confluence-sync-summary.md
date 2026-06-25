# Confluence 문서 동기화 구현 요약

> 작성일: 2026-06-07  
> 프로젝트: egov-demo  
> 연동 대상: https://nsonesoft.atlassian.net (Space: TNYUU, Folder: 2026년 해양 프로젝트 산출물 관리)

---

## 1. 작업 개요

### 목적
Confluence에 등록된 문서를 로컬 파일시스템으로 다운로드하고,  
로컬에서 작성한 신규 문서를 Confluence에 업로드하는 **양방향 동기화** 기능 구현

### 연동 정보
| 항목 | 값 |
|---|---|
| Confluence URL | https://nsonesoft.atlassian.net |
| Space | TNYUU (첨단해양기술연구소) |
| 폴더 ID | 661389353 (2026년 해양 프로젝트 산출물 관리) |
| 계정 | bye23mj@nsonesoft.com |
| 로컬 동기화 경로 | `/Users/ai/vscode/egov-demo/docs/00. confluence` |

---

## 2. 작업 이력

### 2-1. 요구사항 분석
- `docs/PRD/jira_confluence_slack_prerequisites_for_govproject_ai_manager.md` 문서 분석
- Jira + Confluence + Slack 연동 구조 파악
- 동기화 기능 요구사항 도출

### 2-2. 설계
- 양방향 동기화 아키텍처 설계
- CQL(Confluence Query Language) 기반 폴더 탐색 방식 채택
  - Confluence Folder는 Page와 다른 타입 → `GET /wiki/api/v2/folders/{id}/children` 미지원
  - 대안: `GET /wiki/rest/api/search?cql=ancestor={folder_id} AND type=page` 사용
- 메타데이터(.confluence-meta.json) 기반 증분 동기화 설계

### 2-3. 구현
- Python 기반 CLI 스크립트 5개 모듈 구현
- Confluence REST API v1/v2 혼용 (폴더: v2, 검색: v1 CQL, 페이지 콘텐츠: v2)
- 토큰 보안 저장: `~/.confluence-sync/.env` (권한 600)

### 2-4. 테스트 결과
- Confluence 연결 인증 성공
- CQL 검색으로 폴더 내 4개 페이지 조회 성공
- 4개 문서 로컬 다운로드 및 Markdown 변환 성공

### 2-5. 다운로드된 문서 (2026-06-07 기준)
| 파일명 | Confluence 페이지 ID | 내용 |
|---|---|---|
| `02_요구사항_현황판.md` | 661880836 | 요구사항 현황 대시보드 |
| `10.-주간보고-템플릿.md` | 661585941 | 주간보고 작성 템플릿 |
| `DEL-REQ-001-요구사항정의서.md` | 661520434 | 요구사항정의서 (산출물 1) |
| `DEL-REQ-002-요구사항정의서.md` | 661389379 | 요구사항정의서 (산출물 2) |

---

## 3. 소스 파일별 기능 요약

### 3-1. `scripts/confluence-sync.py` — CLI 진입점

**역할**: 사용자가 터미널에서 호출하는 메인 스크립트

| 명령어 | 기능 |
|---|---|
| `config --set-token <token>` | API 토큰을 `~/.confluence-sync/.env`에 저장 |
| `config --show` | 현재 설정 표시 (토큰 마스킹) |
| `status` | 동기화 상태 및 Confluence 연결 테스트 |
| `download` | Confluence → 로컬 다운로드 |
| `download --force` | 변경 여부 무시하고 전체 강제 다운로드 |
| `upload` | 로컬 신규/수정 문서 → Confluence 업로드 |
| `upload --dry-run` | 실제 업로드 없이 대상 목록만 확인 |
| `sync` | 양방향 동기화 (download + upload) |
| `sync --local-overwrite` | 충돌 시 로컬 파일 우선 적용 |
| `sync --confluence-overwrite` | 충돌 시 Confluence 파일 우선 적용 |

```bash
# 사용 예시
python scripts/confluence-sync.py download
python scripts/confluence-sync.py upload --dry-run
python scripts/confluence-sync.py sync
```

---

### 3-2. `scripts/confluence/config.py` — 설정 관리

**역할**: Confluence 연결 정보 및 동기화 설정을 중앙에서 관리

| 항목 | 내용 |
|---|---|
| 클래스 | `ConfluenceConfig` |
| 설정 파일 | `~/.confluence-sync/config.json` |
| 토큰 파일 | `~/.confluence-sync/.env` (권한 600) |
| 기본값 | URL, Space Key, Folder ID, 계정, 로컬 경로 |

**핵심 메서드**:
| 메서드 | 설명 |
|---|---|
| `get_token()` | 환경변수 → `.env` 파일 → 저장값 순서로 토큰 조회 |
| `set(key, value)` | 설정값 변경 및 파일 저장 |
| `display()` | 토큰 마스킹 처리 후 설정 출력 |

**보안**: 토큰은 `config.json`에 저장하지 않고 `.env` 파일에 분리 저장

---

### 3-3. `scripts/confluence/api.py` — Confluence REST API 클라이언트

**역할**: Confluence Cloud API 호출을 추상화한 클라이언트 클래스

| API | 엔드포인트 | 용도 |
|---|---|---|
| 연결 테스트 | `GET /wiki/api/v2/spaces` | 인증 확인 |
| 폴더 정보 조회 | `GET /wiki/api/v2/folders/{id}` | 폴더 메타데이터 |
| **페이지 검색 (CQL)** | `GET /wiki/rest/api/search?cql=...` | **폴더 내 페이지 목록** |
| 페이지 콘텐츠 | `GET /wiki/api/v2/pages/{id}?body-format=view` | HTML 본문 조회 |
| 페이지 생성 | `POST /wiki/api/v2/pages` | 신규 페이지 업로드 |
| 페이지 수정 | `PUT /wiki/api/v2/pages/{id}` | 기존 페이지 업데이트 |
| 첨부파일 목록 | `GET /wiki/api/v2/pages/{id}/attachments` | 첨부 파일 목록 |
| 첨부파일 다운로드 | `GET /wiki/api/v2/attachments/{id}/file` | 파일 바이너리 |

**인증 방식**: Basic Auth (이메일 : API Token)

**CQL 탐색 이유**:
> Confluence의 Folder 타입은 Page와 다르며,  
> `GET /wiki/api/v2/folders/{id}/children` API가 지원되지 않음(404).  
> 대신 CQL(`ancestor={folder_id} AND type=page`)로 하위 페이지를 조회.

---

### 3-4. `scripts/confluence/converter.py` — HTML ↔ Markdown 변환

**역할**: Confluence HTML과 로컬 Markdown 파일 간 양방향 변환

| 함수 | 입력 | 출력 | 사용 라이브러리 |
|---|---|---|---|
| `html_to_markdown(html)` | Confluence HTML | Markdown | `html2text` (폴백: 직접 파싱) |
| `markdown_to_html(markdown)` | Markdown | Confluence storage HTML | `markdown` 라이브러리 |
| `extract_title_from_markdown(md)` | Markdown | H1 제목 문자열 | 정규식 |

**특징**:
- 한글 유니코드 보존 (`unicode_snob=True`)
- 자동 줄바꿈 비활성화 (`body_width=0`)
- `html2text`, `markdown` 라이브러리 미설치 시 기본 정규식 폴백 동작

---

### 3-5. `scripts/confluence/sync.py` — 동기화 로직

**역할**: 로컬 파일과 Confluence 간 동기화 상태 관리 및 처리

**클래스**: `ConfluenceSync`

| 메서드 | 기능 |
|---|---|
| `download(force=False)` | Confluence → 로컬 다운로드 (버전 비교로 증분 처리) |
| `upload(dry_run=False)` | 로컬 → Confluence 업로드 (체크섬 비교로 변경 감지) |
| `sync(...)` | 양방향 동기화 (download + upload 순서 실행) |
| `status()` | 동기화 상태 정보 반환 |

**메타데이터 파일** (`.confluence-meta.json`):
```json
{
  "pages": {
    "661520434": {
      "page_id": "661520434",
      "title": "DEL-REQ-001 요구사항정의서",
      "local_file": "DEL-REQ-001-요구사항정의서.md",
      "version": 1,
      "checksum": "abc123...",
      "last_synced": "2026-06-07T00:11:40",
      "space_key": "TNYUU"
    }
  },
  "last_sync": "2026-06-07T00:11:40"
}
```

**증분 동기화 로직**:
- 다운로드: `remote version != local version` 또는 `--force` 시 갱신
- 업로드: `SHA256 체크섬 변경` 감지 시 업로드

---

## 4. 전체 파일 구조

```
egov-demo/
├── scripts/
│   ├── confluence-sync.py          # CLI 진입점 (명령어 파싱 및 실행)
│   └── confluence/
│       ├── __init__.py             # 패키지 초기화
│       ├── api.py                  # Confluence REST API 클라이언트
│       ├── config.py               # 설정 및 토큰 관리
│       ├── converter.py            # HTML ↔ Markdown 변환
│       └── sync.py                 # 동기화 핵심 로직
├── docs/
│   └── 00. confluence/             # 동기화 로컬 폴더
│       ├── .confluence-meta.json   # 동기화 메타데이터 (자동 생성)
│       ├── 02_요구사항_현황판.md
│       ├── 10.-주간보고-템플릿.md
│       ├── DEL-REQ-001-요구사항정의서.md
│       └── DEL-REQ-002-요구사항정의서.md
└── .claude/
    ├── commands/
    │   └── 문서동기화.md            # /문서동기화 슬래시 명령어
    └── docs/
        ├── confluence-sync-design.md          # 설계 문서
        └── research/
            └── govproject-ai-manager-validation.md  # Gemini 검증 결과
```

---

## 5. 설치 및 실행 방법

### 의존성 설치
```bash
pip3 install requests html2text markdown
```

### 토큰 초기 설정
```bash
python scripts/confluence-sync.py config --set-token "ATATT3xFfGF0..."
```

### 첫 실행 (전체 다운로드)
```bash
cd /Users/ai/vscode/egov-demo
python scripts/confluence-sync.py download
```

### 이후 일반 사용
```bash
# Confluence 변경사항 가져오기
python scripts/confluence-sync.py download

# 로컬 신규 문서 업로드
python scripts/confluence-sync.py upload

# 양방향 동기화
python scripts/confluence-sync.py sync

# 상태 확인
python scripts/confluence-sync.py status
```

---

## 6. 알려진 제약 사항

| 항목 | 내용 |
|---|---|
| Folder 자식 API | `GET /folders/{id}/children` 미지원 (404) → CQL로 우회 |
| 하위 폴더 재귀 | 현재 단일 폴더만 조회 (서브폴더 내 페이지 미지원) |
| 첨부파일 업로드 | 다운로드만 지원, 업로드 미구현 |
| 충돌 해결 | 자동 병합 없음 (flag로 어느 쪽 우선인지 선택) |
| 테이블 변환 | html2text가 Confluence 테이블을 텍스트로 단순 변환 |

---

**작성자**: Claude Code (egov-demo 프로젝트)  
**상태**: 구현 완료, 운영 적용 가능
