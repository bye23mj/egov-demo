🚀 SDD 자동화 워크플로우 - 실제 사용 예시

---
Step 0: 사전 준비

cd /Users/ai/vscode/egov-demo/scripts

# 1. 의존성 설치
pip install -r requirements.txt

# 2. Confluence API 토큰 설정
python confluence-sync.py config --set-token "ATATT3x..."

# 3. JIRA API 토큰 설정
python confluence-sync.py jira config --set-token "jira_api_token..."

# 4. 설정 확인
python confluence-sync.py jira status

예상 출력:
🔌 JIRA 연결 테스트 중...
✓ JIRA 연결 성공
  Project Key: GOVPJT
  URL: https://nsonesoft.atlassian.net

---
Step 1: JIRA 문서 수집

# 내부검토 상태의 요구사항 문서들 수집
python confluence-sync.py sdd collect \
  --status "내부검토" \
  --document-types "요구사항정의서,유스케이스정의서,컴포넌트정의서" \
  --project-key "GOVPJT" \
  --workspace "/tmp/sdd-workspaces"

예상 출력:
📁 SDD 문서 수집 시작
   Run ID: RUN-20260611-K7F
   Workspace: /tmp/sdd-workspaces/RUN-20260611-K7F
   Status: 내부검토
   Document Types: 요구사항정의서, 유스케이스정의서, 컴포넌트정의서

⬇  JIRA에서 문서 수집 중...
   ✓ GOVPJT-101: 사용자 관리 시스템 (2개 첨부파일)
   ✓ GOVPJT-102: 문서 조회 기능 (1개 첨부파일)
   ✓ GOVPJT-103: 권한 관리 (3개 첨부파일)

💾 메타데이터 저장 중...

✅ 문서 수집 완료
──────────────────────────────────
  Run ID: RUN-20260611-K7F
  수집된 문서: 6개
    - JIRA에서: 6개
    - Confluence에서: 0개
  Workspace: /tmp/sdd-workspaces/RUN-20260611-K7F
  메타데이터: .../source-metadata.json
──────────────────────────────────

생성된 구조:
/tmp/sdd-workspaces/RUN-20260611-K7F/
├── input/
│   ├── GOVPJT-101/
│   │   ├── 요구사항정의서_v0.3.docx
│   │   └── 테스트케이스_v0.1.xlsx
│   ├── GOVPJT-102/
│   │   └── 유스케이스정의서_v0.2.docx
│   └── GOVPJT-103/
│       ├── 컴포넌트정의서_v0.4.pptx
│       ├── ERD_v1.0.pdf
│       └── 화면정의_v0.5.hwpx
│
└── source-metadata.json

---
Step 2: 문서 정규화

# DOCX/XLSX/PPTX/HWPX → Markdown 자동 변환
python confluence-sync.py sdd normalize \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-K7F"

예상 출력:
🔄 문서 정규화 시작
   Run ID: RUN-20260611-K7F
   입력: /tmp/sdd-workspaces/RUN-20260611-K7F/input
   출력: /tmp/sdd-workspaces/RUN-20260611-K7F/normalized

⚙️  정규화 중...
   ✓ 요구사항정의서_v0.3.docx → Markdown
   ✓ 테스트케이스_v0.1.xlsx → Markdown Table
   ✓ 유스케이스정의서_v0.2.docx → Markdown
   ✓ 컴포넌트정의서_v0.4.pptx → Markdown (슬라이드별)
   ✓ ERD_v1.0.pdf → Markdown (텍스트 추출)
   ✓ 화면정의_v0.5.hwpx → Markdown (부분)

✅ 문서 정규화 완료
──────────────────────────────────
  총 파일: 6개
  성공: 6개
  실패: 0개
  미지원: 0개
  스킵: 0개
  출력 디렉터리: .../normalized
──────────────────────────────────

생성된 구조:
normalized/
├── GOVPJT-101/
│   ├── 요구사항정의서_v0.3.md
│   └── 테스트케이스_v0.1.md
├── GOVPJT-102/
│   └── 유스케이스정의서_v0.2.md
└── GOVPJT-103/
    ├── 컴포넌트정의서_v0.4.md
    ├── ERD_v1.0.md
    └── 화면정의_v0.5.md

---
Step 3: Speckit Specify 실행

# 요구사항 체계화 (requirements.md, spec.md, edge_cases.md 생성)
python confluence-sync.py sdd specify \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-K7F"

예상 출력:
📋 Speckit Specify 실행
   Run ID: RUN-20260611-K7F
   Workspace: /tmp/sdd-workspaces/RUN-20260611-K7F

🔧 Workspace 초기화 중...
✓ Workspace 초기화 완료

📋 /speckit.specify 실행 중...
   Claude API 호출 중... ⏳

   ✓ 입력 파일 분석 완료: 6개
   ✓ 요구사항 추출 완료: 34건
   ✓ 유스케이스 매핑 완료: 12건
   ✓ 테스트케이스 연결 완료: 29건

