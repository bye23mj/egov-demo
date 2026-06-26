#!/usr/bin/env python3
"""옵션 B — 봇이 Claude(헤드리스)를 호출해 실제 전문 에이전트로 검토.

slack_bot_receiver 의 '연결 지점'에서 호출한다. `claude -p` 로 egov-demo 프로젝트
컨텍스트(.claude/agents·skills)를 로드해 {agent}/slack-orchestrator 로 검토를 수행하고,
{cmd}-검토결과.md 를 작성한 뒤 Slack 요약을 stdout 으로 받는다.

요구: `claude` CLI 인증 완료(로컬). 첨부 .xls 는 xlrd 필요.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_TOOLS = ["Read", "Write", "Bash", "Grep", "Glob", "Skill", "Task"]


def build_prompt(cmd, agent, files, md_path):
    if "→" in (agent or "") or agent == "da-agent→dba-agent":
        return build_prompt_chain(cmd, files, md_path)
    file_list = "\n".join(f"- {f}" for f in files)
    notify = "python3 scripts/da_progress_notify.py"
    return f"""너는 egov-demo 의 **slack-agent**(Slack 접점 오케스트레이터)다. slack-orchestrator 스킬에 따라
전문 에이전트 '{agent}'(db-agent 계열)를 호출해 아래 첨부를 검토하고, **진행 단계마다 Slack에 공유**하라.

[명령] {cmd}
[라우팅 에이전트] {agent}
[첨부 파일]
{file_list}

[진행 단계 — 각 단계 시작/완료를 반드시 Slack에 공유]
Slack 공유는 다음 명령으로 한다(webhook→#세종개발팀, 미설정 시 자동 스킵):
  {notify} step --reqid "{cmd}" --step "<단계명>" --status in_progress|completed --note "<요지>"
시작 시 1회: {notify} start --reqid "{cmd}" --steps "1.첨부분석,2.{agent}검토,3.결과정리"

  1) **첨부분석**: in_progress 공유 → 첨부를 읽는다(.xls→xlrd, .xlsx→openpyxl, .docx→unzip word/document.xml, .pdf→Read, csv/tsv/sql→직접) → 핵심 파악 후 completed 공유(note: 테이블/컬럼 수 등).
  2) **{agent}검토**: in_progress 공유 → '{agent}' 기준으로 분석한다.
     - da-agent: 엔터티·정규화·식별자(PK/UK)·관계·표준도메인·표준용어·테이블명명규칙(.claude/rules/테이블명명규칙.md)
     - dba-agent: DDL·제약·인덱스·타입/길이·명명
     - metadata-agent: 표준용어/단어/도메인/코드 매핑(docs/03. metadata TSV)
     → 판정 요지로 completed 공유(note: 보완/부적합 건수).
  3) **결과정리**: in_progress 공유 → 항목별 적합/보완/부적합·근거를 표로 '{md_path}' 에 Markdown 저장 → completed 공유.
  마지막: {notify} done --reqid "{cmd}" --note "<종합 요약>"

[규칙] 원본 첨부는 수정하지 않는다(결과 md만 작성). Slack 공유 실패는 검토를 막지 않는다.

[출력] 작업을 마치면 **마지막 메시지로 Slack 요약만** 출력한다(다른 설명 없이, 5줄 이내, ':mag:'로 시작):
:mag: {cmd} 검토 완료 — {agent}
• 종합: <적합/보완 N건/부적합 M건>
• 핵심 지적: <3건 이내>
:arrow_right: 다음: <다음 액션>
"""


def build_prompt_chain(cmd, files, md_path):
    """데이터모델링(생성·구축) — da-agent 생성 → dba-agent 실제 테이블 생성 체이닝."""
    file_list = "\n".join(f"- {f}" for f in files)
    notify = "python3 scripts/da_progress_notify.py"
    return f"""너는 egov-demo 의 **slack-agent**(Slack 접점 오케스트레이터)다. 명령 '{cmd}'는 검토가 아니라
**생성→구축 파이프라인**이다. da-agent 로 산출물을 생성한 뒤 dba-agent 로 **실제 테이블을 생성**하라.
각 단계 시작/완료를 반드시 Slack에 공유한다.

[입력 첨부(요구사항/모델 정의)]
{file_list}

