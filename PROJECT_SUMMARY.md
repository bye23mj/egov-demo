# egov-demo 프로젝트 생성 완료 ✅

> **전자정부표준프레임워크 + Claude Code + Codex + Gemini 통합 프로젝트**

---

## 📋 생성된 파일 구조

```
egov-demo/
├── 📄 CLAUDE.md                              # Claude Code 지침 (필독)
├── 📄 AGENTS.md                              # Codex 작업 표준
├── 📄 GEMINI.md                              # Gemini 역할 정의
├── 📄 README.md                              # 프로젝트 개요
│
├── 📁 .claude/
│   ├── 📄 settings.json                      # Claude Code 환경 설정
│   └── 📁 rules/
│       ├── 📄 coding-principles.md           # Karpathy 4원칙 + eGov (필독)
│       ├── 📄 dev-environment.md             # Maven + Oracle 개발환경
│       ├── 📄 testing.md                     # JUnit 테스트 표준
│       ├── 📄 security.md                    # 보안 체크리스트
│       ├── 📄 language.md                    # 언어 프로토콜
│       └── 📄 config-protection.md           # 설정 파일 보호 (최우선)
│
├── 📁 .codex/                                # Codex 설정 (향후 추가)
└── 📁 .gemini/                               # Gemini 설정 (향후 추가)
```

---

## 🎯 핵심 가이드라인

### 1️⃣ Karpathy 4원칙 (필수)

```
✅ 코딩하기 전에 먼저 생각하기   — 가정을 명시적으로 드러냄
✅ 단순함을 먼저 선택하기        — 필요해질 때까지 복잡도 추가 금지
✅ 외과수술처럼 변경하기         — 필요한 범위만 정확히 수정
✅ 목표 중심으로 실행하기        — 성공 기준을 먼저 정의하고 검증
```

**위치**: `.claude/rules/coding-principles.md`

### 2️⃣ 멀티에이전트 워크플로우

```
사용자 요청
    ↓
Claude Code (오케스트레이션)
    ├→ Gemini CLI (요구사항 분석)
    │   - REQ-NNN 형식 기능 요구사항
    │   - Given-When-Then 수용조건
    │   - 계층별 영향도 분석
    │   - Oracle 11g 고려사항
    │
    ├→ Claude Code (계획 수립)
    │   - 요구사항 승인
    │   - 영향 범위 분석
    │   - 작업계획 작성
    │
    ├→ Codex CLI (설계 검토)
    │   - 아키텍처 검토
    │   - 리스크 분석
    │
    ├→ Codex CLI (코드 구현)
    │   - Controller·Service·DAO 구현
    │   - Mapper XML·JSP 작성
    │   - JUnit 테스트 작성
    │   - Maven 테스트 통과
    │
    └→ Claude Code (코드 리뷰 & 완료)
        - Karpathy 4원칙 검증
        - 통합 테스트 확인
        - 완료 승인
```

**위치**: [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md), [GEMINI.md](GEMINI.md)

### 3️⃣ 개발 환경 (Maven + Oracle 11g)

```bash
# 필수 명령어
mvn -q -DskipTests compile  # 컴파일 확인
mvn -q test                  # 테스트 실행
mvn -q -DskipTests package   # WAR 빌드

# 완료 조건 (세 가지 모두 통과)
✅ compile → PASS
✅ test → PASS (실패 0건)
✅ package → PASS
```

**위치**: `.claude/rules/dev-environment.md`

### 4️⃣ 테스트 표준 (JUnit 5 + Spring Test)

```java
// AAA 패턴 (필수)
@Test
void selectList_검색어없으면_전체목록을_반환한다() throws Exception {
    // Arrange: 테스트 데이터 준비
    SampleVO searchVO = new SampleVO();
    
    // Act: 실제 동작
    List<SampleVO> result = sampleService.selectList(searchVO);
    
    // Assert: 결과 검증
    assertNotNull(result);
}
```

**위치**: `.claude/rules/testing.md`

### 5️⃣ 보안 체크리스트

- ✅ SQL Injection: `#{}` 파라미터 바인딩
- ✅ XSS: JSP 출력값 `<c:out>` 이스케이프
- ✅ 인증: `EgovUserDetailsHelper.getAuthenticatedUser()` 확인
- ✅ 비밀정보: 환경변수로 관리

**위치**: `.claude/rules/security.md`

### 6️⃣ 언어 프로토콜

- **코드**: 영문 (변수명, 메서드명, 주석)
- **SQL**: 대문자 키워드 + Oracle 표준
- **사용자 응답**: 한국어
- **커밋 메시지**: 한국어 또는 영문

