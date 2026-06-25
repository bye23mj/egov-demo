#!/usr/bin/env python3
"""Slack 알림 테스트 - Claude AI 메시지 전송"""

import requests
import json
from datetime import datetime

# Slack Webhook URL
WEBHOOK_URL = "https://hooks.slack.com/services/<REDACTED-WEBHOOK>"

def send_slack_message(webhook_url, payload):
    """Slack 메시지 전송"""
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "성공"
        else:
            return False, f"상태 코드: {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    # 테스트 메시지 - Claude AI
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 클로드 AI 메시지 전송"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*egov-demo SDD 자동화 시스템*\n\n클로드 AI가 Slack 알림 기능을 정상적으로 설정했습니다."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*상태*\n✅ Webhook 연결"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*시간*\n" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*프로젝트*\negov-demo"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*기능*\nSDD 자동화"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "📋 *SDD 파이프라인 단계*\n\n• Phase 1: `/sdd-collect` - 문서 수집\n• Phase 2: `/sdd-normalize` - 정규화\n• Phase 3: `/sdd-specify` - 요구사항 명세\n• Phase 4: `/sdd-plan` - 설계 계획\n• Phase 5: `/sdd-tasks` - 작업 분해\n• Phase 6: `/sdd-sync` - 결과 동기화 ⭐"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🎯 *다음 단계*\n\n1. JIRA 이슈에 결과 첨부\n2. Confluence에 페이지 생성\n3. 팀에 자동 알림 전송\n\n더 자세한 정보는 `/sdd-sync` 스킬을 참고하세요."
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Claude Code · egov-demo SDD 자동화 · " + datetime.now().strftime('%Y년 %m월 %d일')
                    }
                ]
            }
        ]
    }
    
    print("📤 Slack 메시지 전송 중...\n")
    print(f"Webhook URL: {WEBHOOK_URL[:50]}...")
    print(f"페이로드: {json.dumps(payload, ensure_ascii=False, indent=2)[:200]}...")
    
    success, message = send_slack_message(WEBHOOK_URL, payload)
    
    print("\n" + "="*60)
    if success:
        print("✅ 메시지 전송 성공!")
        print("="*60)
        print(f"\n📍 Slack 채널을 확인하세요.")
        print(f"   → '클로드 AI 메시지 전송' 알림이 도착했습니다.\n")
    else:
        print("❌ 메시지 전송 실패")
        print("="*60)
        print(f"오류: {message}\n")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