[Slack 진행 공유]
시작: {notify} start --reqid "{cmd}" --steps "1.첨부분석,2.da-agent생성,3.dba-agent테이블생성,4.정리"
각 단계: {notify} step --reqid "{cmd}" --step "<단계명>" --status in_progress|completed --note "<요지>"
마지막: {notify} done --reqid "{cmd}" --note "<생성 산출물·테이블 요약>"

[수행]
  1) **첨부분석**(공유): 첨부를 읽어(.xls→xlrd, .xlsx→openpyxl, .docx→unzip, .pdf→Read) 요구사항·엔터티·컬럼을 파악한다.
  2) **da-agent생성**(공유): da-agent(da-orchestrator)로 데이터모델링→표준화→구조검증→산출물 7종을 생성한다.
     - 산출물은 `docs/04. db-deliverables/{cmd}/` 에 저장. 테이블정의서·컬럼정의서 포함.
     - 테이블명명규칙(.claude/rules/테이블명명규칙.md)·표준용어(docs/03. metadata TSV) 적용.
  3) **dba-agent테이블생성**(공유): dba-agent(dba-orchestrator)로 위 테이블정의서·컬럼정의서에서 DDL을 생성하고
     **대상 DB(Oracle 11g, komsa 계정)에 테이블을 실제 생성**한다(기존 동일 테이블 있으면 DROP 후 재생성).
     - 실행은 docker 컨테이너 `oracle-xe-egov` 의 sqlplus 사용(기존 db-build 절차 동일).
     - 생성 후 컬럼 수·PK·제약을 조회해 검증한다.
  4) **정리**(공유): 생성 산출물 목록 + **생성된 테이블 목록(테이블명·컬럼수·PK)** 을 '{md_path}' 에 Markdown으로 저장한다.

[안전] 실 DB 변경(DROP/CREATE)이므로 대상 계정(komsa)·재생성 여부를 결과에 명시한다. 운영 DB에는 실행하지 않는다.

[출력] 마지막 메시지로 Slack 요약만 출력(5줄 이내, ':hammer_and_wrench:'로 시작):
:hammer_and_wrench: {cmd} 생성·구축 완료 — da-agent→dba-agent
• 산출물: <7종 생성 여부>
• 생성 테이블: <테이블명 목록(개수)>
:arrow_right: 다음: <CRUD/적재/Confluence 등록 등>
"""


def run_review_via_claude(cmd, agent, files, workdir, timeout=None):
    """Claude 헤드리스로 실제 에이전트 검토/구축 수행. (md_path, slack_summary) 반환."""
    is_chain = "→" in (agent or "")
    if timeout is None:
        timeout = 1200 if is_chain else 600   # 생성·테이블생성 체이닝은 더 길게
    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    md_path = workdir / f"{cmd}-검토결과.md"
    prompt = build_prompt(cmd, agent, [Path(f).resolve() for f in files], md_path)

    cmd_args = ["claude", "-p", prompt,
                "--permission-mode", "acceptEdits",
                "--allowedTools", *ALLOWED_TOOLS]
    try:
        cp = subprocess.run(cmd_args, cwd=str(ROOT), capture_output=True,
                            text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return md_path, f":warning: {cmd} 검토 시간 초과({timeout}s). 첨부 규모를 줄이거나 재시도하세요."

    out = (cp.stdout or "").strip()
    if cp.returncode != 0 and not out:
        return md_path, f":warning: 검토 실행 오류(rc={cp.returncode}): {(cp.stderr or '')[:300]}"

    # Slack 요약: Claude 최종 출력에서 ':mag:' 블록 우선 추출
    summary = out
    if ":mag:" in out:
        summary = out[out.index(":mag:"):].strip()
    summary = "\n".join(summary.splitlines()[:6])
    if md_path.exists():
        try:
            disp = md_path.relative_to(ROOT)
        except ValueError:
            disp = md_path
        summary += f"\n(상세: `{disp}`)"
    return md_path, summary or f":white_check_mark: {cmd} 검토 완료(요약 출력 없음). md 확인."


if __name__ == "__main__":
    import sys
    # 수동 테스트: python3 slack_review_agent.py {workdir}
    wd = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if wd:
        fs = list((wd / "attachments").iterdir())
        p, s = run_review_via_claude("데이터모델링검토", "da-agent", fs, wd)
        print("=== SUMMARY ===\n" + s)
