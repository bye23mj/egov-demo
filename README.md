# egov-demo

> **전자정부표준프레임워크 + Claude Code + Codex CLI + Gemini CLI**
>
> 멀티에이전트 협업을 통한 전자정부 기반 애플리케이션 자동화 개발 프로젝트

---

## 개요

egov-demo는 다음 세 가지 프로젝트를 통합한 포괄적 개발 자동화 프레임워크입니다:

1. **claude-code-orchestrator** — 멀티에이전트 오케스트레이션 (Claude Code + Codex + Gemini)
2. **claude-ai-spring-boot** — Spring Boot 전문화된 에이전트 및 스킬 라이브러리
3. **egov-template-portal** — 전자정부표준프레임워크 Java/Spring/MyBatis/JSP 개발 패턴

---

## 특징

### 1. Karpathy 4원칙 + eGov 개발 표준

```text
✅ 코딩하기 전에 먼저 생각하기   — 가정을 명시적으로 드러냄
✅ 단순함을 먼저 선택하기        — 필요해질 때까지 복잡도 추가 금지
✅ 외과수술처럼 변경하기         — 필요한 범위만 정확히 수정
✅ 목표 중심으로 실행하기        — 성공 기준을 먼저 정의하고 검증
```

### 2. 멀티에이전트 협업

```
사용자 요청
    ↓
Claude Code (오케스트레이션)
    ├→ Gemini CLI (요구사항 상세화)
    ├→ Codex CLI (설계 검토 & 코드 구현)
    └→ 품질 검증 & 완료 승인
```

### 3. Oracle 11g 전용

- **ROWNUM 기반 페이징** (3중 SELECT 구조)
- **Sequence 자동증가** (AUTO_INCREMENT 금지)
- **MyBatis Mapper XML** 동적 SQL
- **전자정부 네이밍** (EgovXxxController, XxxServiceImpl, XxxDAO)

### 4. TDD 기반 개발

- JUnit 5 + Spring Test
- AAA 패턴 (Arrange-Act-Assert)
- 85%+ 테스트 커버리지 목표
- `mvn -q test` 통과 필수

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| **Framework** | 전자정부표준프레임워크 5.0 |
| **Language** | Java 17 |
| **Web** | Spring MVC 5+ |
| **ORM** | MyBatis 3.5+ |
| **Template** | JSP + JSTL |
| **Database** | Oracle 11g |
| **Build** | Maven 3.8+ |
| **Test** | JUnit 5 + Spring Test |
| **Logging** | SLF4J + Log4j2 |
| **Packaging** | WAR (Tomcat 9) |

---

## 빠른 시작

### 1. 프로젝트 클론 및 구조 확인

```bash
cd /Users/ai/vscode/egov-demo

# 디렉토리 구조 확인
tree -L 2 -a
```

### 2. Maven 빌드 확인

```bash
# 컴파일 확인 (가장 빠름)
mvn -q -DskipTests compile

# 테스트 실행 (Oracle 11g 필요)
mvn -q test

# WAR 패키지 생성
mvn -q -DskipTests package
```

### 3. Oracle 11g Docker 실행 (선택)

```bash
docker run -d \
  --name oracle-xe \
  -p 1521:1521 \
  wnameless/oracle-xe-11g-r2

# 상태 확인
docker ps | grep oracle
```

### 4. 첫 번째 기능 개발

```bash
# Claude Code를 통해 요청
/startproject 사용자 샘플 조회 기능
```

---

## 프로젝트 구조

```
egov-demo/
├── CLAUDE.md                      # Claude Code 지침 (필독)
├── AGENTS.md                      # Codex 작업 표준
├── GEMINI.md                      # Gemini 역할 정의
├── README.md                      # 이 파일
├── pom.xml                        # Maven 설정
│
├── .claude/                       # Claude Code 설정
│   ├── agents/                    # 서브에이전트 (general-purpose, spring-boot-engineer 등)
│   ├── hooks/                     # 자동화 훅 (agent-router, check-codex, lint-on-save 등)
│   ├── rules/                     # 개발 규칙
│   │   ├── coding-principles.md   # Karpathy 4원칙 + eGov
│   │   ├── dev-environment.md     # Maven + Oracle 개발환경
│   │   ├── testing.md             # JUnit 테스트 표준
│   │   ├── security.md            # SQL Injection, XSS, 인증
│   │   ├── language.md            # 영어 코드 + 한국어 응답
│   │   └── config-protection.md   # 설정 파일 보호 (최우선)
│   ├── skills/                    # 재사용 스킬
│   │   ├── egov-crud/             # CRUD 자동 생성
│   │   ├── mybatis-patterns/      # MyBatis 패턴 참조
│   │   ├── oracle-sql/            # Oracle SQL 표준
│   │   ├── egov-test/             # 테스트 작성 헬퍼
│   │   ├── startproject/          # 멀티에이전트 기능 킥오프
│   │   ├── plan/                  # 구현 계획 수립
│   │   ├── tdd/                   # TDD 사이클
│   │   ├── checkpointing/         # 세션 저장
│   │   └── design-tracker/        # 설계 결정 기록
│   ├── docs/                      # 설계 및 조사 결과
│   │   ├── DESIGN.md              # 설계 결정 기록
│   │   └── research/              # Gemini 조사 결과
│   └── settings.json              # Claude Code 환경 설정
│
├── .codex/                        # Codex CLI 설정
│   ├── AGENTS.md                  # Codex 역할 정의 (AGENTS.md와 동기)
│   └── config.toml                # Codex 모델·정책
│
├── .gemini/                       # Gemini CLI 설정
│   ├── GEMINI.md                  # Gemini 역할 정의 (GEMINI.md와 동기)
│   └── settings.json              # Gemini 모델 설정
│
├── src/main/
│   ├── java/egovframework/example/
│   │   ├── <domain>/
│   │   │   ├── service/           # Service 인터페이스 + VO
│   │   │   ├── serviceImpl/        # ServiceImpl
│   │   │   └── web/               # Controller
│   │   └── common/                # 공통 클래스
│   │
│   ├── resources/egovframework/
│   │   ├── spring/                # Spring 설정 (context-*.xml)
│   │   ├── sqlmap/example/        # MyBatis Mapper XML
│   │   └── egovProps/             # 환경 설정 (globals.properties)
│   │
│   └── webapp/WEB-INF/
│       ├── jsp/egov/              # JSP 뷰 (Egov prefix)
│       └── web.xml
│
├── src/test/
│   └── java/egovframework/        # JUnit 테스트
│
└── work/                          # 개발 노트 (자유 기록)
    ├── REVIEW.md                  # 코드 리뷰 체크리스트
    └── ...
```

