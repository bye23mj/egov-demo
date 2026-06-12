# SDD 파이프라인 빠른 시작 가이드

> 5분 안에 JIRA → 요구사항 명세 → 계획서 생성하기

---

## 📦 설치 및 설정

### 1단계: 필수 라이브러리 설치

```bash
pip install beautifulsoup4 html2text requests
```

### 2단계: 환경 변수 설정

```bash
export JIRA_EMAIL="bye23mj@nsonesoft.com"
export JIRA_TOKEN="ATATT3xFfGF0KmZp0WmP5iRFdFPXoQj4UGHz4m3wF5OAGy67bmWrkfYSRUtCTTPzQwPDVARUm20PMN4k6aKjBUXC_Tks7NdbiN1rjAFp4BJ3KIsOgf4KqLOzmAbCLl3PIHm8o4dJTqzs9EsVERGizts4GFDf_kpNbj5pSnnnOAtQeWj8Fhi14Hs=5E98863D"
export JIRA_BOARD_ID="427"
```

**JIRA 토큰 발급:**
1. https://id.atlassian.com 에서 로그인
2. 프로필 → API 토큰 → 토큰 생성
3. 생성된 토큰을 환경변수에 설정

---

## 🚀 전체 파이프라인 한 번에 실행

```bash
#!/bin/bash

# 디렉토리 이동
cd /Users/ai/vscode/egov-demo

# Phase 1: 문서 수집
echo "📥 Phase 1: 문서 수집 중..."
python3 scripts/sdd_collect_with_confluence.py

# Phase 2: 문서 정규화 + 품질 개선
echo "📄 Phase 2: 문서 정규화 중..."
python3 scripts/sdd_normalize_documents_v2.py

# Phase 3: 명세 생성
echo "📋 Phase 3: 명세 생성 중..."
python3 scripts/sdd_generate_specification.py

# Phase 4: 계획 생성
echo "📅 Phase 4: 계획 생성 중..."
python3 scripts/sdd_generate_planning.py

# Git 커밋
echo "✅ SDD 파이프라인 완료!"
git add docs/
git commit -m "feat: SDD 파이프라인 자동 실행"
git log --oneline -4
```

**실행 시간**: 약 30초 (네트워크 상태에 따라 변동)

---

## 단계별 실행 (필요시)

### Phase 1️⃣: 문서 수집 (Collection)

```bash
python3 scripts/sdd_collect_with_confluence.py
```

**확인 사항**:
```bash
ls -la docs/00. confluence/
cat docs/00. confluence/source-metadata.json | jq '.summary'
```

**출력 예**:
```json
{
  "totalIssues": 2,
  "jiraAttachments": 1,
  "confluencePages": 1,
  "totalDocuments": 2
}
```

---

### Phase 2️⃣: 문서 정규화 (Normalization)

```bash
python3 scripts/sdd_normalize_documents_v2.py
```

**확인 사항**:
```bash
cat docs/00. confluence/normalized-metadata.json | jq '.statistics'
```

**출력 예**:
```json
{
  "total_documents": 1,
  "average_quality_score": 88.0
}
```

**품질 점수 확인**:
- 88.0 이상: ✅ 우수
- 70.0~87.9: 👍 양호
- 60.0~69.9: 👌 보통
- 60.0 미만: ⚠️ 개선필요

---

### Phase 3️⃣: 명세 생성 (Specification)

```bash
python3 scripts/sdd_generate_specification.py
```

**생성 파일**:
```bash
ls docs/00. confluence/SPEC-*.md
```

**명세서 내용 확인**:
```bash
cat docs/00. confluence/SPEC-ERP-001.md | head -50
```

---

### Phase 4️⃣: 계획 생성 (Planning)

```bash
python3 scripts/sdd_generate_planning.py
```

**계획 요약 확인**:
```bash
cat docs/00. confluence/planning.json | jq '.projectTimeline'
```

**출력 예**:
```json
{
  "startDate": "2026-06-16",
  "estimatedEndDate": "2026-07-03",
  "totalDays": 13,
  "totalHours": 78
}
```

---

## 📊 결과 확인

### 생성된 파일 목록

```bash
tree docs/00. confluence/ -L 2
```

**디렉토리 구조**:
```
docs/00. confluence/
├── source-metadata.json          # Phase 1 메타데이터
├── normalized-metadata.json      # Phase 2 정규화 결과
├── specification.json            # Phase 3 명세
├── planning.json                 # Phase 4 계획
├── SPEC-ERP-001.md              # 명세서 문서
└── MZ2026-1/
    └── ERP-001/
        ├── ERP-001 요구사항정의서.md
        └── EPR-001 화면정의서.docx
```

### 주요 메트릭 확인

```bash
# 1. 수집 현황
jq '.summary' docs/00. confluence/source-metadata.json

# 2. 품질 점수
jq '.documents[].quality_score' docs/00. confluence/normalized-metadata.json

# 3. 요구사항 분류
jq '.specifications[].requirements[].category' docs/00. confluence/specification.json | sort | uniq -c

# 4. 일정 계획
jq '.weeklyBreakdown | length' docs/00. confluence/planning.json
```

