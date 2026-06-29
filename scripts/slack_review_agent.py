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


def build_prompt(cmd, agent, files, md_path, reqid=None):
    reqid = reqid or cmd
    if "→" in (agent or "") or agent == "da-agent→dba-agent":
        return build_prompt_chain(cmd, files, md_path, reqid)
    file_list = "\n".join(f"- {f}" for f in files)
    notify = "python3 scripts/da_progress_notify.py"
    return f"""너는 egov-demo 의 **slack-agent**(Slack 접점 오케스트레이터)다. slack-orchestrator 스킬에 따라
전문 에이전트 '{agent}'(db-agent 계열)를 호출해 아래 첨부를 검토하고, **진행 단계마다 Slack에 공유**하라.

[명령] {cmd}
[요구사항번호] {reqid}
[라우팅 에이전트] {agent}
[첨부 파일]
{file_list}

[진행 단계 — 각 단계 시작/완료를 반드시 Slack에 공유]
Slack 공유는 다음 명령으로 한다(webhook→#세종개발팀, 미설정 시 자동 스킵):
  {notify} step --reqid "{reqid}" --step "<단계명>" --status in_progress|completed --note "<요지>"
시작 시 1회: {notify} start --reqid "{reqid}" --steps "1.첨부분석,2.{agent}검토,3.결과정리"

  1) **첨부분석**: in_progress 공유 → 첨부를 읽는다(.xls→xlrd, .xlsx→openpyxl, .docx→unzip word/document.xml, .pdf→Read, csv/tsv/sql→직접) → 핵심 파악 후 completed 공유(note: 테이블/컬럼 수 등).
  2) **{agent}검토**: in_progress 공유 → '{agent}' 기준으로 분석한다.
     - da-agent: 엔터티·정규화·식별자(PK/UK)·관계·표준도메인·표준용어·테이블명명규칙(.claude/docs/standards/테이블명명규칙.md)
     - dba-agent: DDL·제약·인덱스·타입/길이·명명
     - metadata-agent: 표준용어/단어/도메인/코드 매핑(docs/03. metadata TSV)
     → 판정 요지로 completed 공유(note: 보완/부적합 건수).
  3) **결과정리**: in_progress 공유 → 항목별 적합/보완/부적합·근거를 표로 '{md_path}' 에 Markdown 저장 → completed 공유.
  마지막: {notify} done --reqid "{reqid}" --note "<종합 요약>"

[규칙] 원본 첨부는 수정하지 않는다(결과 md만 작성). Slack 공유 실패는 검토를 막지 않는다.

[출력] 작업을 마치면 **마지막 메시지로 Slack 요약만** 출력한다(다른 설명 없이, 5줄 이내, ':mag:'로 시작):
:mag: {cmd} 검토 완료 — {agent}
• 종합: <적합/보완 N건/부적합 M건>
• 핵심 지적: <3건 이내>
:arrow_right: 다음: <다음 액션>
"""