**위치**: `.claude/rules/language.md`

---

## 📚 첫 사용 가이드

### Step 1: 프로젝트 구조 이해하기

```bash
cd /Users/ai/vscode/egov-demo

# README 읽기
cat README.md

# CLAUDE.md 읽기 (멀티에이전트 워크플로우)
cat CLAUDE.md

# 개발 규칙 읽기
cat .claude/rules/coding-principles.md
```

### Step 2: 첫 번째 기능 개발 시작

Claude Code에서 다음 커맨드 실행:

```bash
# 멀티에이전트 기능 개발 킥오프
/startproject 샘플 목록 조회 기능

# 또는 수동으로 시작
/plan 샘플 목록 조회 기능
```

### Step 3: 구현 완료 확인

```bash
# Maven 빌드 확인
mvn -q -DskipTests compile

# 테스트 실행 (Oracle 필요)
mvn -q test

# WAR 패키지 생성
mvn -q -DskipTests package
```

---

## 🔐 설정 파일 보호 (최우선)

```
절대 삭제 금지:
❌ .claude/ 전체 디렉토리
❌ .codex/ 전체 디렉토리
❌ .gemini/ 전체 디렉토리
❌ CLAUDE.md, AGENTS.md, GEMINI.md

내용 수정은 가능:
✅ .claude/rules/* 수정
✅ .claude/settings.json 수정
✅ 새 파일 추가
```

**근거**: `.claude/rules/config-protection.md`

---

## 📖 참조 문서

| 문서 | 용도 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | Claude Code 지침 + 멀티에이전트 워크플로우 |
| [AGENTS.md](AGENTS.md) | Codex 구현 표준 |
| [GEMINI.md](GEMINI.md) | Gemini 요구사항 분석 형식 |
| [README.md](README.md) | 프로젝트 개요 |
| `.claude/rules/coding-principles.md` | **Karpathy 4원칙 + eGov** (필독) |
| `.claude/rules/dev-environment.md` | Maven + Oracle 11g |
| `.claude/rules/testing.md` | JUnit 5 테스트 표준 |
| `.claude/rules/security.md` | 보안 체크리스트 |
| `.claude/rules/language.md` | 언어 프로토콜 |
| `.claude/rules/config-protection.md` | 설정 파일 보호 |

---

## 🚀 다음 단계

1. **프로젝트 설정 완료**
   - ✅ CLAUDE.md, AGENTS.md, GEMINI.md 작성 완료
   - ✅ .claude/rules/ 가이드라인 6개 작성 완료
   - ✅ Git 초기화 및 첫 커밋 완료

2. **개발 준비 (수동)**
   - [ ] pom.xml 작성 (eGov 의존성)
   - [ ] src/main/resources/egovframework/egovProps/globals.properties 작성
   - [ ] src/main/webapp/WEB-INF/web.xml 설정
   - [ ] Oracle 11g 테이블 생성 (DDL)

3. **첫 번째 기능 개발**
   - [ ] /startproject로 멀티에이전트 워크플로우 실행
   - [ ] Gemini로 요구사항 상세화
   - [ ] Codex로 CRUD 기능 구현
   - [ ] mvn test 통과 확인

---

## ✅ 생성 완료 체크리스트

- [x] egov-demo 디렉토리 생성
- [x] CLAUDE.md 작성 (Claude Code 지침)
- [x] AGENTS.md 작성 (Codex 작업 표준)
- [x] GEMINI.md 작성 (Gemini 역할 정의)
- [x] README.md 작성 (프로젝트 개요)
- [x] .claude/rules/ 6개 파일 작성:
  - [x] coding-principles.md (Karpathy 4원칙)
  - [x] dev-environment.md (Maven + Oracle)
  - [x] testing.md (JUnit 표준)
  - [x] security.md (보안 체크리스트)
  - [x] language.md (언어 프로토콜)
  - [x] config-protection.md (설정 보호)
- [x] .claude/settings.json 작성
- [x] Git 초기화 및 초기 커밋

---

**프로젝트 생성 완료**: 2026-06-06

다음 세 프로젝트를 통합한 포괄적 개발 자동화 프레임워크가 준비되었습니다:

1. **claude-code-orchestrator** (멀티에이전트 오케스트레이션)
2. **claude-ai-spring-boot** (Spring Boot 전문화)
3. **egov-template-portal** (전자정부 개발 패턴)

이제 Claude Code를 통해 전자정부 기반 애플리케이션을 자동화하여 개발할 수 있습니다! 🚀
