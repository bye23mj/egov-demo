# SDD 파이프라인 아키텍처

## 데이터 흐름도 (Data Flow)

```
┌─────────────────────────────────────────────────────────────────┐
│                       JIRA / Confluence                          │
│                                                                   │
│  Board: MZ2026 (Status: 내부검토)                               │
│  - Issues: MZ2026-1, MZ2026-10, ...                             │
│  - Attachments: PDF, DOCX, XLSX, ...                            │
│  - Pages: ERP-001 요구사항정의서, ...                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1️⃣: 문서 수집 (sdd_collect_with_confluence.py)          │
│                                                                   │
│  1. JIRA Board API 조회 (agile/1.0/board/427/issue)            │
│  2. REQID 추출 (4단계 우선순위)                                  │
│  3. JIRA 첨부파일 다운로드 (/rest/api/2/attachment/)           │
│  4. Confluence 페이지 다운로드 (/wiki/rest/api/content/)       │
│  5. 폴더 구조 생성 ({REQID} 기반)                               │
│  6. 메타데이터 저장 (source-metadata.json)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        docs/00. confluence/
        ├── source-metadata.json
        ├── MZ2026-1/ERP-001/
        │   ├── ERP-001 요구사항정의서.md (원본 HTML)
        │   └── EPR-001 화면정의서.docx
        └── MZ2026-10/REQ-2026/
                              
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2️⃣: 문서 정규화 (sdd_normalize_documents_v2.py)         │
│                                                                   │
│  1. HTML 파싱 (BeautifulSoup4)                                  │
│     - 제목/섹션 추출 (h1~h6)                                    │
│     - 표 감지 (table)                                           │
│     - 리스트 구조 (ul, ol)                                      │
│     - 이미지 링크 (img)                                         │
│                                                                   │
│  2. 메타데이터 추출 (정규식)                                     │
│     - 산출물ID, 버전, 담당자, 상태, 프로젝트, 작성일            │
│                                                                   │
│  3. 품질 점수 계산 (0~100)                                      │
│     - 기본: 50점                                                │
│     - 크기: +10~20점                                            │
│     - 섹션: +5~20점                                             │
│     - 표/링크: +10~15점                                         │
│     - 메타데이터: +15점                                         │
│     - 가독성: +10점                                             │
│     → 결과: 60점 → 88점 달성                                    │
│                                                                   │
│  4. Markdown 파일 개선                                          │
│  5. 정규화 메타데이터 저장 (normalized-metadata.json v2.0)     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        docs/00. confluence/
        ├── normalized-metadata.json (v2.0)
        └── MZ2026-1/ERP-001/
            ├── ERP-001 요구사항정의서.md (개선됨)
            └── EPR-001 화면정의서.docx
                              
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 3️⃣: 명세 생성 (sdd_generate_specification.py)           │
│                                                                   │
│  1. 문서 내용 분석                                              │
│  2. 요구사항 자동 분류                                          │
│     - FUNCTIONAL (기능)                                         │
│     - SECURITY (보안)                                           │
│     - INTEGRATION (연계)                                        │
│     - PERFORMANCE (성능)                                        │
│     - DATA (데이터)                                             │
│     - OPERATIONAL (운영)                                        │
│                                                                   │
│  3. 명세서 생성 (SPEC-*.md)                                     │
│  4. 요구사항 메타데이터 저장 (specification.json)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        docs/00. confluence/
        ├── specification.json
        └── SPEC-ERP-001.md
                              
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 4️⃣: 계획 생성 (sdd_generate_planning.py)                │
│                                                                   │
│  1. 요구사항별 태스크 생성 (5개 서브태스크)                     │
│     - DESIGN (설계)                                             │
│     - DEVELOPMENT (개발)                                        │
│     - TESTING (테스트)                                          │
│     - QA (품질 보증)                                            │
│     - DOCUMENTATION (문서)                                      │
│                                                                   │
│  2. 일정 계산 (6시간/일 생산성)                                 │
│     예: 13일 × 6시간/일 = 78시간                               │
│                                                                   │
│  3. 주간 분해 (Weekly Breakdown)                                │
│  4. 계획 메타데이터 저장 (planning.json)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        docs/00. confluence/
        └── planning.json
        
        예시 출력:
        ├─ Week 1: Design + Development 시작
        ├─ Week 2: Development 완료 + Testing 시작
        └─ Week 3: Testing 완료 + QA + Documentation
```

