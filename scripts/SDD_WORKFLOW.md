# SDD Workflow 자동화 가이드

> Confluence 동기화 + JIRA 연동을 통한 Spec-Driven Development 워크플로우

---

## 📋 개요

본 문서는 **Claude + JIRA + Confluence + Slack** 기반 SDD(Spec-Driven Development) 워크플로우 자동화 구현 가이드입니다.

### 워크플로우 흐름

```
JIRA Kanban (내부검토)
    ↓
문서 수집 (Jira + Confluence)
    ↓
Markdown 정규화
    ↓
Speckit Workspace 자동 실행
    ↓
requirements.md + spec.md 생성
    ↓
JIRA/Confluence 동기화
    ↓
Edge Case 질문 등록
```

---

## 🚀 빠른 시작

### 1단계: 의존성 설치

```bash
cd /Users/ai/vscode/egov-demo/scripts
pip install -r requirements.txt
```

### 2단계: Confluence API 토큰 설정

```bash
python confluence-sync.py config --set-token "ATATT3x..."

# 확인
python confluence-sync.py status
```

### 3단계: JIRA API 토큰 설정

```bash
python confluence-sync.py jira config --set-token "jira_api_token_here"

# 확인
python confluence-sync.py jira status
```

### 4단계: JIRA 이슈 검색

```bash
python confluence-sync.py jira search \
  --status "내부검토" \
  --document-types "요구사항정의서,유스케이스정의서"
```

---

## 🛠 JIRA API 클라이언트

### 클래스: `JiraAPI`

**기본 사용법:**

```python
from confluence.jira_api import JiraAPI

api = JiraAPI()

# 연결 테스트
api.test_connection()

# 상태별 이슈 검색
issues = api.get_issues_by_status(
    status="내부검토",
    document_types=["요구사항정의서", "유스케이스정의서"]
)

# 첨부파일 조회
attachments = api.get_attachments("GOVPJT-101")

# 댓글 등록
api.create_comment("GOVPJT-101", "자동 분석 결과:\n- 요구사항 34건 확인됨")

# 파일 첨부
api.attach_file("GOVPJT-101", "requirements.md", "requirements.md")

# Sub-task 생성
api.create_subtask(
    parent_issue_key="GOVPJT-101",
    summary="[Edge Case] 중복 신청 처리 정책 확인",
    description="관련 요구사항: REQ-FN-007\n..."
)
```

### 메서드 목록

| 메서드 | 설명 |
|--------|------|
| `test_connection()` | JIRA 연결 확인 |
| `get_issues_by_jql(jql)` | JQL 기반 이슈 검색 |
| `get_issues_by_status(status, document_types)` | 상태별 이슈 검색 |
| `get_issue_detail(issue_key)` | 이슈 상세 정보 조회 |
| `get_attachments(issue_key)` | 첨부파일 목록 조회 |
| `download_attachment(attachment_id, filename)` | 첨부파일 다운로드 |
| `create_comment(issue_key, comment_body)` | 댓글 등록 |
| `attach_file(issue_key, file_path, filename)` | 파일 첨부 |
| `create_subtask(parent_issue_key, summary, description)` | Sub-task 생성 |
| `update_custom_field(issue_key, field_name, value)` | 커스텀 필드 업데이트 |
| `transition_issue(issue_key, transition_id)` | 이슈 상태 변경 |
| `get_transitions(issue_key)` | 가능한 상태 전환 목록 |

---

## 🧪 테스트

### 단일 테스트 실행

```bash
cd /Users/ai/vscode/egov-demo/scripts
python -m confluence.test_jira_api
```

### 출력 예시

```
============================================================
█  JIRA API 클라이언트 테스트
============================================================

============================================================
1. JIRA 연결 테스트
============================================================
✅ JIRA 연결 성공
   Project: GOVPJT
   URL: https://nsonesoft.atlassian.net

============================================================
2. JIRA 설정 조회
============================================================
✅ 설정 조회 성공
   jira_url: https://nsonesoft.atlassian.net
   project_key: GOVPJT
   account: ${JIRA_EMAIL}
   token: jira_ap...xxxxx
```

---

## 📁 프로젝트 구조