def build_prompt_chain(cmd, files, md_path, reqid=None):
    """데이터모델링(생성·구축) — da-agent 생성 → dba-agent 실제 테이블 생성 체이닝."""
    reqid = reqid or cmd
    file_list = "\n".join(f"- {f}" for f in files)
    notify = "python3 scripts/da_progress_notify.py"
    return f"""너는 egov-demo 의 **slack-agent**(Slack 접점 오케스트레이터)다. 명령 '{cmd}'는 검토가 아니라
**da-orchestrator 7단계 파이프라인 + 구축**이다. da-orchestrator 스킬의 7단계를 그대로 수행하고, 각 단계의 진행을 TodoList와 Slack으로 공유하라.

[요구사항번호] {reqid}   ← 모든 산출물 파일명·경로·reqid 에 이 값을 사용한다.
[입력 첨부(요구사항/모델 정의)]
{file_list}

[필수 — TodoList 등록(시작 시 즉시)]
`TodoWrite` 로 아래 11단계를 모두 등록한다(**da 7단계 + dba 3단계 + 등록 1단계**). 각 단계 진입 시 `in_progress`(동시 1개), 완료 시 `completed`로 갱신한다.
  [da 7단계]  1.데이터모델링  2.표준화검토  3.데이터구조검증  4.산출물관리  5.변경관리  6.품질관리  7.데이터분석
  [dba 3단계] 8.DB프로비저닝  9.DB객체생성  10.CRUD생성
  [등록]      11.Confluence등록

[필수 — 단계별 Slack 공유(TodoWrite와 1:1)]
시작: {notify} start --reqid "{reqid}" --steps "1.데이터모델링,2.표준화검토,3.데이터구조검증,4.산출물관리,5.변경관리,6.품질관리,7.데이터분석,8.DB프로비저닝,9.DB객체생성,10.CRUD생성,11.Confluence등록"
각 단계 진입: {notify} step --reqid "{reqid}" --step "{{N.단계명}}" --status in_progress --note "<요지>"
각 단계 완료: {notify} step --reqid "{reqid}" --step "{{N.단계명}}" --status completed --note "<핵심결과>"
마지막: {notify} done --reqid "{reqid}" --note "<산출물·테이블·Confluence URL 요약>"
> TodoWrite 갱신과 notify 발송은 **반드시 짝지어** 호출한다(누락 금지). 발송 실패·미설정은 진행을 막지 않는다.

[수행 — da-orchestrator 7단계 + 구축]
※ **각 단계는 이전 단계의 산출물을 입력으로 순차 수행**한다(건너뛰기 금지). 단계 완료(파일 생성·검증 통과)를 확인한 뒤에만 다음 단계로 간다.
  1.데이터모델링: 첨부를 읽어(.xls→xlrd, .xlsx→openpyxl, .docx→unzip, .pdf→Read) 엔터티·테이블·컬럼·식별자·관계를 도출하고 `docs/04. db-deliverables/{reqid}/{reqid}-db-modeling.md` 작성.
  2.표준화검토(**실제 검증 필수**): metadata-standardize 절차로 각 컬럼(한글명)을 `docs/03. metadata` TSV에서 **Grep 조회**(공공표준 우선→없으면 KOMSA)해 표준용어명·영문약어명·표준도메인명·표준코드명(`_CD` 한정)을 채택하고, 컬럼별 **`표준검토상태`를 적합/보완/부적합으로 판정**한다(**`미검토`로 남기지 않는다**). 공공·기관 어디에도 없으면 `.claude/docs/standards/` 규칙으로 기관(KOMSA)표준을 생성·TSV 등록 후 반영한다. 검토 결과는 표준검토결과로 기록.
  3.데이터구조검증: 정규화·식별자(PK/UK/FK)·참조무결성·도메인·명명(.claude/docs/standards/테이블명명규칙.md)을 점검. `보완/부적합`이면 1·2단계로 환류.
  4.산출물관리: `data-output-management` 스킬에 따라 **1~3단계의 설계·표준화·검증 결과를 반영해 산출물 8종을 xlsx로 직접 생성**한다(openpyxl 사용, .md 대체 금지). 컬럼 헤더는 `.claude/skills/data-output-management/references/column-specs.md` 규격을 따른다. 파일명 `{reqid}-{{문서명}}.xlsx`, 저장 `docs/04. db-deliverables/{reqid}/`. 논리/물리 ERD는 Mermaid `erDiagram`. 마지막에 산출물관리대장으로 취합.
     - 파일 게이트: `ls "docs/04. db-deliverables/{reqid}/"*.xlsx | wc -l` ≥ 9(8종+산출물관리대장) 확인. 미달이면 누락분 생성(.md로 종료 금지).
     - **값 검증 게이트**: 컬럼정의서·애트리뷰트정의서의 **표준용어명·표준도메인명이 전 행 채워지고**(코드성 컬럼은 표준코드명), **`표준검토상태`에 `미검토`가 0건**(전부 적합/보완/부적합)인지 확인한다. `미검토`나 빈 값이 남으면 **2단계로 돌아가 실제 검증을 반영**한 뒤 산출물을 다시 생성한다(자동 추정값만 넣고 미검토로 종료 금지).
  5.변경관리: 설계 결정→ADR, 스키마 변경→가역·무중단 마이그레이션(`migrations/`) 정의. (실 DB 실행은 8단계)
  6.품질관리: 표준준수율·완전성·유효성·개인정보 표기를 점검(NCR). 부적합은 3·4단계 환류, 미결 시 완료 보고 금지.
  7.데이터분석: 규모·코드분포·개인정보 범위·표준화효과 요약.
  ── 이하 dba-orchestrator 3단계(구축) ──
  8.DB프로비저닝: dba-orchestrator 1단계. db-provisioning 으로 docker `oracle-xe-egov`(Oracle 11g) 컨테이너 기동·healthcheck 확인(이미 떠 있으면 접속만 확인). 미통과 시 9단계 보류(게이트).
  9.DB객체생성: dba-orchestrator 2단계. 테이블정의서·컬럼정의서(xlsx)에서 DDL(CREATE TABLE+INDEX+COMMENT(테이블·컬럼)+drop 동반)을 생성해 **반드시 `docs/05. db-build/{reqid}/ddl/{{순번}}_{{테이블}}.sql` 파일로 저장**한 뒤, 그 파일을 sqlplus로 실행해 **대상 DB(komsa)에 실제 생성**한다(동일 테이블 DROP 후 재생성). 생성 후 컬럼 수·PK·제약 검증. 불일치 시 4단계 환류.
  10.CRUD생성: dba-orchestrator 3단계. crud-sql-generation 으로 테이블별 self-contained 스크립트(CREATE+INDEX+COMMENT+CRUD 5종)를 **`docs/05. db-build/{reqid}/sql/{{테이블}}_crud.sql` 파일로 저장**한다.
  > **dba 산출물 게이트**: `ls "docs/05. db-build/{reqid}/ddl/"*.sql "docs/05. db-build/{reqid}/sql/"*.sql 2>/dev/null | wc -l` 가 1 이상인지 확인한다. **DB에 테이블만 만들고 db-build 파일을 남기지 않은 채 종료하지 말 것**(이전 버전 버그).
  11.Confluence등록: 산출물(xlsx)을 `python3 scripts/upload_pages_in_folders.py` 로 등록(멱등·무결성 검증). 등록 위치 URL 확보(기본 폴더 https://nsonesoft.atlassian.net/wiki/spaces/TNYUU/folder/677871627). 접근불가/미인증 시 사유 남기고 생략.

[정리] da 7단계 + dba 3단계 결과 + 생성 xlsx 8종 + **db-build 산출물(ddl/·sql/ 파일 목록)** + 생성 테이블(명·컬럼수·PK) + Confluence URL 을 '{md_path}' 에 Markdown으로 저장한다.

[안전] 실 DB 변경(DROP/CREATE)이므로 대상 계정(komsa)·재생성 여부를 결과에 명시한다. 운영 DB에는 실행하지 않는다.

[출력] 마지막 메시지로 Slack 요약만 출력(6줄 이내, ':hammer_and_wrench:'로 시작):
:hammer_and_wrench: {cmd}({reqid}) da 7단계 + dba 3단계 완료
• 산출물: <xlsx 8종 생성 여부>
• 생성 테이블: <테이블명 목록(개수)> / CRUD: <생성 여부>
• :page_facing_up: Confluence: <등록 위치 URL>
:arrow_right: 다음: <데이터 적재 등>
"""


def run_review_via_claude(cmd, agent, files, workdir, timeout=None, reqid=None):
    """Claude 헤드리스로 실제 에이전트 검토/구축 수행. (md_path, slack_summary) 반환."""
    reqid = reqid or cmd
    is_chain = "→" in (agent or "")
    if timeout is None:
        timeout = 1200 if is_chain else 600   # 생성·테이블생성 체이닝은 더 길게
    workdir = Path(workdir).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    md_path = workdir / f"{cmd}-검토결과.md"
    prompt = build_prompt(cmd, agent, [Path(f).resolve() for f in files], md_path, reqid=reqid)

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
