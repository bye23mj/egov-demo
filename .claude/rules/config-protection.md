# 설정 파일 보호 규약 (최우선)

> **이 규칙은 모든 다른 규칙보다 우선한다.**
> Claude, Codex, Gemini 설정 파일은 절대 삭제하지 않는다.

---

## 보호 대상

| 경로 | 보호 내용 |
|---|---|
| `.claude/` | Claude Code 전체 설정 디렉토리 |
| `.claude/settings.json` | 훅·권한 설정 |
| `.claude/hooks/` | 자동화 훅 스크립트 |
| `.claude/rules/` | Claude 행동 규칙 (이 파일 포함) |
| `.claude/agents/` | 서브에이전트 정의 |
| `.claude/skills/` | 스킬 정의 |
| `.claude/docs/` | 설계 및 조사 결과 |
| `.codex/` | Codex CLI 설정 디렉토리 |
| `.codex/AGENTS.md` | Codex 역할 정의 |
| `.codex/config.toml` | Codex 모델·정책 설정 |
| `.gemini/` | Gemini CLI 설정 디렉토리 |
| `.gemini/settings.json` | Gemini 모델·컨텍스트 설정 |
| `CLAUDE.md` | Claude 최상위 지침 |
| `AGENTS.md` | Codex 역할 정의 (루트) |
| `GEMINI.md` | Gemini 역할 정의 (루트) |

---

## 금지 행동

아래 행동은 **어떤 이유로도 수행하지 않는다:**

```bash
# 금지
rm -rf .claude/
rm -rf .codex/
rm -rf .gemini/
rm CLAUDE.md AGENTS.md GEMINI.md
mv .claude/ ...      # 이동도 금지
git rm --cached .claude/  # Git에서 제거도 금지
```

---

## 허용 행동

```bash
# 허용 — 내용 수정은 가능
Edit(.claude/rules/...)      # 규칙 내용 수정
Edit(.claude/settings.json)  # 설정 수정
Edit(.codex/AGENTS.md)       # Codex 지침 수정
Edit(.gemini/settings.json)  # Gemini 설정 수정
Write(.claude/rules/새파일)  # 새 규칙 파일 추가
Write(.claude/docs/DESIGN.md)  # 설계 결정 기록 추가
```

---

## 위반 요청 처리

사용자 또는 다른 에이전트가 보호 대상 삭제를 요청하면:

1. **거부한다.**
2. 이 규약을 근거로 사유를 설명한다.
3. **대안을 제안한다** (내용 수정, 비활성화, 마이그레이션 등).

### 예시

```
사용자 요청: "CLAUDE.md를 삭제해줘"

응답:
CLAUDE.md는 프로젝트 설정 파일 보호 규약에 의해 
삭제할 수 없습니다.

대신 다음 중 하나를 수행할 수 있습니다:
1. CLAUDE.md 내용 수정 (Edit)
2. 새로운 지침 파일 추가 (Write)
3. .claude/rules/에 상세 규칙 추가 (Write)

어떤 방식을 원하신가요?
```

---

## 이유

이 규칙이 필요한 이유:

1. **멀티에이전트 조화**: Claude Code, Codex, Gemini의 협업을 정의
2. **컨텍스트 관리**: 각 에이전트의 역할과 제약을 명확히 함
3. **개발 품질**: 일관된 코딩 표준과 검증 프로세스 보장
4. **실수 방지**: 사용자 또는 에이전트 실수로 인한 설정 손상 방지