---

## 🔧 문제 해결

### JIRA API 401 오류

**에러**:
```
401 Unauthorized: Invalid credentials
```

**해결**:
```bash
# 1. 토큰 확인
echo $JIRA_TOKEN

# 2. 토큰 유효성 테스트
curl -H "Authorization: Bearer $JIRA_TOKEN" \
  https://nsonesoft.atlassian.net/rest/api/2/myself

# 3. 새 토큰 발급 (위 설정 참고)
```

### BeautifulSoup4 설치 오류

**에러**:
```
ImportError: No module named 'bs4'
```

**해결**:
```bash
pip install --upgrade beautifulsoup4
python3 -c "import bs4; print(bs4.__version__)"
```

### 파일 인코딩 오류

**에러**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**해결**:
```bash
# 파일 인코딩 확인
file -I docs/00. confluence/MZ2026-1/ERP-001/*.md

# 변환 (필요시)
iconv -f EUC-KR -t UTF-8 input.txt > output.txt
```

### 파일을 찾을 수 없음

**에러**:
```
FileNotFoundError: source-metadata.json not found
```

**해결**:
```bash
# Phase 1 재실행
python3 scripts/sdd_collect_with_confluence.py

# 파일 확인
ls -la docs/00. confluence/
```

---

## 🎯 일반적인 작업 흐름

### 새로운 JIRA 프로젝트 추가

```bash
# Step 1: 환경 변수 수정
export JIRA_BOARD_ID="새로운보드ID"  # Confluence 보드 설정에서 확인

# Step 2: 파이프라인 실행
python3 scripts/sdd_collect_with_confluence.py
python3 scripts/sdd_normalize_documents_v2.py
...

# Step 3: 결과 확인
ls docs/00. confluence/
```

### 기존 문서 품질 개선

```bash
# Phase 2만 재실행 (다른 단계 스킵)
python3 scripts/sdd_normalize_documents_v2.py

# 품질 점수 확인
jq '.statistics.average_quality_score' docs/00. confluence/normalized-metadata.json
```

### 명세와 계획만 재생성

```bash
# Phase 3, 4 재실행 (수집/정규화는 스킵)
python3 scripts/sdd_generate_specification.py
python3 scripts/sdd_generate_planning.py

# 결과 확인
wc -l docs/00. confluence/SPEC-*.md
cat docs/00. confluence/planning.json | jq '.projectTimeline'
```

---

## 📈 성능 튜닝

### 대량 문서 처리

```python
# sdd_normalize_documents_v2.py 수정: 병렬 처리 추가

from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(analyze_document, file_path)
        for file_path in document_files
    ]
    analyses = [f.result() for f in futures]
```

### API 요청 최적화

```python
# 요청 재시도 + 캐싱
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

---

## 📚 추가 리소스

| 문서 | 설명 |
|------|------|
| [SDD_WORKFLOW.md](./SDD_WORKFLOW.md) | 전체 워크플로우 상세 가이드 |
| [SDD_ARCHITECTURE.md](./SDD_ARCHITECTURE.md) | 아키텍처 및 데이터 흐름도 |
| [../scripts/sdd_*.py](../scripts/) | 각 Phase 스크립트 소스 |

---

## 🤝 기여 및 개선

### 새로운 기능 제안

```
1. Issue 생성: GitHub Issues
2. Discussion: Discussions 탭
3. Pull Request: 변경사항 제출
```

### 버그 리포트

```bash
# 스크린샷 + 로그 첨부
# 재현 단계 명확히 기록
# 환경 정보 포함 (Python 버전, OS 등)
```

---

## 📞 지원

### 자주 묻는 질문

**Q: REQID가 자동으로 생성되지 않습니다.**
A: Phase 1 로그에서 `reqid_source` 확인. JIRA 필드 → 제목 → Confluence → 자동생성 순으로 시도.

**Q: 품질 점수가 낮습니다.**
A: `missing_elements`에서 누락 요소 확인. Confluence HTML을 더 잘 포맷하면 개선.

**Q: 여러 프로젝트를 동시에 처리할 수 있나요?**
A: 현재는 MZ2026 단일 프로젝트. JIRA_BOARD_ID 변경으로 다른 프로젝트 처리 가능.

---

## 📝 로그 분석

### 로그 파일 위치

```bash
# Phase별 로그 (표준 출력)
python3 scripts/sdd_*.py 2>&1 | tee logs/phase-X.log

# 메타데이터 로그 (JSON)
cat docs/00. confluence/source-metadata.json | jq '.sourceDocuments[]'
```

### 디버그 모드

```python
# 스크립트 시작 부분에 추가
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

---

**최종 업데이트**: 2026-06-12  
**가이드 버전**: 1.0  
**실행 환경**: Python 3.10+, Linux/macOS