```
/Users/ai/vscode/egov-demo/scripts/
├── confluence/
│   ├── api.py                      # Confluence API 클라이언트 (기존)
│   ├── config.py                   # 설정 관리
│   ├── sync.py                     # 동기화 로직
│   ├── converter.py                # 포맷 변환
│   ├── jira_api.py                 # ⭐ JIRA API (Phase 1-1)
│   ├── document_collector.py       # ⭐ 문서 수집기 (Phase 1-2)
│   ├── document_normalizer.py      # ⭐ 정규화 (Phase 2)
│   ├── speckit_runner.py           # (향후 Phase 3)
│   ├── test_jira_api.py            # JIRA API 테스트
│   ├── test_document_collector.py  # 수집기 테스트
│   └── test_document_normalizer.py # 정규화 테스트
│
├── confluence-sync.py              # CLI 메인 엔트리
├── requirements.txt                # Python 의존성
└── SDD_WORKFLOW.md                 # 본 문서
```

---

## 🔑 설정 파일

### Confluence 설정

**파일:** `~/.confluence-sync/config.json`

```json
{
  "confluence_url": "https://nsonesoft.atlassian.net",
  "space_key": "TNYUU",
  "folder_id": "661389353",
  "account": "${JIRA_EMAIL}",
  "local_folder": "/Users/ai/vscode/egov-demo/docs/00. confluence"
}
```

**토큰:** `~/.confluence-sync/.env`

```
CONFLUENCE_TOKEN=ATATT3x...
```

### JIRA 설정

**파일:** `~/.jira-sync/config.json`

```json
{
  "jira_url": "https://nsonesoft.atlassian.net",
  "project_key": "GOVPJT",
  "account": "${JIRA_EMAIL}"
}
```

**토큰:** `~/.jira-sync/.env`

```
JIRA_TOKEN=jira_api_token_here
```

---

## 📊 CLI 명령어 전체

### Confluence 명령

```bash
# 설정
python confluence-sync.py config --show
python confluence-sync.py config --set-token "CONFLUENCE_TOKEN"

# 상태 확인
python confluence-sync.py status

# 다운로드
python confluence-sync.py download
python confluence-sync.py download --force

# 업로드
python confluence-sync.py upload
python confluence-sync.py upload --dry-run

# 양방향 동기화
python confluence-sync.py sync
python confluence-sync.py sync --local-overwrite
python confluence-sync.py sync --confluence-overwrite
```

### JIRA 명령

```bash
# 설정
python confluence-sync.py jira config --show
python confluence-sync.py jira config --set-token "JIRA_TOKEN"

# 연결 확인
python confluence-sync.py jira status

# 이슈 검색
python confluence-sync.py jira search \
  --status "내부검토" \
  --document-types "요구사항정의서,유스케이스정의서,컴포넌트정의서"
```

### SDD 통합 워크플로우

```bash
# 1단계: 문서 수집 (Phase 1-2)
python confluence-sync.py sdd collect \
  --status "내부검토" \
  --document-types "요구사항정의서,유스케이스정의서,컴포넌트정의서" \
  --project-key "GOVPJT" \
  --workspace "/tmp/sdd-workspaces"

# 2단계: 문서 정규화 (Phase 2)
python confluence-sync.py sdd normalize \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

# 3단계: Speckit 자동화 (Phase 3)
python confluence-sync.py sdd specify \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

python confluence-sync.py sdd plan \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

python confluence-sync.py sdd tasks \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"
```

---

## 🛠 문서 수집기 (Phase 1-2)

### 기본 사용법

```python
from pathlib import Path
from confluence.document_collector import DocumentCollector

# Workspace 생성
workspace_dir = Path("/tmp/sdd-workspaces/RUN-20260611-001")

# 수집기 초기화
collector = DocumentCollector("RUN-20260611-001", workspace_dir)

# JIRA에서 문서 수집
jira_stats = collector.collect_from_jira_status(
    status="내부검토",
    document_types=["요구사항정의서", "유스케이스정의서"],
)

# Confluence에서 문서 수집 (선택)
confluence_stats = collector.collect_from_confluence([
    "https://nsonesoft.atlassian.net/wiki/spaces/TNYUU/pages/123456",
])

# 메타데이터 저장
metadata_file = collector.save_metadata(
    project_key="GOVPJT",
    target_status="내부검토",
    phase="collect",
)

# 통계 확인
stats = collector.get_stats()
print(f"수집된 문서: {stats['total_documents']}개")
```

