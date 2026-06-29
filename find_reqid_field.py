#!/usr/bin/env python3
"""JIRA REQID 필드 찾기"""
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

import requests
from requests.auth import HTTPBasicAuth

print("🔍 JIRA MZ2026 프로젝트 필드 조회\n")

jira_url = "https://nsonesoft.atlassian.net"
import os
email = os.getenv("JIRA_EMAIL", "")
token = "ATATT3xFfGF0KmZp0WmP5iRFdFPXoQj4UGHz4m3wF5OAGy67bmWrkfYSRUtCTTPzQwPDVARUm20PMN4k6aKjBUXC_Tks7NdbiN1rjAFp4BJ3KIsOgf4KqLOzmAbCLl3PIHm8o4dJTqzs9EsVERGizts4GFDf_kpNbj5pSnnnOAtQeWj8Fhi14Hs=5E98863D"
project_key = "MZ2026"

auth = HTTPBasicAuth(email, token)

print("="*70)
print("방법 1: 프로젝트 이슈 조회로 필드 확인\n")

try:
    # 프로젝트의 이슈를 하나 조회하면 필드 정보 포함
    url = f"{jira_url}/rest/api/3/issues"
    params = {
        'jql': f'project = {project_key}',
        'maxResults': 1,
        'expand': 'changelog'
    }
    
    response = requests.get(url, auth=auth, params=params, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('issues'):
            print(f"✅ 프로젝트에서 이슈 발견\n")
            
            # Editmeta에서 필드 정보 조회
            url2 = f"{jira_url}/rest/api/3/issues/{data['issues'][0]['key']}/editmeta"
            response2 = requests.get(url2, auth=auth, timeout=5)
            
            if response2.status_code == 200:
                editmeta = response2.json()
                fields = editmeta.get('fields', {})
                
                print("프로젝트 편집 가능 필드:\n")
                
                reqid_found = False
                for field_key, field_info in fields.items():
                    name = field_info.get('name', '')
                    if 'REQID' in name or 'REQ ID' in name or 'REQ-ID' in name:
                        print(f"✅ REQID 필드 발견!")
                        print(f"  필드ID: {field_key}")
                        print(f"  필드명: {name}")
                        print(f"  타입: {field_info.get('schema', {}).get('type')}")
                        reqid_found = True
                
                if not reqid_found:
                    print("주요 필드 목록:\n")
                    for field_key, field_info in list(fields.items())[:15]:
                        name = field_info.get('name')
                        print(f"  {field_key:20} → {name}")
        else:
            print("⚠️ 프로젝트에 이슈가 없습니다")
    else:
        print(f"❌ 이슈 조회 실패 ({response.status_code})")
        
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n" + "="*70)
print("\n💡 REQID 필드ID를 찾은 후:")
print("   다음 명령으로 알려주세요:")
print("   예: customfield_10024")

