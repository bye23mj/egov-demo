#!/usr/bin/env python3
"""JIRA 토큰 설정 검증"""
# === .env 자동 로드 (의존성 없음) ===
import sys as _sys
from pathlib import Path as _Path
_root = _Path(__file__).resolve()
while _root.parent != _root and not (_root / '.env').is_file():
    _root = _root.parent
_sys.path.insert(0, str(_root))
try:
    from env_loader import load_env as _load_env
    _load_env()
except Exception:
    pass
# === /.env 자동 로드 ===

import os
import sys

# 환경변수 확인
jira_email = os.getenv('JIRA_EMAIL')
jira_token = os.getenv('JIRA_TOKEN')

print("🔍 JIRA 토큰 설정 검증\n")
print("="*60)

# 1. 이메일 확인
if jira_email:
    print(f"✓ JIRA_EMAIL: {jira_email}")
else:
    print("✗ JIRA_EMAIL: 설정되지 않음")
    print("  → export JIRA_EMAIL='${JIRA_EMAIL}'")

# 2. 토큰 확인
if jira_token:
    print(f"✓ JIRA_TOKEN: {jira_token[:10]}... (길이: {len(jira_token)})")
    
    # 토큰 유효성 기본 검사
    if len(jira_token) >= 30:
        print("✓ 토큰 형식: 유효")
    else:
        print("✗ 토큰 형식: 의심스러움 (너무 짧음)")
else:
    print("✗ JIRA_TOKEN: 설정되지 않음")
    print("  → export JIRA_TOKEN='your-api-token'")

print("="*60)

# 3. 연결 테스트 (선택사항)
if jira_email and jira_token:
    print("\n🧪 JIRA 연결 테스트...\n")
    
    try:
        sys.path.insert(0, '/Users/ai/vscode/egov-demo')
        from scripts.confluence.jira_api import JiraAPI, JiraConfig
        
        config = JiraConfig()
        jira = JiraAPI(config)
        
        result = jira.test_connection()
        
        if result:
            print("✅ JIRA 연결 성공!")
            print("   프로젝트 목록 조회 가능")
        else:
            print("⚠️  JIRA 연결 실패 (권한 확인 필요)")
    except Exception as e:
        print(f"⚠️  연결 테스트 오류: {e}")
        print("   토큰이 유효한지 확인하세요")

print("\n💡 다음 단계:")
print("   1. 위의 토큰을 ~/.zshrc에 설정")
print("   2. source ~/.zshrc로 적용")
print("   3. 이 스크립트 재실행으로 검증")
