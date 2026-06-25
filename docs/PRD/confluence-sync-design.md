# Confluence 문서 동기화 기능 설계

> egov-demo ↔ Confluence (nsonesoft.atlassian.net) 양방향 동기화
> 작성일: 2026-06-06

---

## 1. 개요

### 목적
- Confluence 폴더의 문서를 로컬 `/docs/00. confluence`에 동기화
- 로컬에서 작성한 신규 문서를 Confluence에 자동 업로드
- CLI 명령어 또는 스크립트로 양방향 동기화

### 연동 대상
| 항목 | 값 |
|---|---|
| **Confluence URL** | https://nsonesoft.atlassian.net |
| **Space Key** | TNYUU |
| **Folder ID** | 661389353 |
| **Account** | bye23mj@nsonesoft.com |
| **Auth Token** | ATATT3xFfGF0KmZp0WmP5iRFdFPXoQj4UGHz4m3wF5OAGy67bmWrkfYSRUtCTTPzQwPDVARUm20PMN4k6aKjBUXC_Tks7NdbiN1rjAFp4BJ3KIsOgf4KqLOzmAbCLl3PIHm8o4dJTqzs9EsVERGizts4GFDf_kpNbj5pSnnnOAtQeWj8Fhi14Hs=5E98863D |
| **Local Folder** | `/Users/ai/vscode/egov-demo/docs/00. confluence` |

---

## 2. 아키텍처

### 2.1 시스템 구성

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLI Interface                              │
│              (confluence-sync 명령어 수행)                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────▼─────────┐           ┌──────▼───────┐
   │ Local Storage│           │ Confluence   │
   │              │◄─────────►│  REST API    │
   │ /docs/00.    │           │              │
   │ confluence   │           │ nsonesoft.   │
   │              │           │ atlassian.   │
   └──────────────┘           │ net/wiki     │
                              └──────────────┘
```

### 2.2 모듈 구조

```
scripts/
├── confluence-sync.py          # 메인 CLI 스크립트
├── confluence/
│   ├── __init__.py
│   ├── api.py                  # Confluence REST API 클라이언트
│   ├── sync.py                 # 동기화 로직
│   ├── converter.py            # HTML ↔ Markdown 변환
│   └── config.py               # 설정 관리
└── tests/
    └── test_confluence_sync.py
```

---

## 3. 기능 요구사항

### FR-001: Confluence 폴더 조회
```
Given: Confluence 인증 토큰 설정 완료
When: confluence-sync download 명령 실행
Then: 
  - TNYUU Space의 폴더 661389353 내 모든 페이지를 재귀로 조회
  - 페이지 메타데이터 (ID, title, version, lastModified) 수집
```

### FR-002: 문서 다운로드 및 변환
```
Given: Confluence 페이지 메타데이터 조회 완료
When: 각 페이지를 순차 처리
Then:
  - HTML 콘텐츠를 Markdown으로 변환
  - 첨부 파일(이미지, 파일)을 로컬에 다운로드
  - `/docs/00. confluence/` 폴더에 저장
  - 메타데이터 파일(.confluence.json) 생성
```

### FR-003: 로컬 신규 문서 감지
```
Given: /docs/00. confluence/ 폴더 모니터링
When: 신규 .md 파일 생성 또는 수정 감지
Then:
  - Confluence에 없는 새 문서 판별
  - 로컬 수정 내용 vs Confluence 버전 비교
```

### FR-004: Confluence 업로드
```
Given: 로컬 신규/수정 문서 목록 수집 완료
When: confluence-sync upload 명령 실행
Then:
  - Markdown → HTML 변환
  - Confluence 폴더에 페이지 생성/업데이트
  - 첨부 파일 업로드
  - 로컬 메타데이터 업데이트
```

### FR-005: 충돌 해결 (Conflict Resolution)
```
Given: 로컬과 Confluence 모두 수정된 문서
When: 동기화 명령 실행
Then:
  - 충돌 감지 및 사용자 선택 요청
  - 옵션: Local Overwrite / Confluence Overwrite / Manual Merge
