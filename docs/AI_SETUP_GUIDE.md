# AI 에이전트 설정 가이드

> egov-demo 프로젝트의 Claude Code, Gemini, Codex 다중 에이전트 설정

---

## 📋 목차

1. [다중 에이전트 개요](#다중-에이전트-개요)
2. [Claude Code 설정](#claude-code-설정)
3. [Gemini 설정](#gemini-설정)
4. [Codex 설정](#codex-설정)
5. [워크플로우](#워크플로우)
6. [설정 검증](#설정-검증)

---

## 다중 에이전트 개요

### 역할 분담

```
┌──────────────────────────────────────────────────┐
│            사용자 요청 (Claude Code)             │
│  • 오케스트레이션                                │
│  • 계획 수립                                    │
│  • 코드 리뷰                                    │
└──────────────────────────────────────────────────┘
                      ↓
        ┌─────────────────────────────┐
        │   병렬 처리 (분석 & 구현)    │
        ├─────────────────────────────┤
        │ Gemini      │ Codex         │
        │ (분석)      │ (구현)        │
        ├─────────────┼───────────────┤
        │ • 요구사항  │ • Controller  │
        │ • 설계      │ • Service     │
        │ • 리서치    │ • DAO         │
        │ • 영향도    │ • Mapper XML  │
        │ • Oracle    │ • JSP         │
        └─────────────────────────────┘
                      ↓
        ┌──────────────────────────────┐
        │  Claude Code (최종 검증)     │
        │  • 통합 테스트              │
        │  • 완료 승인                │
        └──────────────────────────────┘
```

### 각 에이전트의 특성

| 에이전트 | 모델 | 기능 | 강점 |
|---------|------|------|------|
| **Claude Code** | claude-sonnet-4-6 | 오케스트레이션 | 사용자 대화, 계획, 조율 |
| **Gemini** | gemini-2.0-flash | 요구사항 분석 | 빠른 리서치, API 조사 |
| **Codex** | gpt-5.5 | 코드 구현 | 깊은 추론, 고품질 코드 |

---

## Claude Code 설정

### 설정 위치

```
.claude/settings.json
```

### 설정 내용

```json
{
  "model": "claude-sonnet-4-6",
  "enabledPlugins": {
    "code-review@claude-plugins-official": true,
    "github@claude-plugins-official": true,
    "slack@claude-plugins-official": true,
    "understand-anything@understand-anything": true
  }
}
```

### 주요 역할

```
✅ 수행:
   • 사용자 요청 수신 및 분석
   • 프로젝트 전체 계획 수립
   • Gemini/Codex에 작업 위임
   • 최종 코드 리뷰 및 검증
   • Git 커밋 수행
   • Slack 알림 발송

❌ 금지:
   • (없음 - 모든 작업 가능)
```

### 실행 명령어

```bash
claude-code /path/to/egov-demo

# 또는 VS Code 클릭
```

---

## Gemini 설정

### 설정 위치

```
.gemini/settings.json
```

### 설정 내용

```json
{
  "model": "gemini-2.0-flash",
  "max_tokens": 4096,
  "temperature": 0.7,
  "context": {
    "size": "large",
    "mode": "research"
  },
  "project": {
    "type": "egov-framework",
    "language": "Korean",
    "framework": "Spring MVC + MyBatis",
    "database": "Oracle 11g"
  },
  "capabilities": {
    "requirement_analysis": true,
    "api_research": true,
    "oracle_sql_analysis": true,
    "business_flow_design": true,
    "acceptance_criteria": true
  },
  "restrictions": {
    "no_code_generation": true,
    "no_git_operations": true,
    "no_test_execution": true
  }
}
```

### 주요 역할

```
✅ 수행:
   • 원 요구사항 상세화
   • 기능 분해 및 설계
   • 화면/Controller/Service/DAO 영향도 분석
   • Oracle 11g 제약 사항 검토
   • API/라이브러리 리서치
   • Given-When-Then 수용조건 작성
   • 미확정 질문 도출

❌ 금지:
   • Java 코드 작성
   • SQL 구현
   • Git 커밋
   • 테스트 실행
   • 아키텍처 변경 제안
```

### 실행 명령어

```bash
# Gemini CLI 설치
pip install gemini-cli

# 프로젝트 분석
gemini -p "
전자정부표준프레임워크 포털 템플릿 프로젝트에서
다음 기능의 요구사항을 상세화해 주세요.

기능: {기능 요청}

다음 형식으로 작성:
1. 기능 요구사항 (REQ-NNN 형식)
2. 수용조건 (Given-When-Then)
3. 화면 · Controller · Service · DAO · DB 영향도
4. Oracle 11g 고려사항
5. 미확정 질문
" --include-directories . 2>/dev/null
```

### 산출물 저장

```
.claude/docs/research/{기능명}-requirements.md
```

### 예시: 샘플 목록 조회 요구사항

```markdown
## 요구사항 분석: 샘플 목록 조회

### 기능 요구사항

**REQ-001: 샘플 목록 조회**
- 사용자가 샘플 목록을 페이징으로 조회한다
- 검색어로 샘플명을 필터링할 수 있다
- 정렬: 등록일(최신순)
- 권한: 로그인 필수

**REQ-002: 검색 필터**
- 샘플명 검색 (부분 일치)
- 등록자별 필터링 (선택)

### 수용조건

**AC-001: 검색어 없을 때 전체 목록**
- Given: 검색 조건 미입력
- When: 목록 조회 버튼 클릭
- Then: 등록일 최신순 전체 목록을 페이징(10건/페이지)으로 표시

**AC-002: 검색어로 필터링**
- Given: 검색어 "테스트"
- When: 검색 버튼 클릭
- Then: 샘플명에 "테스트"를 포함하는 데이터만 표시

### 영향도 분석

| 계층 | 파일 | 작업 |
|------|------|------|
| View | EgovSampleList.jsp | 검색폼, 목록테이블, 페이징 추가 |
| Controller | EgovSampleController | selectList 메서드 추가 |
| Service | EgovSampleService + Impl | selectList 로직 구현 |
| DAO | SampleDAO | selectList, selectCount 메서드 추가 |
| SQL | SampleMapper.xml | ROWNUM 페이징 쿼리 작성 |
| VO | SampleDefaultVO | searchKeyword, pageIndex, pageSize 필드 |
| DB | Oracle 11g | SAMPLE_TBL 테이블 확인 |

### Oracle 11g 고려사항

```sql
-- ROWNUM 페이징 (3중 SELECT 필수)
SELECT * FROM (
    SELECT ROWNUM RN, A.* FROM (
        SELECT SAMPLE_ID, SAMPLE_NM, REG_USR_ID, FRST_REGIST_PNTTM
        FROM SAMPLE_TBL
        WHERE 1=1
        AND SAMPLE_NM LIKE '%' || :searchKeyword || '%'
        ORDER BY FRST_REGIST_PNTTM DESC
    ) A WHERE ROWNUM <= :lastIndex
) WHERE RN > :firstIndex

-- 금지:
-- OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY (Oracle 12c+)
-- LIMIT 10 OFFSET 10 (MySQL/PostgreSQL)
```

### 미확정 질문

- Q1: 페이지 크기는 10건으로 고정할까, 사용자 선택 가능할까?
- Q2: 검색 대상은 샘플명만? 설명도 포함?
- Q3: 권한별 필터링이 필요할까?
```

---

## Codex 설정

### 설정 위치

```
.codex/config.toml
```

### 설정 내용

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"

[project]
type = "egov-framework"
language = "Java"
javaVersion = "17"
framework = "Spring 5.x"
orm = "MyBatis"
database = "Oracle 11g"

[conventions]
packagePrefix = "egovframework.example"
controllerSuffix = "Controller"
serviceSuffix = "Service"
serviceSuffixImpl = "ServiceImpl"
daoSuffix = "DAO"

[standards]
enforceLayerSeparation = true
requireTests = true
testCoverage = 85
forbiddenSyntax = ["OFFSET", "LIMIT", "AUTO_INCREMENT"]

[security]
requireParamBinding = true
forbidStringConcatenationInSQL = true
```

### 주요 역할

```
✅ 수행:
   • Java/Spring 코드 구현
   • MyBatis Mapper XML 작성
   • JSP 뷰 개발
   • 단위 테스트 작성
   • SQL 성능 최적화
   • 보안 검토 (SQL Injection, XSS 방지)
   • 코드 리뷰 및 리팩토링

❌ 금지:
   • 요구사항 분석 (Gemini 담당)
   • 최종 승인 결정 (Claude Code 담당)
   • Git 커밋 (Claude Code 담당)
   • 아키텍처 설계 (CLAUDE.md 규칙 위반)
```

### 실행 명령어

```bash
# Codex CLI 설치
pip install codex-cli

# 코드 구현 요청
codex "
전자정부표준프레임워크에서 샘플 목록 조회 기능을 구현해 주세요.

요구사항:
- 페이징: ROWNUM 기반 3중 SELECT
- 검색: 샘플명 부분 일치
- 정렬: 등록일 최신순

다음을 구현:
1. EgovSampleController.selectList()
2. EgovSampleService.selectList()
3. EgovSampleServiceImpl.selectList()
4. SampleDAO.selectList()
5. SampleMapper.xml 쿼리
6. EgovSampleList.jsp
7. JUnit 테스트
"
```

### 구현 산출물

```
src/main/java/egovframework/example/sample/
├── web/EgovSampleController.java
├── service/EgovSampleService.java
├── service/impl/EgovSampleServiceImpl.java
├── SampleDAO.java
└── SampleVO.java

src/main/resources/egovframework/sqlmap/example/sample/
└── SampleMapper.xml

src/main/webapp/WEB-INF/jsp/egov/sample/
└── EgovSampleList.jsp

src/test/java/egovframework/example/sample/
├── web/EgovSampleControllerTest.java
├── service/EgovSampleServiceTest.java
└── service/impl/SampleDAOTest.java
```

---

## 워크플로우

### Phase 1: 요구사항 상세화 (Gemini)

```
1. Claude Code가 사용자 요청 수신
2. Claude Code가 Gemini에 위임
   ↓
3. Gemini가 요구사항 분석:
   - REQ-NNN 형식 기능 분해
   - Given-When-Then 수용조건
   - 화면/Controller/Service/DAO/DB 영향도
   - Oracle 11g 고려사항
   ↓
4. Gemini가 .claude/docs/research/{기능명}-requirements.md 작성
   ↓
5. Claude Code가 Gemini 결과 검증:
   - 요구사항 형식 확인
   - 수용조건 완성도 확인
   - Oracle 11g 제약 반영 확인
```

### Phase 2: 코드 구현 (Codex)

```
1. Claude Code가 Codex에 위임 (Gemini 결과 참고)
   ↓
2. Codex가 다음을 구현:
   - Controller 메서드
   - Service 인터페이스 & 구현
   - DAO 클래스
   - Mapper XML (Oracle SQL)
   - JSP 뷰
   - JUnit 테스트
   ↓
3. Codex가 다음을 확인:
   - 계층 분리 (Controller → Service → DAO)
   - SQL 파라미터 바인딩
   - 테스트 커버리지 85% 이상
   ↓
4. 구현 산출물 생성
```

### Phase 3: 최종 검증 (Claude Code)

```
1. Claude Code가 Codex 구현 검토
   ↓
2. Maven 컴파일 확인:
   $ mvn -q -DskipTests compile → PASS
   ↓
3. 테스트 실행:
   $ mvn -q test → 0 failures, 0 errors
   ↓
4. 패키지 빌드:
   $ mvn -q -DskipTests package → *.war 생성
   ↓
5. Git 커밋 및 Slack 알림
   ↓
6. 완료 승인
```

---

## 설정 검증

### Step 1: 설정 파일 확인

```bash
# Gemini 설정
cat .gemini/settings.json | jq '.model, .capabilities'

# Codex 설정
cat .codex/config.toml | grep model, language
```

### Step 2: 각 에이전트 연결 테스트

```bash
# Claude Code (이미 실행 중)
# VS Code 또는 claude-code 명령어

# Gemini 설치 & 테스트
pip install gemini-cli
gemini --version

# Codex 설치 & 테스트
pip install codex-cli
codex --version
```

### Step 3: 간단한 작업으로 테스트

```bash
# 1. Claude Code에서 사용자 요청
"샘플 목록 조회 기능을 구현해 주세요"

# 2. Claude Code가 Gemini 호출
gemini -p "샘플 목록 조회 요구사항 분석..." \
  --include-directories . > .claude/docs/research/sample-requirements.md

# 3. Claude Code가 Codex 호출
codex "Gemini 결과를 바탕으로 구현..." \
  --project-root . \
  --include-tests

# 4. Claude Code가 최종 검증
mvn -q -DskipTests compile
mvn -q test
git add .
git commit -m "..."
```

---

## 주의사항

### ⚠️ Gemini 사용 시

- **코드 작성 금지**: 분석/리서치만 수행
- **요구사항 우선**: 요구사항 없이 구현 금지
- **Given-When-Then**: 모든 수용조건을 명시

### ⚠️ Codex 사용 시

- **계층 분리**: Controller → Service → DAO 순서만
- **SQL 파라미터**: `#{}` 바인딩 필수, `${}` 금지
- **테스트 필수**: 단위 테스트 + 통합 테스트
- **Oracle 호환**: ROWNUM, Sequence, NVL 사용

### ⚠️ Claude Code 최종 검증 시

```bash
# 필수 체크
mvn -q -DskipTests compile  # 컴파일 성공
mvn -q test                  # 테스트 통과
mvn -q -DskipTests package   # 패키지 생성
```

---

## 트러블슈팅

### Gemini 연결 오류

```bash
# 인증 확인
gemini login

# 모델 확인
gemini --model gemini-2.0-flash --test

# 설정 재로드
rm ~/.gemini/cache
```

### Codex 연결 오류

```bash
# OpenAI API 키 확인
export OPENAI_API_KEY="sk-..."

# 모델 확인
codex --model gpt-5.5 --test

# 설정 검증
codex --config-validate
```

### 다중 에이전트 충돌

```
❌ 발생 상황: 
   Gemini가 코드 작성, Codex가 요구사항 분석

✅ 해결책:
   - 각 에이전트의 역할 재확인
   - 제약 사항(restrictions) 검토
   - Claude Code가 명확한 지시 제공
```

---

## 참고 자료

| 문서 | 내용 |
|------|------|
| [CLAUDE.md](../CLAUDE.md) | Claude Code 최상위 지침 |
| [GEMINI.md](../GEMINI.md) | Gemini 역할 및 출력 형식 |
| [AGENTS.md](../AGENTS.md) | Codex 역할 정의 |
| [coding-principles.md](./.claude/rules/coding-principles.md) | 코딩 원칙 (Karpathy) |

---

**최종 업데이트**: 2026-06-12  
**설정 버전**: 1.0
