# .md 문서 구조 및 프로젝트 워크플로우 적용 시점 분석

> 프로젝트: egov-demo  
> 분석일: 2026-06-07  
> 총 .md 파일: 25개

---

## 1. 문서 분류 체계

```
egov-demo/
│
├── 📘 에이전트 행동 정의 (상시 로드)
│   ├── CLAUDE.md
│   ├── AGENTS.md
│   ├── GEMINI.md
│   └── .claude/rules/*.md  (6개)
│
├── 📗 프로젝트 기준 문서 (착수 단계)
│   ├── README.md
│   └── PROJECT_SUMMARY.md
│
├── 📙 요구사항 · 설계 문서 (분석/설계 단계)
│   ├── docs/PRD/*.md  (4개)
│   └── docs/02. interview/COMPONENT_SPEC.md
│
├── 📕 산출물 (개발 단계 전반)
│   ├── docs/01. requirements/REQUIREMENTS.md
│   └── docs/00. confluence/*.md  (4개, 동기화본)
│
└── 📓 내부 관리 문서 (AI 운영)
    ├── .claude/docs/*.md  (2개)
    └── work/*.md  (현재 문서 포함)
```

---

## 2. 문서별 구조 및 워크플로우 적용 시점

### 2-1. 에이전트 행동 정의 문서 (상시 적용)

> **적용 시점**: 세션 시작 시 자동 로드 → 모든 작업에 상시 적용

| 파일 | 역할 | 주요 내용 |
|---|---|---|
| `CLAUDE.md` | Claude 전체 오케스트레이션 규칙 | 멀티에이전트 협업 구조, 컨텍스트 관리 원칙, Gemini/Codex 위임 기준 |
| `AGENTS.md` | Codex CLI 작업 표준 | Codex 역할(Java 구현 담당), 금지사항, 코딩 표준 참조 |
| `GEMINI.md` | Gemini CLI 역할 정의 | 요구사항 분석 담당, REQ-NNN 출력 형식, Given-When-Then 표준 |

**적용 흐름**:
```
세션 시작
  └── Claude가 CLAUDE.md 로드 → 에이전트 역할 파악
        ├── 설계 판단 필요 → AGENTS.md 참조 → Codex 위임
        └── 요구사항 분석 필요 → GEMINI.md 참조 → Gemini 위임
```

---

### 2-2. 운영 규칙 문서 (`.claude/rules/`) — 상시 적용

> **적용 시점**: 각 작업 유형 진입 시 해당 규칙 자동 참조

| 파일 | 적용 시점 | 주요 제약 |
|---|---|---|
| `language.md` | 모든 응답 생성 시 | 응답 한국어, 코드·로그 영어 |
| `config-protection.md` | 파일 수정·삭제 시 | `.claude/`, `.codex/`, `.gemini/` 삭제 절대 금지 |
| `coding-principles.md` | 코드 작성·리뷰 시 | 계층 분리, 외과적 변경, eGov 네이밍 규칙 |
| `dev-environment.md` | 빌드·실행 시 | Maven 명령어, Oracle 11g 전용, Docker 확인 |
| `security.md` | Mapper XML·JSP 작성 시 | SQL Injection(`#{}`), XSS(`<c:out>`), 인증 확인 |
| `testing.md` | 테스트 코드 작성 시 | JUnit 5, AAA 패턴, 실DB(Oracle 11g) 테스트 |

**우선순위 구조**:
```
config-protection.md  ← 최우선 (다른 모든 규칙보다 우선)
  ↓
language.md           ← 항상 적용
  ↓
coding-principles.md  ← 코드 작성 시 적용
  ↓
security.md           ← 보안 민감 코드 작성 시 적용
  ↓
testing.md            ← 테스트 코드 작성 시 적용
  ↓
dev-environment.md    ← 빌드/배포 시 적용
```

---

### 2-3. 프로젝트 기준 문서 — 착수 단계

> **적용 시점**: 프로젝트 최초 착수, 신규 팀원 온보딩, 프로젝트 맥락 파악 시

| 파일 | 용도 |
|---|---|
| `README.md` | 프로젝트 전체 개요, 기술스택, 빠른 시작 가이드 |
| `PROJECT_SUMMARY.md` | 프로젝트 생성 완료 보고서, 구조 요약, 다음 단계 |

**적용 흐름**:
```
[착수] 프로젝트 시작
  └── README.md 참조 → 기술스택·실행방법 파악
        └── PROJECT_SUMMARY.md 참조 → 완료 항목·다음 단계 확인
```

---