```

### FR-006: 동기화 로그 및 리포트
```
Given: 동기화 작업 완료
When: 명령 종료
Then:
  - 로그 파일 생성 (.confluence-sync.log)
  - 요약 리포트: 다운로드 N개, 업로드 N개, 충돌 N개, 오류 N개
```

---

## 4. 수용조건 (Given-When-Then)

### AC-001: 처음 동기화 (초기화)
```
Given: 빈 로컬 폴더, Confluence에 5개 문서 존재
When: confluence-sync download --init 명령 실행
Then:
  - 5개 문서 모두 로컬에 다운로드
  - 각 문서별 .confluence.json 메타데이터 생성
  - 로그: "Downloaded 5 documents"
```

### AC-002: 증분 동기화 (다운로드만)
```
Given: 로컬에 3개 문서, Confluence에 5개 문서
When: confluence-sync download 명령 실행
Then:
  - 신규 2개 문서만 다운로드
  - 기존 3개 문서 버전 비교, 업데이트 필요 시 갱신
  - 로그: "Downloaded 2 new, Updated 0"
```

### AC-003: 로컬 신규 문서 업로드
```
Given: 로컬에 `new-document.md` 파일 생성
When: confluence-sync upload 명령 실행
Then:
  - Confluence 폴더 661389353에 페이지 생성
  - 로컬 파일에 .confluence.json 추가 (confluence_id, page_id 포함)
  - 로그: "Created 1 page"
```

### AC-004: 동기화 충돌 처리
```
Given: 로컬과 Confluence 모두 수정된 문서
When: confluence-sync sync 명령 실행
Then:
  - 충돌 감지
  - 사용자에게 선택 옵션 제시 (--local-overwrite, --confluence-overwrite 플래그)
  - 선택에 따라 병합 처리
```

---

## 5. 기술 스택

### 언어 및 라이브러리
| 항목 | 선택 |
|---|---|
| **언어** | Python 3.9+ |
| **Confluence API** | requests 라이브러리 + 기본 HTTP |
| **HTML → Markdown** | html2text, pandoc, or beautifulsoup4 |
| **CLI Framework** | Click 또는 typer |
| **설정 관리** | python-dotenv (토큰 보안) |
| **로깅** | logging 모듈 |
| **테스트** | pytest |

### Confluence REST API 엔드포인트
```
# 폴더 내 페이지 조회 (Recursive)
GET /wiki/api/v2/spaces/TNYUU/pages
Query: limit=50, cursor (페이징)

# 페이지 콘텐츠 조회
GET /wiki/api/v2/pages/{page_id}?body-format=view

# 페이지 생성
POST /wiki/api/v2/pages
Body: { title, space_id, body { representation: "storage", value } }

# 페이지 업데이트
PUT /wiki/api/v2/pages/{page_id}
Body: { version { number }, title, body { ... } }

# 첨부파일 조회
GET /wiki/api/v2/pages/{page_id}/attachments

# 첨부파일 다운로드
GET /wiki/api/v2/attachments/{attachment_id}/file
```

---

## 6. 데이터 구조

### 6.1 메타데이터 파일 (.confluence.json)
```json
{
  "confluence_id": "661389353",
  "page_id": "12345678",
  "page_title": "Sample Document",
  "space_key": "TNYUU",
  "url": "https://nsonesoft.atlassian.net/wiki/spaces/TNYUU/pages/12345678",
  "version": 3,
  "last_modified": "2026-06-06T10:30:00Z",
  "last_modified_by": "bye23mj@nsonesoft.com",
  "local_file": "sample-document.md",
  "local_checksum": "abc123def456",
  "status": "synced",
  "attachments": [
    {
      "id": "att_123",
      "filename": "image.png",
      "local_path": "attachments/image.png"
    }
  ]
}
```

### 6.2 동기화 로그
```
[2026-06-06 14:30:45] INFO: Starting Confluence sync...
[2026-06-06 14:30:46] INFO: Authenticating to https://nsonesoft.atlassian.net
[2026-06-06 14:30:47] INFO: Fetching pages from folder 661389353
[2026-06-06 14:30:50] INFO: Found 5 pages in Confluence
[2026-06-06 14:30:51] INFO: Comparing with local folder /docs/00. confluence
[2026-06-06 14:30:52] INFO: Downloaded: page-1.md, page-2.md (2 new)
[2026-06-06 14:30:53] INFO: Uploaded: new-doc.md (1 new)
[2026-06-06 14:30:54] INFO: Conflicts: 0
[2026-06-06 14:30:55] INFO: Sync completed successfully
```

---

## 7. CLI 명령어 설계

### 기본 명령어
```bash
# 초기 설정 (토큰 저장)
confluence-sync config --set-token "ATATT3xFfGF0KmZp0..."
confluence-sync config --set-folder-id "661389353"

