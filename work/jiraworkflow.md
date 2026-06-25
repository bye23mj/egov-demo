# JIRA Workflow Guide — egov-demo

> **JIRA + Confluence + SDD 자동화 통합 가이드**
>
> 이 문서는 egov-demo 프로젝트에서 JIRA를 활용한 요구사항 수집, 정규화, 명세화 전체 워크플로우를 설명합니다.

---

## 1. 초기 설정

### 1.1 JIRA 토큰 설정

#### 방법 1: 환경변수로 설정 (권장)

```bash
export JIRA_EMAIL="bye23mj@gmail.com"
export JIRA_TOKEN="your-jira-api-token"
```

#### 방법 2: 설정 파일로 설정

```bash
mkdir -p ~/.jira-sync
cat > ~/.jira-sync/.env << 'EOF'
JIRA_EMAIL=bye23mj@gmail.com
JIRA_TOKEN=your-jira-api-token
JIRA_INSTANCE_URL=https://your-instance.atlassian.net
EOF

chmod 600 ~/.jira-sync/.env
```

### 1.2 JIRA 토큰 발급 방법

1. [Atlassian API 토큰 페이지](https://id.atlassian.com/manage-profile/security/api-tokens) 접속
2. "Create API token" 클릭
3. 토큰명 입력 (예: `egov-demo-sdd`)
4. 생성된 토큰 복사 → `JIRA_TOKEN` 환경변수에 저장
5. 설정 파일 권한: `chmod 600 ~/.jira-sync/.env`

---

## 2. JIRA API 사용법

### 2.1 Python 클라이언트 활용

```python
from scripts.confluence.jira_api import JiraAPI, JiraConfig

# JIRA 설정 로드
config = JiraConfig()

# JiraAPI 인스턴스 생성
jira = JiraAPI(config)

# 연결 테스트
jira.test_connection()
# → ✓ JIRA 연결 성공

# JIRA 이슈 조회
issues = jira.get_issues_by_status(
    status="Backlog",
    project="GOVPJT",
    max_results=10
)

for issue in issues:
    print(f"{issue['key']}: {issue['summary']}")
    # → GOVPJT-101: 사용자 목록 조회 기능
    # → GOVPJT-102: 사용자 등록 기능
```

### 2.2 주요 메서드

| 메서드 | 설명 | 사용례 |
|-------|------|-------|
| `test_connection()` | JIRA 연결 테스트 | API 초기화 후 확인 |
| `get_issues_by_status(status, project)` | 상태별 이슈 조회 | Backlog 상태 이슈 검색 |
| `get_issue_detail(issue_key)` | 이슈 상세 정보 | GOVPJT-101 상세 정보 조회 |
| `get_attachments(issue_key)` | 첨부파일 목록 | 이슈의 문서 파일 조회 |
| `download_attachment(url, output_path)` | 첨부파일 다운로드 | 문서 수집 |
| `create_comment(issue_key, comment)` | 주석 추가 | 진행 상황 업데이트 |
| `attach_file(issue_key, file_path)` | 파일 업로드 | 생성 문서 첨부 |
| `create_subtask(issue_key, summary)` | 서브태스크 생성 | 작업 분해 |
| `transition_issue(issue_key, status)` | 상태 전환 | Done으로 변경 |

---

## 3. SDD 통합 워크플로우

### 3.1 전체 흐름도

```
┌─────────────────────────────────────────────────────────┐
│                    JIRA (Confluence 연계)                │
│  • 요구사항 이슈: GOVPJT-101, GOVPJT-102, ...           │
│  • 첨부파일: DOCX, XLSX, PPTX, PDF, HWPX 등            │
└────────────────────────┬────────────────────────────────┘
                         │
                    /sdd-collect
                    (Phase 1)
                         │
            ┌────────────▼─────────────┐
            │   input/{ISSUE-KEY}/     │
            │   ├── requirements.docx  │
            │   ├── design.pptx        │
            │   └── data_model.xlsx    │
            │                          │
            │  source-metadata.json    │
            └────────────┬─────────────┘
                         │
                    /sdd-normalize
                    (Phase 2)
                         │
            ┌────────────▼─────────────┐
            │  normalized/             │
            │  ├── requirements.md     │
            │  ├── design.md           │
            │  └── data_model.md       │
            └────────────┬─────────────┘
                         │
                    /sdd-specify
                    (Phase 3)
                         │
            ┌────────────▼──────────────┐
            │  specs/                   │
            │  ├── requirements.md      │
            │  ├── spec.md              │
            │  └── edge_cases.md        │
            └────────────┬──────────────┘
                         │
                    /sdd-plan
                    (Phase 4)
                         │
            ┌────────────▼──────────────────┐
            │  specs/                       │
            │  ├── plan.md                  │
            │  ├── component_spec.md        │
            │  ├── data_model.md            │
            │  └── TDD.md                   │
            └────────────┬──────────────────┘
                         │
                    /sdd-tasks
                    (Phase 5)
                         │
            ┌────────────▼──────────────┐
            │  specs/                   │
            │  └── tasks.md             │
            │     (T001~T033 분해)      │
            └───────────────────────────┘
```

### 3.2 각 Phase별 특징

#### Phase 1: Document Collection
```
목적: JIRA 이슈에서 문서 수집
입력: JIRA 이슈 (Backlog, Todo, In Progress)
출력: input/{ISSUE-KEY}/files + source-metadata.json
시간: ~2-3분 (5개 이슈 기준)

예시:
$ /sdd-collect
  Status: Backlog
  Document Types: ALL
  Workspace: /tmp/sdd-workspaces
  
  ✅ GOVPJT-101 (3개 문서 다운로드)
  ✅ GOVPJT-102 (2개 문서 다운로드)
  ✅ GOVPJT-103 (1개 문서 다운로드)
```

#### Phase 2: Document Normalization
```
목적: 다양한 형식의 문서를 Markdown으로 통일
입력: input/{ISSUE-KEY}/ (DOCX, XLSX, PPTX, HWPX, PDF)
출력: normalized/ (모두 .md 형식)
시간: ~1-2분

지원 형식:
  ✓ DOCX (Word) → Markdown
  ✓ XLSX (Excel) → Markdown 테이블
  ✓ PPTX (PowerPoint) → Markdown 슬라이드
  ✓ HWPX (한글) → Markdown (부분)
  ✓ PDF → Markdown (텍스트 추출)
  ✓ HTML → Markdown
  ✓ Markdown → 그대로
```

#### Phase 3: Specification
```
목적: 정규화된 문서에서 요구사항 추출 및 체계화
입력: normalized/ (Markdown 문서)
출력: specs/{requirements.md, spec.md, edge_cases.md}
시간: ~3-5분

생성 내용:
  • requirements.md
    - REQ-FN-001: 기능 요구사항
    - REQ-NF-001: 비기능 요구사항
    - REQ-SEC-001: 보안 요구사항
  
  • spec.md
    - 시스템 아키텍처
    - API 스펙
    - 데이터 모델
  
  • edge_cases.md
    - 모호한 항목
    - 추가 확인 필요 사항
```

#### Phase 4: Planning
```
목적: 설계 계획 수립 및 컴포넌트 정의
입력: specs/requirements.md, spec.md
출력: specs/{plan.md, component_spec.md, data_model.md, TDD.md}
시간: ~5-10분

생성 내용:
  • plan.md
    - Phase별 일정 (Phase 1~5)
    - Story 분해 (Story 1~N)
    - 마일스톤
  
  • component_spec.md
    - Controller 설계
    - Service/ServiceImpl 설계
    - DAO/Mapper 설계
    - VO 정의
  
  • data_model.md
    - 테이블 정의 (CREATE TABLE)
    - 컬럼 정의
    - Sequence 정의
    - Index 정의
  
  • TDD.md
    - 테스트 전략
    - Unit Test 목록
    - Integration Test 목록
```

#### Phase 5: Task Breakdown
```
목적: 개발 작업 분해
입력: specs/plan.md, component_spec.md
출력: specs/tasks.md
시간: ~5-7분

생성 내용:
  Story 1: 사용자 목록 조회
  ├── T001: Controller 작성
  ├── T002: Service 인터페이스 정의
  ├── T003: ServiceImpl 구현
  ├── T004: DAO 인터페이스 정의
  ├── T005: Mapper XML 작성
  ├── T006: SQL 쿼리 검증
  ├── T007: 페이징 기능 추가
  ├── T008: 단위 테스트 작성
  └── T009: 통합 테스트
  
  Story 2: 사용자 등록
  └── T010~T018 (9개 Sub-task)
```

---

## 4. 실제 사용 예시

### 4.1 시나리오: 전자정부 요구사항 자동화

```bash
# Step 1: JIRA 설정 확인
export JIRA_EMAIL="bye23mj@gmail.com"
export JIRA_TOKEN="your-api-token"

# Step 2: 문서 수집
/sdd-collect
  Status: Backlog
  Document Types: DOCX,XLSX,PPTX
  Workspace: /tmp/sdd-workspaces
  Requirement ID: REQ-GOVPJT-20260611

# Step 3: 정규화
/sdd-normalize
  workspace: /tmp/sdd-workspaces
  requirement_id: REQ-GOVPJT-20260611

# Step 4: 요구사항 명세화
/sdd-specify
  run_id: /tmp/sdd-workspaces/REQ-GOVPJT-20260611

# Step 5: 설계 계획
/sdd-plan
  run_id: /tmp/sdd-workspaces/REQ-GOVPJT-20260611

# Step 6: 작업 분해
/sdd-tasks
  run_id: /tmp/sdd-workspaces/REQ-GOVPJT-20260611

# Step 7: 결과 확인
ls -la /tmp/sdd-workspaces/REQ-GOVPJT-20260611/specs/
# ├── requirements.md (30개 요구사항)
# ├── spec.md (2400줄)
# ├── edge_cases.md (12개 미결정)
# ├── plan.md (5개 Phase, 4개 Story)
# ├── component_spec.md (Controller/Service/DAO 설계)
# ├── data_model.md (5개 테이블)
# ├── TDD.md (테스트 전략)
# └── tasks.md (33개 Sub-task)
```

### 4.2 메타데이터 활용

수집된 모든 문서의 메타데이터는 `source-metadata.json`에 저장됩니다.

```json
{
  "run_id": "REQ-GOVPJT-20260611",
  "project_key": "GOVPJT",
  "target_status": "Backlog",
  "phase": "collect",
  "started_at": "2026-06-11T10:30:00Z",
  "completed_at": "2026-06-11T10:35:00Z",
  "source_documents": [
    {
      "issue_key": "GOVPJT-101",
      "document_type": "DOCX",
      "source_file_name": "requirements.docx",
      "local_file_path": "input/GOVPJT-101/requirements.docx",
      "checksum": "abc123def456",
      "downloaded_at": "2026-06-11T10:31:00Z"
    }
  ]
}
```

이를 통해:
- 각 문서의 출처 추적
- 버전 관리 및 변경 감지
- 감사(Audit) 추적

---

## 5. CLI 명령어 참고

### 5.1 JIRA 상태 조회

```bash
python scripts/confluence/confluence-sync.py jira status
```

출력:
```
✓ JIRA 연결 성공
Instance: https://your-instance.atlassian.net
User: bye23mj@gmail.com
```

### 5.2 JIRA 이슈 검색

```bash
python scripts/confluence/confluence-sync.py jira search \
  --project GOVPJT \
  --status Backlog \
  --max-results 10
```

출력:
```
GOVPJT-101: 사용자 목록 조회 기능
GOVPJT-102: 사용자 등록 기능
GOVPJT-103: 사용자 수정 기능
...
```

### 5.3 특정 이슈 상세 정보

```bash
python scripts/confluence/confluence-sync.py jira detail \
  --issue-key GOVPJT-101
```

출력:
```
Key: GOVPJT-101
Summary: 사용자 목록 조회 기능
Status: Backlog
Description: ...
Attachments:
  - requirements.docx (204 KB)
  - design.pptx (1.2 MB)
```

---

## 6. 문제 해결

### 6.1 JIRA 연결 실패

**증상:**
```
Error: JIRA API 연결 실패
```

**원인 및 해결:**
```bash
# 1. 환경변수 확인
echo $JIRA_EMAIL
echo $JIRA_TOKEN

# 2. 설정 파일 확인
cat ~/.jira-sync/.env

# 3. 네트워크 연결 확인
curl -I https://your-instance.atlassian.net

# 4. 토큰 재발급
# → Atlassian API 토큰 페이지에서 새 토큰 생성
```

### 6.2 문서 다운로드 실패

**증상:**
```
Error: 첨부파일 다운로드 실패 (403 Forbidden)
```

**원인 및 해결:**
```bash
# 1. 권한 확인
# → JIRA 프로젝트 접근 권한 확인

# 2. 파일 크기 제한
# → 대용량 파일의 경우 JIRA 설정 확인

# 3. 캐시 초기화
rm -rf /tmp/sdd-workspaces/
```

### 6.3 정규화 실패

**증상:**
```
Error: HWPX 파일 변환 실패
```

**원인 및 해결:**
```bash
# 1. Python 라이브러리 확인
pip list | grep python-pptx
pip list | grep openpyxl

# 2. 누락 라이브러리 설치
pip install python-pptx openpyxl python-docx PyPDF2

# 3. 재시도
/sdd-normalize
```

---

## 7. 권장 사항

### 7.1 JIRA 프로젝트 구조

```
프로젝트: GOVPJT (전자정부 프로젝트)

백로그:
├── Epic 1: 사용자 관리 기능
│   ├── GOVPJT-101: 사용자 목록 조회
│   ├── GOVPJT-102: 사용자 등록
│   └── GOVPJT-103: 사용자 수정
├── Epic 2: 게시판 관리 기능
│   ├── GOVPJT-104: 게시물 목록
│   ├── GOVPJT-105: 게시물 등록
│   └── GOVPJT-106: 댓글 관리

각 이슈에 첨부:
├── 요구사항 문서 (requirements.docx)
├── 설계 다이어그램 (design.pptx)
├── 데이터 모델 (data_model.xlsx)
└── 상세 명세 (specification.pdf)
```

### 7.2 자동화 주기

```
권장 주기:
• 일일: /sdd-collect (최신 요구사항 수집)
• 주 1회: /sdd-normalize (정규화)
• 주 1회: /sdd-specify (명세화)
• 월 1회: /sdd-plan (계획 수립)
• 월 1회: /sdd-tasks (작업 분해)
```

### 7.3 품질 관리

```
검증 체크리스트:
- [ ] 모든 이슈의 첨부파일이 다운로드되었는가?
- [ ] 정규화된 문서가 원본과 일치하는가?
- [ ] 생성된 요구사항이 비즈니스 요구를 반영하는가?
- [ ] 설계가 기존 시스템과 통합 가능한가?
- [ ] 작업 분해가 현실적인 일정인가?
```

---

## 8. API 참고

### 8.1 JiraAPI 전체 메서드

```python
from scripts.confluence.jira_api import JiraAPI

# 필수 메서드
jira.test_connection()                    # 연결 테스트
jira.get_issues_by_status(status, ...)    # 상태별 조회
jira.get_issue_detail(issue_key)          # 상세 정보
jira.get_attachments(issue_key)           # 첨부파일 목록
jira.download_attachment(url, path)       # 다운로드

# 선택 메서드 (이후 단계)
jira.create_comment(issue_key, text)      # 주석 추가
jira.attach_file(issue_key, path)         # 파일 업로드
jira.create_subtask(issue_key, summary)   # 서브태스크
jira.update_custom_field(issue_key, ...)  # 커스텀 필드
jira.transition_issue(issue_key, status)  # 상태 전환
jira.get_transitions(issue_key)           # 가능 상태 조회
```

### 8.2 설정 파일 위치

```
~/.jira-sync/.env              # JIRA 토큰
/tmp/sdd-workspaces/           # 기본 workspace
/tmp/sdd-workspaces/RUN-*/     # 실행별 폴더
```

---

## 9. 다음 단계

1. **초기 설정 완료**: JIRA 토큰 설정
2. **첫 실행**: `/sdd-collect` → 문서 수집
3. **검증**: `source-metadata.json` 확인
4. **자동화**: `/sdd-normalize` → `/sdd-tasks` 순차 실행
5. **통합**: 생성된 명세를 eGov 프로젝트에 적용

---

**마지막 업데이트**: 2026-06-11
**버전**: 1.0.0