### 2-4. 요구사항 · 설계 문서 (`docs/PRD/`, `docs/02. interview/`) — 분석/설계 단계

> **적용 시점**: 신규 기능 개발 착수 전, Gemini 리서치 위임 시, 설계 검토 시

#### PRD 문서

| 파일 | 적용 단계 | 역할 |
|---|---|---|
| `egov_standard_project_deliverables_flow.md` | 착수 ~ 검수 전반 | 정부기관 표준 산출물 흐름 기준서. 어떤 단계에서 어떤 산출물을 만들어야 하는지 정의 |
| `jira_confluence_slack_prerequisites_for_govproject_ai_manager.md` | 개발 착수 전 | Jira/Confluence/Slack 사전 설정 체크리스트. 자동화 도구 개발 전 필수 확인 |
| `doc2claude_manager_design.md` | 설계 단계 | Doc2Claude Manager 시스템 설계서. 문서 수집 → 변환 → Claude 연동 전체 설계 |
| `govproject_ai_manager_api_keys_guide.md` | 개발 착수 전 | API 키·토큰·Webhook·서비스 계정 발급 가이드. 환경 세팅 시 참조 |

#### 인터뷰 문서

| 파일 | 적용 단계 | 역할 |
|---|---|---|
| `COMPONENT_SPEC.md` | 분석 ~ 설계 단계 | React 컴포넌트 명세 (Tika 칸반 앱). Props, Hook, 이벤트 흐름 정의 |

**Gemini 리서치 위임 흐름**:
```
[분석] 신규 기능 요구사항 접수
  └── Gemini에 PRD 문서 참조 위임
        ├── egov_standard_project_deliverables_flow.md  → 산출물 범위 파악
        ├── jira_confluence_slack_prerequisites...md     → 외부 연동 조건 확인
        └── COMPONENT_SPEC.md                           → 컴포넌트 영향도 분석
              └── 결과 → .claude/docs/research/ 저장
```

---

### 2-5. 산출물 문서 (`docs/01. requirements/`, `docs/00. confluence/`) — 개발 단계 전반

> **적용 시점**: 구현 착수 전 요구사항 확인, Jira 이슈 연동 시, 테스트 작성 시

| 파일 | 단계 | 역할 |
|---|---|---|
| `REQUIREMENTS.md` | 요구사항 정의 → 개발 → 테스트 | 기능 요구사항(FR), 비기능 요구사항(NFR), 사용자 스토리(US), 추적 매트릭스. 구현 기준 문서 |
| `docs/00. confluence/*.md` | 개발 전 단계 | Confluence에서 동기화된 실제 산출물. 요구사항정의서, 주간보고 템플릿 등 |

**개발 흐름에서의 참조 구조**:
```
[요구사항] REQUIREMENTS.md
  ├── FR-001 ~ FR-008  → Controller/Service/DAO 구현 기준
  ├── NFR-001 ~ NFR-006 → 성능·보안·배포 기준
  └── US-001 ~ US-008  → 테스트 케이스 기준

[산출물] docs/00. confluence/*.md (Confluence 동기화본)
  ├── DEL-REQ-001/002-요구사항정의서.md  → 구현 상세 기준
  ├── 02_요구사항_현황판.md              → 진행 현황 트래킹
  └── 10.-주간보고-템플릿.md             → 주간보고 생성 기준
```

---

### 2-6. 내부 관리 문서 (`.claude/docs/`, `work/`) — AI 운영 단계

> **적용 시점**: 새 기능 설계 결정 시, 작업 결과 기록 시, 다음 세션 컨텍스트 연결 시

| 파일 | 적용 시점 | 역할 |
|---|---|---|
| `.claude/docs/confluence-sync-design.md` | Confluence 연동 기능 개발 시 | 동기화 아키텍처 설계서. API 선택 근거, FR/AC 정의 |
| `.claude/docs/research/govproject-ai-manager-validation.md` | GovProject AI Manager 기능 개발 시 | Gemini가 검증한 요구사항 상세화 결과. REQ-NNN 형식, AC, 체크리스트 |
| `.claude/commands/문서동기화.md` | 문서 동기화 실행 시 | `/문서동기화` 슬래시 명령어 정의 |
| `work/confluence-sync-summary.md` | 구현 결과 리뷰 시 | Confluence 동기화 구현 작업 요약 |
| `work/md-document-workflow-analysis.md` | 문서 구조 파악 시 (현재 파일) | 전체 .md 문서 체계 및 워크플로우 적용 시점 분석 |

---

