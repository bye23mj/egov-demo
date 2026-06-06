# CLAUDE.md — egov-demo

> **전자정부표준프레임워크 + 멀티에이전트 자동화 프레임워크**
>
> Claude Code가 Codex CLI(심층 추론)와 Gemini CLI(대규모 리서치)를 오케스트레이션하여
> 전자정부 기반 Java/Spring/MyBatis/JSP 프로젝트 개발을 자동화한다.

---

## 에이전트 역할 분담

| 에이전트 | 강점 | 사용 목적 |
|---------|------|---------|
| **Claude Code** | 오케스트레이션, 사용자 대화 | 요구사항 승인, 계획 수립, 품질 게이트 |
| **Codex CLI** | 깊은 추론, 설계 판단, 코드 구현 | Controller·Service·DAO·Mapper·JSP 구현 |
| **Gemini CLI** | 1M 토큰, 웹 검색, 멀티모달 | 요구사항 상세화, 대규모 분석, 문서 조사 |

**IMPORTANT**: 출력이 큰 작업(코드 리뷰, 요구사항 분석, 설계 검토)은 반드시 서브에이전트를 경유한다.

---

## 4원칙 (Karpathy Guidelines)

### 1. 코딩하기 전에 먼저 생각하기
- 가정을 조용히 하지 않는다. 불명확하면 멈추고 질문한다.
- 여러 해석 가능성이 있으면 모두 나열하고 사용자에게 확인한다.
- 구현 전에 영향 범위(Controller/Service/DAO/JSP/SQL)를 먼저 분석한다.

### 2. 단순함을 먼저 선택하기
- 요청한 것만 구현한다. 추측으로 기능 추가 금지.
- 미사용 VO 필드, 불필요한 공통 클래스 자의적 생성 금지.
- 200줄 코드가 50줄로 가능하면 다시 작성한다.

### 3. 외과수술처럼 변경하기
- 기존 코드 수정 시 인접 주석·포맷 임의 개선 금지.
- 작동 중인 코드 리팩토링 금지 (버그 수정 범위 준수).
- 관련 없는 데드코드 발견 시 삭제 금지 → 사용자에게 보고.

### 4. 목표 중심으로 실행하기
- "구현해줘" → "테스트 작성 → 통과하도록 구현 → 회귀 없음 검증"으로 변환.
- 성공 기준을 먼저 정의하고 검증 가능한 단계로 나눈다.
- 각 단계 완료 후 `mvn -q -DskipTests compile` 통과를 확인한다.

---

## 전자정부프레임워크 개발 워크플로우

```
/startproject <기능명>
```

1. **Gemini** → 요구사항 상세화 (REQ-NNN, Given-When-Then, 영향도)
2. **Claude** → 요구사항 승인, 영향 범위 분석, 작업계획 수립
3. **Codex** → 설계 리뷰 및 리스크 검토
4. **Claude** → 실행 가능한 태스크 리스트 생성
5. **Codex** → Controller · Service · DAO · Mapper XML · JSP 구현
6. **Claude** → 코드 리뷰, 완료 승인 (`mvn -q test` 통과 확인)

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| **Framework** | 전자정부표준프레임워크 5.0 (eGovFramework) |
| **Language** | Java 17 |
| **Web** | Spring MVC + JSP + JSTL |
| **ORM** | MyBatis (iBatis 계열) |
| **DB** | Oracle 11g (단일 DBMS, 변경 불가) |
| **Build** | Maven |
| **Test** | JUnit 5 + Spring Test |
| **Logging** | SLF4J + Log4j2 |
| **Packaging** | WAR (Tomcat 9 배포) |

---

## 빠른 명령어

```bash
# 빌드 확인
mvn -q -DskipTests compile

# 전체 테스트
mvn -q test

# WAR 패키지
mvn -q -DskipTests package

# Oracle DB 상태 확인
docker ps | grep oracle
nc -zv localhost 1521
```

---

## 컨텍스트 관리 (CRITICAL)

Claude Code 실질 컨텍스트: **70~100k 토큰**  
**출력이 큰 작업은 반드시 서브에이전트 경유:**

| 출력 크기 | 방식 |
|--------|------|
| 1~2문장 | 직접 호출 |
| 10줄 이상 분석 | **서브에이전트 경유** |
| Codex 설계 검토 | **서브에이전트 경유** |
| Gemini 요구사항 분석 | **서브에이전트 경유** |

---

## 계층 구조

```
Controller (app/api 진입점)
  └── Service / ServiceImpl (업무 로직)
        └── DAO (MyBatis Mapper 호출)
              └── Mapper XML (Oracle 11g SQL)
```

**계층 간 직접 접근 금지**: Controller → DAO 직접 호출 불가

---

## 구현 완료 기준

세 가지 모두 통과해야 완료:

```bash
mvn -q -DskipTests compile   # PASS
mvn -q test                   # PASS (실패 0건)
mvn -q -DskipTests package    # PASS
```

---

## 스킬 목록

| 스킬 | 용도 |
|------|------|
| `/startproject` | 멀티에이전트 기능 개발 킥오프 |
| `/plan` | 구현 계획 수립 (파일·단계·검증 방법) |
| `/tdd` | Red→Green→Refactor TDD 사이클 |
| `/egov-crud` | CRUD 전 계층 자동 생성 |
| `/mybatis-patterns` | MyBatis + Oracle 패턴 참조 |
| `/oracle-sql` | Oracle 11g SQL 표준 참조 |
| `/egov-test` | Controller·Service·DAO 테스트 작성 |
| `/checkpointing` | 세션 컨텍스트 보존 |
| `/design-tracker` | 설계 결정 자동 기록 |

---

## 언어 프로토콜

- **코드·로그**: 영어 (변수명, 메서드명, 주석)
- **사용자 응답**: 한국어
- **SQL 키워드**: 대문자 (Oracle 표준)
- **eGov 네이밍**: `EgovXxxController`, `XxxServiceImpl`, `XxxDAO`, `XxxVO`

---

## 참조 문서

| 파일 | 내용 |
|------|------|
| `.claude/rules/coding-principles.md` | 코딩 원칙 (Karpathy + eGov) |
| `.claude/rules/dev-environment.md` | Maven + Oracle 개발환경 |
| `.claude/rules/testing.md` | JUnit + Oracle 테스트 규칙 |
| `.claude/rules/security.md` | SQL Injection, XSS, 인증 |
| `.claude/rules/codex-delegation.md` | Codex 위임 기준 |
| `.claude/rules/gemini-delegation.md` | Gemini 위임 기준 |
| `.claude/rules/config-protection.md` | 설정 파일 보호 (최우선) |
| `AGENTS.md` | Codex 작업 표준 (필독) |
| `GEMINI.md` | Gemini 역할·출력 형식 (필독) |
| `.claude/docs/DESIGN.md` | 설계 결정 기록 |
