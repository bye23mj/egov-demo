#!/usr/bin/env python3
"""sejongDev 봇 수신 스타터 (Socket Mode).

@sejongDev 멘션을 받아 ① 명령어 파싱 ② 첨부 다운로드 ③ slack-orchestrator 연결지점까지 수행.
공개 서버 불필요(Socket Mode). 토큰은 .env 에서 로드(SLACK_BOT_TOKEN / SLACK_APP_TOKEN).

사전:
    python3 -m pip install slack_bolt slack_sdk
    .env: SLACK_BOT_TOKEN=xoxb-..., SLACK_APP_TOKEN=xapp-...
실행:
    python3 scripts/slack_bot_receiver.py
"""
import os
import re
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))         # slack_review
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # env_loader
import env_loader
env_loader.load_env()
import slack_review_agent

try:
    from slack_bolt import App
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    import requests
except ImportError:
    print("의존성 필요: python3 -m pip install slack_bolt slack_sdk requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DIR = ROOT / "docs" / "06. slack-review"
BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

if not BOT_TOKEN or not APP_TOKEN:
    print("⚠️ .env 에 SLACK_BOT_TOKEN(xoxb-) / SLACK_APP_TOKEN(xapp-) 설정 필요")
    sys.exit(1)

app = App(token=BOT_TOKEN)

# 명령어 → 라우팅 키워드 (slack-orchestrator 라우팅표와 일치)
# "데이터모델링"(검토 아님)은 생성→구축 체이닝: da-agent → dba-agent(실제 테이블 생성)
ROUTE = {
    "데이터모델링": "da-agent→dba-agent",
    "데이터모델링검토": "da-agent", "erd검토": "da-agent", "모델검토": "da-agent",
    "표준화검토": "metadata-agent", "용어검토": "metadata-agent",
    "db검토": "dba-agent", "테이블검토": "dba-agent", "ddl검토": "dba-agent",
    "코드검토": "python-reviewer", "파이썬검토": "python-reviewer",
    "설계검토": "design-reviewer", "보안검토": "security-auditor",
}


def parse_command(text):
    """멘션 텍스트에서 <@BOT> 제거 후 첫 명령어 추출."""
    cleaned = re.sub(r"<@[A-Z0-9]+>", "", text or "").strip()
    cmd = cleaned.split()[0] if cleaned else ""
    agent = ROUTE.get(cmd.lower())
    return cmd, agent, cleaned


def download_attachments(files, dest: Path):
    """Slack 첨부를 Bearer 토큰으로 다운로드(files:read 필요)."""
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    for f in files or []:
        url = f.get("url_private_download") or f.get("url_private")
        name = f.get("name", f.get("id", "file"))
        if not url:
            continue
        r = requests.get(url, headers={"Authorization": f"Bearer {BOT_TOKEN}"}, timeout=30)
        if r.status_code == 200:
            (dest / name).write_bytes(r.content)
            saved.append((name, len(r.content)))
    return saved


def post_review_md(client, channel, thread_ts, md_path):
    """검토결과.md 를 Slack에 업로드. files:write 없으면 내용을 코드블록으로 게시(폴백)."""
    md_path = Path(md_path)
    if not md_path.exists():
        return
    try:
        client.files_upload_v2(channel=channel, thread_ts=thread_ts,
                               file=str(md_path), title=md_path.name,
                               initial_comment=":page_facing_up: 검토결과 상세")
        return "uploaded"
    except Exception:
        text = md_path.read_text(encoding="utf-8")
        chunks = [text[i:i + 3500] for i in range(0, len(text), 3500)]
        client.chat_postMessage(channel=channel, thread_ts=thread_ts,
            text=f":page_facing_up: *{md_path.name}* (파일첨부 권한 없어 내용 게시 · {len(chunks)}조각)")
        for ck in chunks[:8]:
            client.chat_postMessage(channel=channel, thread_ts=thread_ts, text="```\n" + ck + "\n```")
        return "posted"


@app.event("app_mention")
def on_mention(event, say, client, logger):
    text = event.get("text", "")
    files = event.get("files", [])
    thread_ts = event.get("thread_ts") or event.get("ts")
    cmd, agent, full = parse_command(text)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    work = REVIEW_DIR / f"{ts}_{cmd or 'cmd'}" / "attachments"
    saved = download_attachments(files, work)

    # 1) 수신 확인 + 라우팅 결과 스레드 응답
    lines = [f":inbox_tray: 수신: *{cmd or '(명령없음)'}*"]
    if agent:
        lines.append(f":robot_face: 라우팅 → *{agent}*")
    else:
        lines.append(":grey_question: 매칭 에이전트 없음 — 지원 명령: "
                     + ", ".join(sorted({v for v in ROUTE})))
    if saved:
        lines.append("첨부 " + str(len(saved)) + "개 다운로드: "
                     + ", ".join(f"{n}({sz}B)" for n, sz in saved))
        lines.append(f"저장: `{work.relative_to(ROOT)}`")
    else:
        lines.append("첨부 없음")
    say(text="\n".join(lines), thread_ts=thread_ts)

    # 2) ── 검토 실행 (slack-orchestrator 4~8단계: 분석·검토·요약·다음액션) ──
    if agent and saved:
        try:
            say(text=f":hourglass_flowing_sand: Claude {agent} 검토 진행 중… (수 분 소요)", thread_ts=thread_ts)
            md_path, slack_summary = slack_review_agent.run_review_via_claude(
                cmd, agent, [work / n for n, _ in saved], work.parent)
            say(text=slack_summary, thread_ts=thread_ts)
            # 검토결과.md 를 Slack에 업로드(또는 내용 게시)
            mode = post_review_md(client, event["channel"], thread_ts, md_path)
            logger.info(f"[review] cmd={cmd} agent={agent} → {md_path} (md:{mode})")
        except Exception as e:
            say(text=f":warning: 검토 중 오류: {e}", thread_ts=thread_ts)
            logger.exception("review failed")
    elif not agent:
        say(text=":grey_question: 지원 명령으로 다시 멘션해 주세요.", thread_ts=thread_ts)
    elif not saved:
        say(text=":paperclip: 검토할 첨부파일을 함께 올려 주세요.", thread_ts=thread_ts)


if __name__ == "__main__":
    print("⚡️ sejongDev 봇 수신 시작 (Socket Mode). Ctrl+C 종료.")
    SocketModeHandler(app, APP_TOKEN).start()