---

## 개발 워크플로우

### Phase 1: 요구사항 분석 (Gemini)

```bash
# Claude Code에서 요청
/startproject 샘플 목록 조회 기능

# Gemini가 수행:
# 1. 기능 요구사항 분석 (REQ-001, REQ-002, ...)
# 2. 수용조건 작성 (Given-When-Then)
# 3. 계층별 영향도 분석
# 4. Oracle 11g 고려사항 정리
# 5. 미확정 질문 도출

# 산출물: .claude/docs/research/샘플-requirements.md
```

### Phase 2: 계획 수립 (Claude Code)

```bash
# Claude가 수행:
# 1. 요구사항 검토 및 승인
# 2. 영향 범위 분석
# 3. 작업계획 수립 (파일·단계·검증 방법)
```

### Phase 3: 설계 검토 (Codex)

```bash
# Codex가 수행:
# 1. 계획 리뷰
# 2. 아키텍처 검토
# 3. 리스크 분석
# 4. 개선안 제시
```

### Phase 4: 구현 (Codex)

```bash
# Codex가 수행:
# 1. Controller · Service · DAO · Mapper XML 구현
# 2. JSP 뷰 작성
# 3. JUnit 테스트 작성 (정상·예외 케이스)
# 4. Maven 빌드 및 테스트 검증

# 완료 조건:
mvn -q -DskipTests compile   → PASS
mvn -q test                   → PASS (실패 0건)
mvn -q -DskipTests package    → PASS
```

### Phase 5: 코드 리뷰 & 완료 (Claude Code)

```bash
# Claude가 수행:
# 1. 코드 리뷰 (Karpathy 4원칙 + eGov 표준)
# 2. 통합 테스트 검증
# 3. 완료 승인
# 4. CHANGELOG 업데이트
```

---

## 참조 문서

| 문서 | 내용 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | Claude Code 지침 및 멀티에이전트 워크플로우 |
| [AGENTS.md](AGENTS.md) | Codex 작업 표준 및 구현 가이드 |
| [GEMINI.md](GEMINI.md) | Gemini 역할 및 요구사항 분석 형식 |
| [.claude/rules/coding-principles.md](.claude/rules/coding-principles.md) | Karpathy 4원칙 + eGov 코딩 원칙 |
| [.claude/rules/dev-environment.md](.claude/rules/dev-environment.md) | Maven + Oracle 개발환경 |
| [.claude/rules/testing.md](.claude/rules/testing.md) | JUnit + Spring Test 표준 |
| [.claude/rules/security.md](.claude/rules/security.md) | SQL Injection, XSS, 인증 보안 |

---

## 완료 기준

모든 기능 개발 후 반드시:

```bash
# 1. 컴파일 확인
mvn -q -DskipTests compile
# → 컴파일 에러 없음

# 2. 전체 테스트 통과
mvn -q test
# → BUILD SUCCESS, 테스트 실패 0건

# 3. 패키지 빌드
mvn -q -DskipTests package
# → target/egov-demo-1.0.0.war 생성됨

# 4. Oracle 상태 확인
docker ps | grep oracle
nc -zv localhost 1521
# → Oracle 11g 컨테이너 실행 중
```

---

## 문제 해결

### Maven 캐시 문제

```bash
rm -rf .m2/repository/{egovframework,org}
mvn -q clean && mvn -q -DskipTests compile
```

### Oracle 연결 실패

```bash
# Oracle 컨테이너 확인
docker ps | grep oracle

# 포트 연결 확인
nc -zv localhost 1521

# 접속 정보 확인
cat src/main/resources/egovframework/egovProps/globals.properties
```

### 테스트 실패

```bash
# 단일 테스트 상세 로그
mvn test -Dtest=SampleDAOTest -X

# Oracle 상태 재확인
docker restart oracle-xe
sleep 10
mvn -q test
```

---

## 라이센스

Apache License 2.0

---

## 기여 가이드

이 프로젝트는 Claude Code, Codex CLI, Gemini CLI의 협업으로 개발됩니다.

기능 추가 시:
1. [CLAUDE.md](CLAUDE.md)의 워크플로우를 따릅니다.
2. [AGENTS.md](AGENTS.md)의 구현 표준을 준수합니다.
3. [.claude/rules/](./claude/rules/) 가이드라인을 검토합니다.

---

## 연락처

질문 및 피드백: [GitHub Issues](https://github.com/yourusername/egov-demo/issues)