---

## 📄 문서 정규화 (Phase 2)

**목표:** DOCX, XLSX, PPTX, HWPX, PDF → **Markdown** 자동 변환

### 지원 포맷

| 입력 형식 | 라이브러리 | 지원 여부 |
|---------|----------|---------|
| DOCX | python-docx | ✅ 완전 지원 |
| XLSX | openpyxl | ✅ 테이블 → Markdown |
| PPTX | python-pptx | ✅ 슬라이드별 추출 |
| HWPX | python-hwp | ⚠️ 부분 지원 (텍스트만) |
| PDF | PyPDF2 | ✅ 텍스트 추출 |
| HTML | html2text | ✅ 완전 지원 |
| Markdown | - | ✅ 통과 (복사) |

### 기본 사용법

```python
from pathlib import Path
from confluence.document_normalizer import DocumentNormalizer

input_dir = Path("/tmp/sdd-workspaces/RUN-20260611-001/input")
output_dir = Path("/tmp/sdd-workspaces/RUN-20260611-001/normalized")

# 정규화기 초기화
normalizer = DocumentNormalizer()

# 디렉터리 내 모든 문서 정규화
stats = normalizer.normalize_directory(input_dir, output_dir)

# 통계 확인
print(f"변환 성공: {stats['successful']}개")
print(f"변환 실패: {stats['failed']}개")
```

### Workspace 구조 (정규화 후)

```
RUN-20260611-001/
├── input/
│   ├── GOVPJT-101/
│   │   ├── 요구사항_v0.3.docx
│   │   └── 테스트_v0.1.xlsx
│   └── ...
│
├── normalized/                  # ⭐ 정규화된 출력
│   ├── GOVPJT-101/
│   │   ├── 요구사항_v0.3.md      # DOCX → Markdown
│   │   └── 테스트_v0.1.md        # XLSX → Markdown Table
│   └── ...
│
└── source-metadata.json
```

### DOCX → Markdown 예시

**입력 (요구사항정의서.docx):**
```
# 요구사항 정의서

## 1. 개요

| 항목 | 내용 |
|------|------|
| 프로젝트 | GOVPJT |
| 버전 | 1.0 |
```

**출력 (요구사항정의서.md):**
```markdown
# 요구사항 정의서

## 1. 개요

| 항목 | 내용 |
|------|------|
| 프로젝트 | GOVPJT |
| 버전 | 1.0 |
```

### XLSX → Markdown 예시

**입력 (requirements.xlsx):**

| ID | 요구사항 | 우선순위 |
|-----|---------|---------|
| REQ-001 | 사용자 로그인 | 높음 |
| REQ-002 | 문서 조회 | 보통 |

**출력 (requirements.md):**
```markdown
## requirements

| ID | 요구사항 | 우선순위 |
|---|---|---|
| REQ-001 | 사용자 로그인 | 높음 |
| REQ-002 | 문서 조회 | 보통 |
```

### DocumentNormalizer 클래스

**메서드:**

| 메서드 | 설명 |
|--------|------|
| `normalize_directory()` | 디렉터리의 모든 문서 정규화 |
| `_convert_docx()` | DOCX → Markdown |
| `_convert_xlsx()` | XLSX → Markdown Table |
| `_convert_pptx()` | PPTX → Markdown (슬라이드별) |
| `_convert_hwpx()` | HWPX → Markdown (부분) |
| `_convert_pdf()` | PDF → Markdown (텍스트 추출) |
| `_convert_html()` | HTML → Markdown |
| `get_stats()` | 정규화 통계 |

### Workspace 구조

```
RUN-20260611-001/
├── input/
│   ├── GOVPJT-101/
│   │   ├── 요구사항정의서_v0.3.hwpx
│   │   └── 테스트케이스_v0.1.xlsx
│   └── GOVPJT-102/
│       ├── 유스케이스정의서_v0.2.docx
│       └── 컴포넌트정의서_v0.4.pptx
│
└── source-metadata.json
```

### source-metadata.json 예시

