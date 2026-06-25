#!/usr/bin/env python3
"""SDD 파이프라인 완료 알림 테스트"""

import os
import sys
sys.path.insert(0, '/Users/ai/vscode/egov-demo')

from scripts.confluence.slack_notifier import SlackNotifier
from datetime import datetime

def main():
    print("🚀 SDD 파이프라인 완료 알림 테스트\n")
    print("="*60)
    
    # Slack 알림 초기화
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL 환경변수를 찾을 수 없습니다")
        return False
    
    print(f"✓ Webhook URL 로드됨")
    print(f"  {webhook_url[:50]}...\n")
    
    notifier = SlackNotifier(webhook_url=webhook_url)
    
    # Phase별 통계
    print("📊 테스트 통계 정보:")
    stats = {
        'requirements': 30,
        'stories': 4,
        'subtasks': 33,
        'tables': 5,
        'files': 8
    }
    
    for key, value in stats.items():
        print(f"   • {key}: {value}")
    
    print("\n📤 Slack 메시지 전송 중...\n")
    
    # 파이프라인 완료 알림 전송
    success = notifier.notify_pipeline_complete(
        project_key="GOVPJT",
        run_id="REQ-GOVPJT-20260611",
        stats=stats
    )
    
    print("="*60)
    if success:
        print("✅ SDD 파이프라인 완료 알림 발송 성공!\n")
        print("📍 Slack 채널 확인:")
        print("   🎉 SDD 자동화 파이프라인 완료!")
        print("   프로젝트: GOVPJT")
        print("   요구사항: 30개 | Story: 4개 | Sub-task: 33개")
        print("   생성 파일: 8개 | 완료 테이블: 5개\n")
    else:
        print("❌ 메시지 전송 실패")
        return False
    
    # 추가 Phase별 알림 테스트
    print("\n📋 Phase별 알림 테스트:\n")
    
    tests = [
        ("Phase 1", "Collection", lambda: notifier.notify_collection_complete("GOVPJT", "REQ-001", 5, 11)),
        ("Phase 2", "Normalization", lambda: notifier.notify_normalization_complete("GOVPJT", "REQ-001", 11)),
        ("Phase 3", "Specification", lambda: notifier.notify_specification_complete("GOVPJT", "REQ-001", 30, 12)),
        ("Phase 4", "Planning", lambda: notifier.notify_planning_complete("GOVPJT", "REQ-001", 5, 4, 5)),
        ("Phase 5", "Tasks", lambda: notifier.notify_tasks_complete("GOVPJT", "REQ-001", 4, 33)),
    ]
    
    for phase, name, notify_func in tests:
        success = notify_func()
        status = "✓" if success else "✗"
        print(f"{status} {phase}: {name} 알림 발송")
    
    print("\n" + "="*60)
    print("✅ 모든 테스트 완료!")
    print("="*60)
    print("\n💡 이제 다음 명령으로 실제 SDD 파이프라인을 실행할 수 있습니다:\n")
    print("  /sdd-collect     # Phase 1: 문서 수집")
    print("  /sdd-normalize   # Phase 2: 정규화")
    print("  /sdd-specify     # Phase 3: 명세화")
    print("  /sdd-plan        # Phase 4: 계획")
    print("  /sdd-tasks       # Phase 5: 작업분해")
    print("  /sdd-sync        # Phase 6: JIRA/Confluence/Slack 동기화\n")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