---

## 구성 요소별 책임

### Phase 1: sdd_collect_with_confluence.py

```python
main()
├── JIRA Board API 조회
│   └── MZ2026 프로젝트, 내부검토 상태 이슈 조회
├── 각 이슈 처리
│   ├── REQID 추출 (sdd_extract_reqid.py 호출)
│   ├── JIRA 첨부파일 다운로드
│   ├── Confluence 페이지 URL 추출
│   └── Confluence 페이지 다운로드
├── 폴더 구조 생성
│   └── {이슈키}/{REQID}/
└── source-metadata.json 생성
```

### Phase 2: sdd_normalize_documents_v2.py

```python
main()
├── source-metadata.json 로드
├── 각 마크다운 파일 분석
│   ├── convert_html_to_markdown()
│   │   ├── BeautifulSoup 파싱
│   │   └── html2text 변환
│   ├── extract_html_structure()
│   │   ├── 제목 추출
│   │   ├── 표 개수 계산
│   │   └── 리스트/이미지 감지
│   ├── extract_metadata_fields()
│   │   └── 정규식으로 필드 추출
│   └── analyze_document()
│       └── 종합 분석
├── 품질 점수 계산 (calculate_quality_score_v2)
├── Markdown 파일 업데이트
└── normalized-metadata.json v2.0 생성
```

### Phase 3: sdd_generate_specification.py

```python
main()
├── normalized-metadata.json 로드
├── 각 문서별 명세 생성
│   ├── 요구사항 추출
│   ├── 자동 분류 (classify_requirement)
│   └── 명세 테이블 생성
├── SPEC-*.md 파일 생성
└── specification.json 저장
```

### Phase 4: sdd_generate_planning.py

```python
main()
├── specification.json 로드
├── 각 명세별 계획 생성
│   ├── 요구사항별 태스크 5개 생성
│   ├── 예상 시간 계산
│   └── 주간 분해
└── planning.json 저장
```

---

## 메타데이터 변환 과정

```
Phase 1 입력: JIRA Board API
              ↓
        source-metadata.json
        {
          "sourceDocuments": [
            {
              "type": "jira_attachment|confluence_page",
              "issue": "MZ2026-1",
              "reqid": "ERP-001"
            }
          ]
        }
              ↓
Phase 2 입력: 마크다운 파일 + HTML 파싱
              ↓
        normalized-metadata.json
        {
          "documents": [
            {
              "title": "ERP-001 요구사항정의서",
              "quality_score": 88.0,
              "structure": { ... },
              "metadata": { ... }
            }
          ]
        }
              ↓
Phase 3 입력: 정규화 메타데이터
              ↓
        specification.json
        {
          "specifications": [
            {
              "specId": "SPEC-ERP-001",
              "requirements": [
                { "id": "REQ-001", "category": "FUNCTIONAL" }
              ]
            }
          ]
        }
              ↓
Phase 4 입력: 명세 메타데이터
              ↓
        planning.json
        {
          "projectTimeline": {
            "totalDays": 13,
            "tasks": [
              { "taskId": "DESIGN-ERP-001", ... }
            ]
          }
        }
```

---

## REQID 추출 전략

```
입력: JIRA 이슈 (MZ2026-1)

Level 1: JIRA 커스텀 필드 (customfield_10431)
         ↓
         찾음? → "ERP-001" 반환
         ↓ 찾지 못함
         
Level 2: 이슈 제목에서 정규식 추출
         "MZ2026-1 ERP-001 화면정의서" 
         ↓ 정규식: ERP-\d{3} 또는 REQ-\d+
         ↓
         찾음? → "ERP-001" 반환
         ↓ 찾지 못함
         
Level 3: Confluence 페이지 메타데이터
         HTML 내 "산출물ID: ERP-001" 검색
         ↓
         찾음? → "ERP-001" 반환
         ↓ 찾지 못함
         
Level 4: 자동 생성 (fallback)
         "REQ-" + 이슈번호
         → "REQ-1" 생성 (MZ2026-1의 경우)
```

