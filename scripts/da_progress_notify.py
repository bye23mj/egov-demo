#!/usr/bin/env python3
"""da-orchestrator(DA 7단계 파이프라인) 진행상황 Slack 발송 헬퍼.

da-orchestrator가 단계 전환마다 호출한다. SLACK_WEBHOOK_URL(환경변수 또는
저장소 루트 .env)을 사용한다. 미설정 시 발송을 건너뛰고 0으로 종료한다(파이프라인 비차단).

사용법:
  # 시작: TodoList 등록 공유
  da_progress_notify.py start  --reqid 선박기본정보 \
      --steps "1.데이터모델링,2.표준화검토,3.데이터구조검증,4.산출물관리,5.변경관리,6.품질관리,7.데이터분석"
  # 단계 전환
  da_progress_notify.py step   --reqid 선박기본정보 --step "2.표준화검토" --status in_progress
  da_progress_notify.py step   --reqid 선박기본정보 --step "2.표준화검토" --status completed --note "KOMSA 5건 등록"
  # 완료
  da_progress_notify.py done   --reqid 선박기본정보 --note "산출물 7종 생성, 적재 68,933행"
"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

import requests

ICON = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}


def load_webhook_url():
    url = os.getenv("SLACK_WEBHOOK_URL")
    if url:
        return url
    # 보조 로드 — .claude/.env(표준) → .env(루트, 하위호환)
    root = Path(__file__).resolve().parent.parent
    for env_path in (root / ".claude" / ".env", root / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("SLACK_WEBHOOK_URL=") and not line.startswith("#"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def post(blocks):
    url = load_webhook_url()
    if not url:
        print("⚠️ SLACK_WEBHOOK_URL 미설정 — 발송 건너뜀(파이프라인 계속)")
        return 0
    try:
        r = requests.post(url, json={"blocks": blocks}, timeout=10)
        if r.status_code == 200:
            print("✅ Slack 발송 성공")
            return 0
        print(f"❌ Slack 발송 실패: HTTP {r.status_code}")
        return 0  # 비차단
    except Exception as e:
        print(f"❌ Slack 발송 예외: {e}")
        return 0  # 비차단


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def cmd_start(a):
    steps = [s.strip() for s in a.steps.split(",") if s.strip()]
    todo = "\n".join(f"{ICON['pending']} {s}" for s in steps)
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": f"🚀 DA 파이프라인 시작: {a.reqid}"}},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"*요구사항*: `{a.reqid}`\n*TodoList ({len(steps)}단계)*\n{todo}"}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": f"da-orchestrator · {now()}"}]},
    ]
    return post(blocks)


def cmd_step(a):
    icon = ICON.get(a.status, "•")
    label = {"in_progress": "진행 시작", "completed": "완료", "pending": "대기"}.get(a.status, a.status)
    text = f"{icon} *{a.step}* — {label}"
    if a.note:
        text += f"\n> {a.note}"
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": f"{a.reqid} · {now()}"}]},
    ]
    return post(blocks)


def cmd_done(a):
    text = f"🎉 *DA 파이프라인 완료: {a.reqid}*"
    if a.note:
        text += f"\n{a.note}"
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": f"da-orchestrator · {now()}"}]},
    ]
    return post(blocks)


def main():
    p = argparse.ArgumentParser(description="DA 파이프라인 진행상황 Slack 발송")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start"); s.add_argument("--reqid", required=True); s.add_argument("--steps", required=True); s.set_defaults(fn=cmd_start)
    s = sub.add_parser("step");  s.add_argument("--reqid", required=True); s.add_argument("--step", required=True)
    s.add_argument("--status", required=True, choices=["pending", "in_progress", "completed"]); s.add_argument("--note", default=""); s.set_defaults(fn=cmd_step)
    s = sub.add_parser("done");  s.add_argument("--reqid", required=True); s.add_argument("--note", default=""); s.set_defaults(fn=cmd_done)

    a = p.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