✅ Specify 실행 완료
──────────────────────────────────
  생성된 파일: 3개
    - requirements.md (요구사항 정의)
    - spec.md (상세 명세)
    - edge_cases.md (모호한 항목 12건)
──────────────────────────────────

생성된 requirements.md:
# 요구사항정의서

## 기능 요구사항

### REQ-FN-001: 사용자 목록 조회
- 사용자 목록을 페이징으로 조회한다
- 사용자명 검색 지원
- 테스트케이스: TC-001, TC-002

### REQ-FN-002: 사용자 상세 조회
- 특정 사용자의 상세 정보를 조회한다
- 테스트케이스: TC-003

### REQ-FN-003: 사용자 등록
- 신규 사용자를 등록한다
- 필수 필드: 사용자명, 이메일, 부서
- 테스트케이스: TC-004, TC-005

## 비기능 요구사항

### REQ-NF-001: 성능
- 사용자 목록 조회는 2초 이내로 완료되어야 함
- 동시 접속자 100명 이상 지원

### REQ-NF-002: 보안
- 암호는 BCrypt로 암호화 저장
- HTTPS 필수

생성된 spec.md:
# 명세서

## 시스템 아키텍처

UserController
  ↓
EgovUserService
  ↓
UserDAO
  ↓
UserMapper.xml
  ↓
USER_TBL (Oracle)

## 컴포넌트별 설계

### UserController
- GET /users - 사용자 목록 조회
- GET /users/{userId} - 사용자 상세
- POST /users - 사용자 등록
- PUT /users/{userId} - 사용자 수정
- DELETE /users/{userId} - 사용자 삭제

### UserService
- selectList(UserSearchVO) → List<UserVO>
- selectDetail(String userId) → UserVO
- insertUser(UserVO) → void
- updateUser(UserVO) → void
- deleteUser(String userId) → void

### UserDAO
- 모든 서비스 메서드에 대응하는 SQL 매퍼 호출

### Database Schema
```sql
CREATE TABLE USER_TBL (
  USER_ID VARCHAR2(50) PRIMARY KEY,
  USER_NAME VARCHAR2(100) NOT NULL,
  EMAIL VARCHAR2(100),
  DEPT_ID VARCHAR2(50),
  REG_USR_ID VARCHAR2(50),
  FRST_REGIST_PNTTM DATE
);

CREATE SEQUENCE SEQ_USER_ID;

**생성된 edge_cases.md:**
```markdown
# 모호한 항목 및 확인 질문

## 질문 1: 중복 사용자 처리
관련 요구사항: REQ-FN-003 (사용자 등록)
- 동일 사용자명으로 중복 등록할 수 있는가?
- 선택지:
  1. 차단 (중복 검사 후 오류 반환)
  2. 경고 후 허용 (확인 알림 표시)
  3. 자동 수정 (예: user → user_001)
- Claude 제안: 차단 정책 권장

## 질문 2: 비밀번호 초기값
관련 요구사항: REQ-FN-003
- 신규 사용자 등록 시 임시 비밀번호 제공 방식?
- 선택지:
  1. 사용자가 직접 입력
  2. 시스템 자동 생성 (이메일 발송)
  3. 관리자가 입력
- Claude 제안: 시스템 자동 생성 + 이메일 발송

