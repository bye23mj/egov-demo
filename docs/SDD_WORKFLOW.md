# SDD (Spec-Driven Development) 워크플로우

> **자동화된 요구사항 수집 → 정규화 → 명세 생성 → 계획 수립 파이프라인**
>
> JIRA 보드의 문서를 자동 수집하고, Confluence 동기화, 품질 개선, 요구사항 추출까지
> 4단계로 자동화된 SDD 파이프라인

---

## 📋 목차

1. [시스템 개요](#시스템-개요)
2. [프로젝트 구조](#프로젝트-구조)
3. [4단계 파이프라인](#4단계-파이프라인)
4. [사용 방법](#사용-방법)
5. [메타데이터 구조](#메타데이터-구조)
6. [확장 및 커스터마이징](#확장-및-커스터마이징)

---

## 시스템 개요

### 목표

전자정부표준프레임워크 기반 프로젝트에서:
- **JIRA 보드**의 요구사항 문서를 자동 수집
- **Confluence** 동기화 및 HTML 파싱으로 품질 개선
- 자동으로 **명세서** 및 **계획서** 생성

### 주요 특징

| 기능 | 설명 |
|------|------|
| **자동 수집** | JIRA API + Confluence API로 문서 자동 다운로드 |
| **REQID 관리** | JIRA 필드 → 제목 → Confluence → 자동생성의 4단계 추출 |
| **첨부파일 지원** | PDF, DOCX, XLSX, PPTX, HWPX, HWP 등 13+ 형식 |
| **품질 개선** | HTML 파싱으로 60점 → 88점 달성 |
| **메타데이터 추적** | 모든 문서의 출처, 생성일시, 체크섬 기록 |
| **폴더 구조** | `{프로젝트}/{이슈키}/{REQID}/` 일관성 있는 구조 |

---

## 프로젝트 구조

### 디렉토리 레이아웃

```
egov-demo/
├── scripts/                              # SDD 파이프라인 스크립트
│   ├── sdd_collect_with_confluence.py    # Phase 1: 문서 수집
│   ├── sdd_extract_reqid.py              # 유틸: REQID 추출
│   ├── sdd_normalize_documents.py        # Phase 2: 문서 정규화 (v1)
│   ├── sdd_normalize_documents_v2.py     # Phase 2: 문서 정규화 (v2) - HTML 파싱
│   ├── sdd_generate_specification.py     # Phase 3: 명세 생성
│   └── sdd_generate_planning.py          # Phase 4: 계획 생성
│
├── docs/
│   └── 00. confluence/                   # SDD 작업 디렉토리
│       ├── source-metadata.json          # Phase 1 수집 메타데이터
│       ├── normalized-metadata.json      # Phase 2 정규화 결과
│       ├── specification.json            # Phase 3 명세
│       ├── planning.json                 # Phase 4 계획
│       └── {프로젝트}/{이슈키}/{REQID}/  # 수집된 문서 저장
│           ├── {문서}.md
│           ├── {문서}.docx
│           └── ...
│
├── .claude/
│   └── docs/
│       └── SDD_WORKFLOW.md               # 이 파일
│
└── README.md
```

### 주요 파일 설명

| 파일 | 용도 | 입력 | 출력 |
|------|------|------|------|
| `sdd_collect_with_confluence.py` | Phase 1: 문서 수집 | JIRA Board API | `source-metadata.json` + 문서 다운로드 |
| `sdd_extract_reqid.py` | REQID 추출 유틸 | 텍스트 | REQID 문자열 |
| `sdd_normalize_documents.py` | Phase 2: 정규화 (v1) | `source-metadata.json` | `normalized-metadata.json` |
| `sdd_normalize_documents_v2.py` | Phase 2: 정규화 (v2) | 마크다운 파일 | 개선된 `normalized-metadata.json` |
| `sdd_generate_specification.py` | Phase 3: 명세 생성 | `normalized-metadata.json` | `specification.json` + SPEC-*.md |
| `sdd_generate_planning.py` | Phase 4: 계획 생성 | `specification.json` | `planning.json` + 태스크 리스트 |

---

## 4단계 파이프라인

### Phase 1️⃣: 문서 수집 (Collection)

**목표**: JIRA 보드에서 요구사항 문서를 자동으로 다운로드

**실행**:
```bash
python3 scripts/sdd_collect_with_confluence.py
```

**처리 과정**:

1. **JIRA 보드 조회** (`agile/1.0/board/{board_id}/issue`)
   - 프로젝트: MZ2026
   - 상태: 내부검토 (In Review)
   - 필드: 첨부파일, 설명, 커스텀 필드

2. **REQID 자동 추출** (4단계 우선순위)
   ```
   우선순위 1: JIRA 커스텀 필드 (customfield_10431)
             ↓
   우선순위 2: 이슈 제목 (정규식 "ERP-001", "REQ-123" 등)
             ↓
   우선순위 3: Confluence 페이지 메타데이터
             ↓
   우선순위 4: 자동 생성 (REQ-{이슈번호})
   ```

3. **문서 다운로드**
   - **JIRA 첨부파일**: `/rest/api/2/attachment/{id}`로 다운로드
   - **Confluence 페이지**: `/wiki/rest/api/content/{page_id}?expand=body.view`로 다운로드
   - 지원 형식: PDF, DOCX, XLSX, PPTX, HWPX, HWP, DOC, XLS, PPT, TXT, XML, JSON, CSV

4. **폴더 구조 생성**
   ```
   docs/00. confluence/
   └── {프로젝트}/{이슈키}/{REQID}/
       ├── {문서1}.md
       ├── {문서2}.docx
       └── ...
   ```

**출력**: `source-metadata.json`

**지원 상태**: ✅ 완료 (v4 최종)

---

### Phase 2️⃣: 문서 정규화 (Normalization)

**목표**: 다운로드한 문서를 분석하고 품질 점수 평가

**실행**:
```bash
python3 scripts/sdd_normalize_documents_v2.py
```

**처리 과정**:

1. **HTML 파싱** (v2 신기능)
   - BeautifulSoup으로 HTML 구조 분석
   - `<h1>~<h6>` → 섹션 추출
   - `<table>` → 표 감지 및 카운팅
   - `<ul>`, `<ol>` → 리스트 구조 유지
   - `<img>` → 이미지 링크 추출

2. **메타데이터 자동 추출**
   ```
   정규식으로 다음 필드 자동 추출:
   - 산출물ID
   - 버전
   - 담당자
   - 상태
   - 프로젝트
   - 작성일
   ```

3. **품질 점수 계산** (0~100점)
   ```
   기본점수: 50점
   ├─ 문서 크기: +10~20점 (50줄 이상)
   ├─ 섹션 구조: +5~20점 (3개 이상)
   ├─ 표: +10점 (1개 이상)
   ├─ 링크: +5점 (1개 이상)
   ├─ 메타데이터: +15점 (6개 필드 완성)
   ├─ 가독성: +10점 (코드블록, 리스트, 이미지)
   └─ HTML 요소: +8점 (표 3개, 이미지 등)
   
   예시: 60점 → 88점 (28점 상향)
   ```

4. **정규화 결과 저장**
   - 구조화된 메타데이터
   - 품질 평가 점수
   - 누락 요소 목록

**출력**: `normalized-metadata.json` (v2.0)

**지원 상태**: ✅ 완료 (v2.0 - HTML 파싱 포함)

---

### Phase 3️⃣: 명세 생성 (Specification)

**목표**: 정규화된 문서에서 요구사항을 추출하고 명세서 생성

**실행**:
```bash
python3 scripts/sdd_generate_specification.py
```

**처리 과정**:

1. **요구사항 자동 분류**
   - FUNCTIONAL (기능)
   - SECURITY (보안)
   - INTEGRATION (연계)
   - PERFORMANCE (성능)
   - DATA (데이터)
   - OPERATIONAL (운영)

2. **명세서 생성**
   ```
   SPEC-{REQID}.md 파일 생성:
   ├─ 요구사항 요약
   ├─ 상세 요구사항 테이블
   ├─ 검증 기준
   └─ 관련 이슈 링크
   ```

3. **메타데이터 통합**
   - 출처: 원본 문서 추적
   - 버전: 변경 이력 관리
   - 상태: 검토/승인 상태

**출력**: `specification.json` + `SPEC-*.md`

**지원 상태**: ✅ 완료

---

### Phase 4️⃣: 계획 생성 (Planning)

**목표**: 명세 요구사항을 실행 가능한 태스크로 변환

**실행**:
```bash
python3 scripts/sdd_generate_planning.py
```

**처리 과정**:

1. **자동 태스크 생성**
   각 요구사항마다:
   - 설계 (Design)
   - 개발 (Development)
   - 테스트 (Testing)
   - QA (Quality Assurance)
   - 문서화 (Documentation)

2. **일정 계산**
   ```
   기준: 하루 6시간 생산성
   
   예시:
   - 설계: 2일 (12시간)
   - 개발: 5일 (30시간)
   - 테스트: 3일 (18시간)
   - QA: 2일 (12시간)
   - 문서: 1일 (6시간)
   ─────────────
   합계: 13일 (78시간)
   ```

3. **주간 분해** (Weekly Breakdown)

**출력**: `planning.json`

**지원 상태**: ✅ 완료

---

## 사용 방법

### 전체 파이프라인 실행

```bash
#!/bin/bash
# 환경 변수 설정
export JIRA_EMAIL="bye23mj@nsonesoft.com"
export JIRA_TOKEN="your-token"
export JIRA_BOARD_ID="427"

# 1. Phase 1: 문서 수집
python3 scripts/sdd_collect_with_confluence.py

# 2. Phase 2: 문서 정규화
python3 scripts/sdd_normalize_documents_v2.py

# 3. Phase 3: 명세 생성
python3 scripts/sdd_generate_specification.py

# 4. Phase 4: 계획 생성
python3 scripts/sdd_generate_planning.py

# 5. Git 커밋
git add docs/
git commit -m "feat: SDD 파이프라인 실행"
```

### 단계별 실행

#### Step 1: Phase 1 (수집)

```bash
python3 scripts/sdd_collect_with_confluence.py
```

**결과**:
```
docs/00. confluence/
├── source-metadata.json
└── MZ2026-1/ERP-001/
    ├── ERP-001 요구사항정의서.md
    └── EPR-001 화면정의서.docx
```

#### Step 2: Phase 2 (정규화)

```bash
python3 scripts/sdd_normalize_documents_v2.py
```

**결과**:
```
품질 점수: 60점 → 88점 ✅
```

#### Step 3: Phase 3 (명세)

```bash
python3 scripts/sdd_generate_specification.py
```

**결과**:
```
specification.json + SPEC-ERP-001.md
```

#### Step 4: Phase 4 (계획)

```bash
python3 scripts/sdd_generate_planning.py
```

**결과**:
```
planning.json (13일, 78시간 일정)
```

---

## 메타데이터 구조

### source-metadata.json (Phase 1 출력)

```json
{
  "runId": "REQ-MZ2026-20260612-142021",
  "projectKey": "MZ2026",
  "targetStatus": "내부검토",
  "phase": "1-collect",
  "summary": {
    "totalIssues": 2,
    "jiraAttachments": 1,
    "confluencePages": 1,
    "totalDocuments": 2
  },
  "sourceDocuments": [
    {
      "type": "jira_attachment",
      "issue": "MZ2026-1",
      "reqid": "ERP-001",
      "reqid_source": "JIRA_FIELD",
      "filename": "EPR-001 화면정의서.docx",
      "file_path": "docs/00. confluence/MZ2026-1/ERP-001/...",
      "size": 1321
    }
  ]
}
```

### normalized-metadata.json (Phase 2 출력)

```json
{
  "runId": "REQ-MZ2026-20260612-142021",
  "phase": "2-normalize",
  "version": "2.0",
  "statistics": {
    "total_documents": 1,
    "average_quality_score": 88.0
  },
  "documents": [
    {
      "title": "ERP-001 요구사항정의서",
      "quality_score": 88.0,
      "structure": {
        "sections": 6,
        "html_elements": {
          "headings": 7,
          "tables": 3
        }
      },
      "metadata": {
        "산출물ID": "ERP-001",
        "버전": "v1.0"
      }
    }
  ]
}
```

### specification.json (Phase 3 출력)

```json
{
  "phase": "3-specification",
  "specifications": [
    {
      "specId": "SPEC-ERP-001",
      "requirements": [
        {
          "id": "REQ-001",
          "category": "FUNCTIONAL",
          "description": "...",
          "priority": "HIGH"
        }
      ]
    }
  ]
}
```

### planning.json (Phase 4 출력)

```json
{
  "phase": "4-planning",
  "projectTimeline": {
    "startDate": "2026-06-16",
    "estimatedEndDate": "2026-07-03",
    "totalDays": 13,
    "totalHours": 78
  },
  "tasks": [
    {
      "taskId": "DESIGN-ERP-001",
      "type": "DESIGN",
      "estimatedHours": 12
    }
  ]
}
```

---

## 기술 스택

| 항목 | 기술 |
|------|------|
| **언어** | Python 3.10+ |
| **JIRA API** | REST API v2 + Agile 1.0 |
| **Confluence API** | Cloud Content API |
| **HTML 파싱** | BeautifulSoup4 + html2text |
| **인증** | Bearer Token |
| **메타데이터** | JSON |
| **버전 관리** | Git |

---

## 완료 현황

| Phase | 작업 | 상태 |
|-------|------|------|
| **1** | 문서 수집 (JIRA + Confluence) | ✅ 완료 |
| **2** | 문서 정규화 + 품질 개선 (HTML 파싱) | ✅ 완료 |
| **3** | 명세 생성 (요구사항 추출) | ✅ 완료 |
| **4** | 계획 생성 (일정/태스크) | ✅ 완료 |

---

**최종 업데이트**: 2026-06-12  
**버전**: 2.0 (HTML 파싱 + 메타데이터 추출)