```json
{
  "runId": "RUN-20260611-001",
  "projectKey": "GOVPJT",
  "targetStatus": "내부검토",
  "phase": "collect",
  "startedAt": "2026-06-11T10:30:45.123456",
  "sourceDocuments": [
    {
      "issue_key": "GOVPJT-101",
      "confluence_page_id": null,
      "document_type": "요구사항정의서",
      "source_file_name": "요구사항정의서_v0.3.hwpx",
      "source_version": "v0.3",
      "local_file_path": "input/GOVPJT-101/요구사항정의서_v0.3.hwpx",
      "checksum": "abc123def456",
      "downloaded_at": "2026-06-11T10:30:46.789012"
    }
  ],
  "notes": "자동 수집: 내부검토 상태의 문서"
}
```

### DocumentCollector 클래스

**메서드:**

| 메서드 | 설명 |
|--------|------|
| `collect_from_jira_status()` | JIRA 상태별 문서 수집 |
| `collect_from_confluence()` | Confluence 페이지 수집 |
| `save_metadata()` | 메타데이터 저장 (source-metadata.json) |
| `get_stats()` | 수집 통계 조회 |

**유틸리티:**

| 메서드 | 설명 |
|--------|------|
| `_infer_document_type()` | 파일명에서 문서 유형 자동 추론 |
| `_extract_version()` | 파일명에서 버전 정보 추출 |
| `_compute_checksum()` | 파일 체크섬 계산 |
| `_extract_page_id_from_url()` | Confluence 페이지 ID 추출 |

---

## 🧪 테스트

### Phase 1-2: 문서 수집기 테스트

```bash
python -m confluence.test_document_collector
```

**테스트 항목:**
- ✅ 유틸리티 메서드 (문서 유형 추론, 버전 추출, 페이지 ID 추출)
- ✅ 메타데이터 구조 (SourceDocument, SourceMetadata)
- ✅ JIRA 문서 수집 (실제 JIRA 연결)

### Phase 2: 문서 정규화 테스트

```bash
python -m confluence.test_document_normalizer
```

**테스트 항목:**
- ✅ 지원 포맷 확인
- ✅ Markdown 파일 통과 (복사)
- ✅ DOCX → Markdown 변환
- ✅ XLSX → Markdown Table 변환

---

## 🔐 보안

### 토큰 저장

- 토큰은 **절대 코드에 하드코딩하지 않음**
- 환경변수 우선: `CONFLUENCE_TOKEN`, `JIRA_TOKEN`
- 파일 저장: `~/.confluence-sync/.env`, `~/.jira-sync/.env` (권한: 600)

### 액세스 제어

```bash
# 토큰 파일 권한 확인
ls -la ~/.confluence-sync/.env
ls -la ~/.jira-sync/.env

# 출력 예시 (600 = 소유자만 읽기/쓰기)
# -rw------- 1 user staff 45 Jun 11 10:00 .env
```

---

## 🚦 상태 관리

### JIRA Kanban 상태

```
내부검토
  ↓ (Claude Specify 자동 실행)
요구사항보완
  ↓ (담당자 검토 & 수정)
보완완료
  ↓ (Claude Plan 자동 실행)
설계검토
  ↓ (PM 검토)
개발대기
```

### Claude SDD Status (Custom Field)

```
READY_TO_SPECIFY
  → SPECIFY_RUNNING
  → SPECIFY_DONE
  → NEEDS_CLARIFICATION (Edge Case 발견 시)
  → PLAN_RUNNING
  → PLAN_DONE
  → TASKS_RUNNING
  → TASKS_DONE
```

---

## 📈 향후 단계

### Phase 2: 문서 정규화 (document_normalizer.py)

```
입력 형식: HWPX, DOCX, XLSX, PPTX, Confluence HTML
  ↓
변환 엔진: python-docx, openpyxl, python-pptx
  ↓
출력 형식: Markdown
```

### Phase 3: Speckit 자동화 (speckit_runner.py)

```
Workspace 생성
  → /speckit.specify 실행
  → /speckit.plan 실행
  → /speckit.tasks 실행
```

---

## 📝 로그

### 로그 파일 위치

```
~/.confluence-sync/.confluence-sync.log
~/.jira-sync/.jira-sync.log
```

### 상세 로그 출력

```bash
python confluence-sync.py -v jira search \
  --status "내부검토" \
  --document-types "요구사항정의서"
```

---