## 3. 전체 워크플로우 적용 타임라인

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 단계         적용 문서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [상시]       CLAUDE.md / AGENTS.md / GEMINI.md
              .claude/rules/*.md (6개)
─────────────────────────────────────────────────────────────
 [착수]       README.md
              PROJECT_SUMMARY.md
              govproject_ai_manager_api_keys_guide.md
─────────────────────────────────────────────────────────────
 [현황분석]   egov_standard_project_deliverables_flow.md
              jira_confluence_slack_prerequisites...md
─────────────────────────────────────────────────────────────
 [요구사항]   docs/01. requirements/REQUIREMENTS.md
              docs/00. confluence/DEL-REQ-001/002-요구사항정의서.md
              docs/00. confluence/02_요구사항_현황판.md
─────────────────────────────────────────────────────────────
 [분석/설계]  docs/02. interview/COMPONENT_SPEC.md
              docs/PRD/doc2claude_manager_design.md
              .claude/docs/confluence-sync-design.md
              .claude/docs/research/govproject-ai-manager-validation.md
─────────────────────────────────────────────────────────────
 [개발]       .claude/rules/coding-principles.md
              .claude/rules/dev-environment.md
              .claude/rules/security.md
─────────────────────────────────────────────────────────────
 [테스트]     .claude/rules/testing.md
              docs/01. requirements/REQUIREMENTS.md (US 기준)
─────────────────────────────────────────────────────────────
 [보고]       docs/00. confluence/10.-주간보고-템플릿.md
              .claude/commands/문서동기화.md
─────────────────────────────────────────────────────────────
 [산출물]     work/*.md  (구현 요약, 분석 결과)
              .claude/docs/research/*.md  (Gemini 결과)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. 문서 간 참조 관계

```
CLAUDE.md
  ├── 참조 → AGENTS.md          (Codex 위임 시)
  ├── 참조 → GEMINI.md          (Gemini 위임 시)
  └── 참조 → .claude/rules/*.md (모든 작업 시)

REQUIREMENTS.md
  ├── 기반 → COMPONENT_SPEC.md  (컴포넌트 설계)
  ├── 기반 → 요구사항정의서.md   (Confluence 산출물)
  └── 기반 → 테스트 케이스      (US → TC 매트릭스)

doc2claude_manager_design.md
  ├── 참조 → jira_confluence_slack_prerequisites.md
  ├── 참조 → govproject_ai_manager_api_keys_guide.md
  └── 참조 → egov_standard_project_deliverables_flow.md

confluence-sync-design.md
  └── 구현 결과 → work/confluence-sync-summary.md

govproject-ai-manager-validation.md
  ├── 검증 대상 → jira_confluence_slack_prerequisites.md
  └── 결과 참조 → 개발 Phase 계획
```

---

## 5. 문서 관리 규칙

| 문서 유형 | 수정 주체 | 수정 시점 | 보관 위치 |
|---|---|---|---|
| 에이전트 정의 (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) | PM 또는 아키텍트 | 역할 변경 시 | 루트 |
| 운영 규칙 (`.claude/rules/`) | PM | 정책 변경 시 | `.claude/rules/` |
| PRD 문서 (`docs/PRD/`) | 분석가 + Gemini | 요구사항 변경 시 | `docs/PRD/` |
| 산출물 (`docs/00. confluence/`) | **자동 동기화** | `python confluence-sync.py sync` 실행 시 | `docs/00. confluence/` |
| 요구사항 (`REQUIREMENTS.md`) | 분석가 | 기능 추가·변경 시 | `docs/01. requirements/` |
| 연구 결과 (`.claude/docs/research/`) | Gemini | 리서치 위임 후 | `.claude/docs/research/` |
| 작업 요약 (`work/`) | Claude | 구현 완료 후 | `work/` |

---

## 6. 누락 및 보완 권장 사항

| 항목 | 현황 | 권장 조치 |
|---|---|---|
| **API 설계서** | 미존재 | `docs/PRD/api-spec.md` 추가 필요 |
| **DB 설계서** | 미존재 | `docs/PRD/db-spec.md` 추가 필요 |
| **테스트 계획서** | 미존재 | `docs/PRD/test-plan.md` 추가 필요 |
| **변경 이력 (CHANGELOG)** | 미존재 | `CHANGELOG.md` 루트에 추가 권장 |
| **Confluence 동기화 산출물** | 4개 (부분) | 전체 폴더 하위 파일 동기화 완성 필요 |
| **운영 가이드** | 미존재 | `work/operation-guide.md` 추가 권장 |

---

**분석자**: Claude Code  
**상태**: 완료