# 초기 동기화
confluence-sync init

# Confluence → Local 다운로드
confluence-sync download [--force]

# Local → Confluence 업로드
confluence-sync upload [--dry-run]

# 양방향 동기화 (충돌 감지)
confluence-sync sync [--local-overwrite | --confluence-overwrite]

# 상태 확인
confluence-sync status

# 로그 확인
confluence-sync log [--tail 20]
```

### 사용 예시
```bash
# 1. 첫 실행: 토큰 설정
$ confluence-sync config --set-token "ATATT3xFfGF0..."
✓ Token saved securely

# 2. 초기화
$ confluence-sync init
✓ Downloaded 5 documents from Confluence
✓ Created metadata files

# 3. 신규 문서 작성 후 업로드
$ confluence-sync upload
✓ Created: new-document.md
✓ Updated: existing-document.md
Summary: 1 created, 1 updated

# 4. Confluence 변경 반영
$ confluence-sync download
✓ Downloaded 2 updated documents
Summary: 2 downloaded
```

---

## 8. 보안 고려사항

### 토큰 관리
- **저장 위치**: `~/.confluence-sync/.env` (홈 디렉토리, 600 권한)
- **환경변수 사용**: `CONFLUENCE_TOKEN` (프로덕션)
- **로그에 노출 방지**: 토큰 마스킹 처리

### API 호출 보안
- HTTPS 강제 사용
- User-Agent 헤더 설정
- Rate Limit 준수 (모듈식 throttling)

### 파일 무결성
- Checksum (SHA256) 저장 및 검증
- 충돌 감지 및 백업 생성 (`.backup`)

---

## 9. 구현 일정

| Phase | 기간 | 작업 |
|---|---|---|
| **1. 설계 및 구조** | 1일 | API 분석, 모듈 설계 |
| **2. 기본 모듈** | 3일 | Confluence API 클라이언트, 인증 |
| **3. 동기화 로직** | 3일 | 다운로드, 업로드, 충돌 해결 |
| **4. CLI 구현** | 2일 | Click/Typer 기반 명령어 |
| **5. 테스트 & 문서** | 2일 | 단위 테스트, 사용자 가이드 |
| **총 기간** | **11일** | |

---

## 10. 파일 구조 (최종)

```
/Users/ai/vscode/egov-demo/
├── docs/
│   └── 00. confluence/           # 동기화 폴더
│       ├── document-1.md
│       ├── document-2.md
│       ├── attachments/
│       │   ├── image-1.png
│       │   └── image-2.jpg
│       └── .confluence-meta.json # 폴더별 메타데이터
├── scripts/
│   ├── confluence-sync.py        # CLI 엔트리포인트
│   └── confluence/
│       ├── __init__.py
│       ├── api.py                # REST API 클라이언트
│       ├── sync.py               # 동기화 로직
│       ├── converter.py          # HTML ↔ Markdown
│       └── config.py             # 설정 관리
├── .env                          # 토큰 저장 (gitignore)
└── .confluence-sync.log          # 동기화 로그
```

---

## 11. 다음 단계

1. ✅ **설계 문서 작성** (현재)
2. **Python 스크립트 구현**
   - Confluence API 클라이언트
   - 동기화 로직
   - CLI 명령어
3. **테스트**
   - 단위 테스트
   - 통합 테스트 (실제 Confluence 연동)
4. **배포**
   - egov-demo에 통합
   - 문서화

---

**설계 승인**: 대기 중  
**상태**: Draft