---

## 폴더 구조 진화

### Phase 1 이전 (구 구조)
```
docs/00. confluence/
└── MZ2026-1/page_661520434/
    └── ERP-001 요구사항정의서.md
```
문제: page_ID 기반 → 의미 불명확

### Phase 1 이후 (현재 구조)
```
docs/00. confluence/
└── MZ2026-1/ERP-001/
    ├── ERP-001 요구사항정의서.md
    └── EPR-001 화면정의서.docx
```
개선: REQID 기반 → 의미 명확, 추적 용이

---

## API 엔드포인트

### JIRA API

| 엔드포인트 | 목적 | 버전 |
|-----------|------|------|
| `agile/1.0/board/{board_id}/issue` | 이슈 목록 조회 | Agile 1.0 |
| `rest/api/2/attachment/{id}` | 첨부파일 다운로드 | REST v2 |

### Confluence API

| 엔드포인트 | 목적 | 버전 |
|-----------|------|------|
| `/wiki/rest/api/content/{page_id}?expand=body.view` | 페이지 본문 조회 | Cloud |

### 인증

```
Authorization: Bearer {JIRA_TOKEN}

예시:
Authorization: Bearer ATATT3xFfGF0KmZp0WmP5iRFdFPXoQj4UGHz4m...
```

---

## 성능 최적화

### 병렬 처리 기회

```
Phase 1: 
├─ 이슈 조회 (직렬)
└─ 각 이슈 처리 (병렬 가능)
   ├─ JIRA 첨부파일 다운로드
   └─ Confluence 페이지 다운로드

Phase 2:
├─ 마크다운 파일 분석 (병렬 가능)
└─ 품질 점수 계산 (병렬 가능)

Phase 3:
└─ 명세 생성 (병렬 가능)

Phase 4:
└─ 계획 생성 (병렬 가능)
```

### 캐싱 전략

```
source-metadata.json:
├─ JIRA 보드 조회 결과 캐싱 (1시간)
└─ Confluence 페이지 내용 캐싱 (1시간)

normalized-metadata.json:
└─ 품질 점수 캐싱 (24시간)
```

---

## 에러 처리

### Phase 1

```
┌─ JIRA API 401: 토큰 만료/무효
├─ JIRA API 404: 보드 또는 이슈 없음
├─ Confluence API 404: 페이지 없음
└─ 파일 다운로드 실패: 네트워크 오류
    → 재시도 (3회)
    → 이슈 스킵, 로그 기록
    → 통계에 오류 개수 누적
```

### Phase 2

```
┌─ BeautifulSoup 파싱 오류
├─ 메타데이터 추출 실패 (선택사항)
└─ 파일 인코딩 오류
    → 로그 기록
    → 기본값으로 계속 진행
```

### Phase 3, 4

```
└─ 메타데이터 파일 누락
    → 이전 단계 재실행 필요
    → 사용자에게 안내
```

---

## 확장 포인트

### 다중 프로젝트 지원

```python
# Phase 1 수정
for project_key in ["MZ2026", "GOVPJT", "EGOV"]:
    collect_documents(project_key)
    normalize_documents(project_key)
    generate_specification(project_key)
    generate_planning(project_key)
```

### 커스텀 분류 규칙

```python
# Phase 3 확장
CUSTOM_CATEGORIES = {
    "FUNCTIONAL": [...],
    "SECURITY": [...],
    "CUSTOM_DOMAIN": ["프로젝트 맞춤형"],
}

def classify_requirement(text):
    for category, keywords in CUSTOM_CATEGORIES.items():
        if any(kw in text for kw in keywords):
            return category
```

### Claude API 연동

```python
# Phase 3, 4 고도화
from anthropic import Anthropic

client = Anthropic()

# 요구사항 자동 분류 (의미론적)
def smart_classify(text):
    response = client.messages.create(
        model="claude-opus-4",
        messages=[
            {"role": "user", "content": f"분류: {text}"}
        ]
    )
    return response.content[0].text
```

---

**최종 업데이트**: 2026-06-12  
**아키텍처 버전**: 2.0