## 질문 3: 페이징 크기
관련 요구사항: REQ-FN-001
- 기본 페이지 크기는 10개? 20개? 50개?
- 최대 페이지 크기 제한이 있는가?
- Claude 제안: 기본 10개, 최대 100개 제한
```

---
Step 4: Speckit Plan 실행

# 설계 계획 수립 (plan.md, component_spec.md, data_model.md, TDD.md 생성)
python confluence-sync.py sdd plan \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-K7F"

예상 출력:
📐 Speckit Plan 실행
   Run ID: RUN-20260611-K7F

📐 /speckit.plan 실행 중...
   Claude API 호출 중... ⏳

✅ Plan 실행 완료
──────────────────────────────────
  생성된 파일: 4개
    - plan.md (구현 계획)
    - component_spec.md (컴포넌트 설계)
    - data_model.md (데이터 모델)
    - TDD.md (테스트 전략)
──────────────────────────────────

생성된 plan.md:
# 구현 계획

## Phase 1: 기초 (1주)

### Task 1-1: VO/DTO 정의
- UserVO, UserSearchVO, UserDefaultVO 작성
- ComDefaultVO 상속 (페이징)
- 소요: 1일

### Task 1-2: Service 인터페이스
- EgovUserService 인터페이스 정의
- 메서드 시그니처 확정
- 소요: 0.5일

### Task 1-3: SQL Mapper 작성
- UserMapper.xml (Oracle ROWNUM 페이징)
- CRUD 쿼리 작성
- 소요: 2일

## Phase 2: 테스트 (3일)

### Task 2-1: JUnit 테스트
- UserControllerTest
- EgovUserServiceTest
- UserDAOTest
- 커버리지: 85% 이상
- 소요: 2일

### Task 2-2: 통합 테스트
- Spring Test + MockMvc
- 엔드투엔드 테스트
- 소요: 1일

## Phase 3: 마무리 (2일)

### Task 3-1: 성능 최적화
- 인덱스 추가 (USER_ID, EMAIL)
- 쿼리 성능 검증
- 소요: 1일

### Task 3-2: 코드 리뷰 & 배포
- 코드 리뷰 (Karpathy 4원칙)
- 문서 작성
- WAR 패키지 생성
- 소요: 1일

## 일정

Week 1: Phase 1 (5일) + Phase 2 시작 (1일)
Week 2: Phase 2 (2일) + Phase 3 (2일)
예상: 2주 완료


---
Step 5: Speckit Tasks 실행

# 작업 분해 (tasks.md 생성 및 Jira Task 변환 준비)
python confluence-sync.py sdd tasks \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-K7F"

예상 출력:
✅ Speckit Tasks 실행
   Run ID: RUN-20260611-K7F

✅ /speckit.tasks 실행 중...
   Claude API 호출 중... ⏳

✅ Tasks 실행 완료
──────────────────────────────────
  생성된 파일: 1개
    - tasks.md (작업 분해)
      - Story 3개
      - Sub-task 28개
──────────────────────────────────

생성된 tasks.md:
# 작업 분해

## Story 1: 사용자 목록 조회

### Sub-tasks

- [ ] T001 UserVO, UserSearchVO, UserDefaultVO 작성
  - 관련 요구사항: REQ-FN-001
  - 예상 소요: 2시간

- [ ] T002 UserController 테스트 작성
  - GET /users 엔드포인트 테스트
  - 페이징 테스트 (1~5페이지)
  - 예상 소요: 4시간

- [ ] T003 EgovUserService 테스트 작성
  - selectList() 메서드 테스트
  - 검색 조건별 테스트
  - 예상 소요: 3시간

- [ ] T004 UserDAO 테스트 작성
  - Oracle ROWNUM 페이징 검증
  - 실DB 연결 테스트
  - 예상 소요: 3시간

- [ ] T005 UserMapper.xml SQL 작성
  - selectList 쿼리 (ROWNUM 3중 SELECT)
  - 검색 조건 동적 추가
  - 예상 소요: 3시간

- [ ] T006 EgovUserServiceImpl 구현
  - selectList() 메서드 구현
  - 예외 처리 추가
  - 예상 소요: 2시간

- [ ] T007 UserController 구현
  - GET /users 엔드포인트
  - 파라미터 바인딩
  - 예상 소요: 2시간

- [ ] T008 EgovSampleList.jsp 작성
  - 사용자 목록 테이블
  - 페이징 네비게이션
  - 검색 폼
  - 예상 소요: 4시간

- [ ] T009 통합 테스트
  - Spring Test 통합 테스트
  - 예상 소요: 2시간

## Story 2: 사용자 상세 조회
...

## Story 3: 사용자 등록
...

---
Step 6: 최종 구조 확인

# 생성된 모든 파일 확인
ls -R /tmp/sdd-workspaces/RUN-20260611-K7F/

# 생성된 산출물 목록
echo "=== 최종 생성 파일 ==="
ls -lh /tmp/sdd-workspaces/RUN-20260611-K7F/specs/

# 실행 로그 확인
cat /tmp/sdd-workspaces/RUN-20260611-K7F/speckit-execution.json | python -m json.tool

예상 출력:
RUN-20260611-K7F/
├── input/
│   ├── GOVPJT-101/
│   ├── GOVPJT-102/
│   └── GOVPJT-103/
│
├── normalized/
│   ├── GOVPJT-101/
│   ├── GOVPJT-102/
│   └── GOVPJT-103/
│
├── specs/                          ⭐ 최종 산출물
│   ├── requirements.md (12 KB)
│   ├── spec.md (15 KB)
│   ├── edge_cases.md (8 KB)
│   ├── plan.md (10 KB)
│   ├── component_spec.md (9 KB)
│   ├── data_model.md (7 KB)
│   ├── TDD.md (11 KB)
│   └── tasks.md (14 KB)
│
├── .specify/
│   └── config.json
│
├── speckit-execution.json          ⭐ 실행 로그
│   [
│     {"step": "initialize", "status": "success", ...},
│     {"step": "specify", "status": "success", ...},
│     {"step": "plan", "status": "success", ...},
│     {"step": "tasks", "status": "success", ...}
│   ]
│
└── source-metadata.json

---
Step 7: 다음 단계 (선택사항)

Confluence에 산출물 등록

# Phase 4 (향후): 생성된 산출물을 Confluence에 동기화
python confluence-sync.py sdd publish \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-K7F" \
  --target "confluence" \
  --space-key "TNYUU"

JIRA에 Task 생성

# Phase 4 (향후): tasks.md 기반 Jira Task 자동 생성
python confluence-sync.py sdd publish \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-K7F" \
  --target "jira" \
  --parent-issue "GOVPJT-101"

Slack 팀 알림

# Phase 4 (향후): 완료 알림
python confluence-sync.py sdd notify \
  --run-id "/tmp/sdd-workspaces/RUN-20260611-K7F" \
  --channel "development"
