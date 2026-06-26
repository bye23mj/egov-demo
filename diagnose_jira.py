#!/usr/bin/env python3
"""JIRA 401 오류 진단"""
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
sys.path.insert(0, '/Users/ai/vscode/egov-demo')

print("🔍 JIRA 401 오류 진단\n")
print("="*70)

# 1. 환경변수 확인
print("\n✓ Step 1: 환경변수 확인")
print("-"*70)

jira_email = os.getenv('JIRA_EMAIL')
jira_token = os.getenv('JIRA_TOKEN')

if jira_email:
    print(f"  Email: {jira_email}")
else:
    print(f"  Email: ❌ 설정 안됨")

if jira_token:
    print(f"  Token: {jira_token[:30]}... (길이: {len(jira_token)})")
    
    # 토큰 기본 검증
    if len(jira_token) >= 150:
        print(f"  형식: ✓ 유효 (Atlassian Cloud 토큰)")
    else:
        print(f"  형식: ❌ 의심스러움 (너무 짧음)")
else:
    print(f"  Token: ❌ 설정 안됨")

# 2. JIRA 설정 파일 확인
print("\n✓ Step 2: JIRA 설정 파일 확인")
print("-"*70)

from pathlib import Path
config_file = Path.home() / ".jira-sync" / "config.json"
env_file = Path.home() / ".jira-sync" / ".env"

if config_file.exists():
    import json
    with open(config_file) as f:
        config = json.load(f)
    print(f"  config.json: ✓ 존재")
    print(f"    - JIRA URL: {config.get('jira_url')}")
    print(f"    - 계정: {config.get('account')}")
    print(f"    - 프로젝트: {config.get('project_key')}")
else:
    print(f"  config.json: ❌ 없음")

if env_file.exists():
    print(f"  .env: ✓ 존재 (권한: {oct(os.stat(env_file).st_mode)[-3:]})")
else:
    print(f"  .env: ❌ 없음")

# 3. 토큰 유효성 기본 검사
print("\n✓ Step 3: 토큰 유효성 검사")
print("-"*70)

if jira_token:
    checks = []
    
    # ATATT로 시작하는가?
    if jira_token.startswith('ATATT'):
        checks.append(("ATATT 시작", "✓"))
    else:
        checks.append(("ATATT 시작", "❌"))
    
    # 길이 확인
    if 180 < len(jira_token) < 210:
        checks.append(("토큰 길이", "✓"))
    else:
        checks.append(("토큰 길이", "❌"))
    
    # 특수문자 포함
    if '=' in jira_token and '_' in jira_token:
        checks.append(("특수문자", "✓"))
    else:
        checks.append(("특수문자", "❌"))
    
    for check, result in checks:
        print(f"  {check}: {result}")

# 4. 연결 시도
print("\n✓ Step 4: JIRA 연결 테스트")
print("-"*70)

if jira_email and jira_token:
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        from scripts.confluence.jira_api import JiraConfig
        config = JiraConfig()
        jira_url = config.get('jira_url')
        
        # 직접 HTTP 요청
        url = f"{jira_url}/rest/api/3/myself"
        auth = HTTPBasicAuth(jira_email, jira_token)
        
        print(f"  URL: {url}")
        print(f"  Auth: Basic {jira_email}:***")
        
        response = requests.get(url, auth=auth, timeout=5)
        
        print(f"  상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ 연결 성공!")
            print(f"    이름: {data.get('displayName')}")
            print(f"    계정: {data.get('emailAddress')}")
        elif response.status_code == 401:
            print(f"  ❌ 401 Unauthorized")
            print(f"    원인 분석:")
            print(f"      1. 토큰이 유효하지 않음")
            print(f"      2. 토큰이 만료됨")
            print(f"      3. 토큰이 잘못된 인스턴스용")
            print(f"      4. 계정이 비활성화됨")
        else:
            print(f"  ❌ 연결 실패 ({response.status_code})")
            
    except Exception as e:
        print(f"  ❌ 오류: {e}")

print("\n" + "="*70)