## 🐛 문제 해결

### JIRA 연결 실패

```bash
# 1. 토큰 확인
cat ~/.jira-sync/.env

# 2. JIRA URL 확인
python confluence-sync.py jira config --show

# 3. 네트워크 연결 확인
curl -u ${JIRA_EMAIL}:TOKEN https://nsonesoft.atlassian.net/rest/api/3/myself
```

### 이슈 검색 결과 없음

```bash
# 현재 상태 확인
python confluence-sync.py jira search --status "전체" --document-types "모든"

# JQL 직접 테스트
# JIRA Web UI에서 이슈 > "고급" > JQL 입력:
# project = GOVPJT AND status = "내부검토" AND issuetype = Deliverable
```

---

## 📞 지원

문제가 발생하면:

1. 로그 파일 확인: `-v` 플래그로 상세 로그 출력
2. 연결 테스트: `jira status` 명령으로 JIRA 연결 확인
3. 설정 확인: `jira config --show` 명령으로 설정값 확인

---

## ⚡ Speckit 자동화 (Phase 3)

**목표:** Speckit 워크플로우 자동화 (`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`)

### SpeckitRunner 클래스

**메서드:**

| 메서드 | 목적 |
|--------|------|
| `initialize_workspace()` | Speckit Workspace 초기화 |
| `run_specify()` | `/speckit.specify` 자동 실행 |
| `run_plan()` | `/speckit.plan` 자동 실행 |
| `run_tasks()` | `/speckit.tasks` 자동 실행 |
| `get_execution_log()` | 실행 로그 조회 |
| `save_execution_log()` | 실행 로그 저장 |

### Workspace 구조 (자동화 후)

```
RUN-20260611-ABC/
├── input/                           # 원본 문서
├── normalized/                      # 정규화된 Markdown
├── specs/                           # ⭐ Speckit 생성 파일
│   ├── requirements.md              # Specify 결과
│   ├── spec.md
│   ├── edge_cases.md
│   ├── plan.md                      # Plan 결과
│   ├── component_spec.md
│   ├── data_model.md
│   ├── TDD.md
│   └── tasks.md                     # Tasks 결과
│
├── .specify/
│   └── config.json                  # Speckit 설정
│
├── speckit-execution.json           # 실행 로그
└── source-metadata.json
```

### CLI 명령어

```bash
# Phase 3-1: Specify 실행 (요구사항 체계화)
python scripts/confluence-sync.py sdd specify \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

# Phase 3-2: Plan 실행 (설계 계획)
python scripts/confluence-sync.py sdd plan \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"

# Phase 3-3: Tasks 실행 (작업 분해)
python scripts/confluence-sync.py sdd tasks \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-ABC"
```

### 출력 예시

```
📋 Speckit Specify 실행
   Run ID: RUN-20260611-ABC

🔧 Workspace 초기화 중...
✓ Workspace 초기화 완료

📋 /speckit.specify 실행 중...

✅ Specify 실행 완료
─────────────────────────────
  생성된 파일: 3개
    - requirements.md
    - spec.md
    - edge_cases.md
─────────────────────────────
```

### Speckit 생성 파일 설명

| 파일 | 설명 |
|------|------|
| **requirements.md** | 요구사항 정의 (REQ-FN-001, REQ-NF-001 등) |
| **spec.md** | 상세 명세 (유스케이스, 기술 스택) |
| **edge_cases.md** | 모호한 항목 및 확인 질문 |
| **plan.md** | 구현 계획 (Phase별 작업) |
| **component_spec.md** | 컴포넌트 설계 (Controller, Service, DAO) |
| **data_model.md** | 데이터베이스 모델 정의 |
| **TDD.md** | 테스트 전략 및 테스트케이스 |
| **tasks.md** | 구현 작업 분해 (Story별 Sub-task) |

---

## 📊 구현 진행률

```
Phase 1-1: JIRA API 클라이언트          ✅ 완료 (14개 메서드)
Phase 1-2: 문서 수집기                  ✅ 완료 (메타데이터 관리)
Phase 2:   문서 정규화                  ✅ 완료 (7개 포맷 지원)
Phase 3:   Speckit 자동화               ✅ 완료 (3개 명령)

전체 구현 완료: 4개 Phase, 총 15개 모듈
```
