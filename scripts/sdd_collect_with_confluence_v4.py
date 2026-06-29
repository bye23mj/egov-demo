#!/usr/bin/env python3
"""
/sdd-collect with Confluence Sync (v4)
JIRA 이슈 수집 + Confluence 콘텐츠 + 첨부파일 다운로드
"""
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
import json
import sys
import re
import requests
from datetime import datetime
from pathlib import Path

# REQID 추출 함수
def extract_reqid(issue_key: str, title: str = None, confluence_content: str = None) -> dict:
    """REQID 추출 및 생성"""
    patterns = [
        r'([A-Z]+-\d{3})',
        r'([A-Z]+-\d{2})',
        r'([A-Z]{2,}-\d+)',
        r'([A-Z]+-\d+)',
    ]
    
    if title and title.strip() not in ['T', 'N/A', '']:
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                return {"reqid": match.group(1), "source": "TITLE"}
    
    if confluence_content:
        confluence_patterns = [
            r'산출물\s*ID[:\s]+([A-Z0-9\-]+)',
            r'산출물ID[:\s]+([A-Z0-9\-]+)',
        ]
        for pattern in confluence_patterns:
            match = re.search(pattern, confluence_content)
            if match:
                reqid = match.group(1).strip()
                if reqid and len(reqid) > 1:
                    return {"reqid": reqid, "source": "CONFLUENCE_METADATA"}
    
    issue_num = re.search(r'\d+', issue_key)
    generated = f"REQ-{issue_num.group()}" if issue_num else f"REQ-{issue_key}"
    return {"reqid": generated, "source": "GENERATED"}

# JIRA 설정
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_TOKEN = os.getenv("JIRA_TOKEN", "")
JIRA_INSTANCE = "https://nsonesoft.atlassian.net"
PROJECT_KEY = "MZ2026"
BOARD_ID = "427"

# 지원 형식
SUPPORTED_FORMATS = [
    'pdf', 'docx', 'xlsx', 'pptx', 'hwpx',
    'doc', 'xls', 'ppt', 'hwp', 'txt',
    'xml', 'json', 'csv'
]

def is_supported_format(filename: str) -> bool:
    """지원 형식 확인"""
    ext = Path(filename).suffix.lower().lstrip('.')
    return ext in SUPPORTED_FORMATS

def download_attachment(attachment_id: str, filename: str, output_dir: Path) -> dict:
    """JIRA에서 첨부파일 다운로드"""
    try:
        auth = (JIRA_EMAIL, JIRA_TOKEN)
        
        # JIRA 첨부파일 다운로드 URL
        url = f"{JIRA_INSTANCE}/rest/api/2/attachment/{attachment_id}"
        
        response = requests.get(url, auth=auth, timeout=30, stream=True)
        
        if response.status_code != 200:
            return {"success": False, "error": f"HTTP {response.status_code}"}
        
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / filename
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size = file_path.stat().st_size
        
        return {
            "success": True,
            "filename": filename,
            "file_path": str(file_path),
            "size": file_size,
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_confluence_urls(text: str):
    """텍스트에서 Confluence URL 추출"""
    if not text:
        return []
    pattern = r'https://[^\s\]]+/wiki/(?:spaces/[^\s/]+/)?pages/\d+'
    matches = re.findall(pattern, text)
    return list(set(matches))

def extract_page_id(url: str):
    """URL에서 페이지 ID 추출"""
    match = re.search(r'/pages/(\d+)', url)
    return match.group(1) if match else None

def download_confluence_page(page_id: str, output_dir: Path):
    """Confluence 페이지 다운로드"""
    try:
        auth = (JIRA_EMAIL, JIRA_TOKEN)
        url = f"{JIRA_INSTANCE}/wiki/rest/api/content/{page_id}?expand=body.view"
        response = requests.get(url, auth=auth, headers={"Accept": "application/json"}, timeout=30)

        if response.status_code != 200:
            return None

        page_data = response.json()
        title = page_data.get("title", f"page_{page_id}")
        html = page_data.get("body", {}).get("view", {}).get("value", "")
        markdown = f"# {title}\n\n{html}"

        output_dir.mkdir(parents=True, exist_ok=True)
        md_file = output_dir / f"{title}.md"
        md_file.write_text(markdown, encoding='utf-8')

        return {
            "page_id": page_id,
            "title": title,
            "file": str(md_file),
            "size": len(markdown),
            "content": markdown,
        }

    except Exception as e:
        return None

def main():
    print("\n" + "="*70)
    print("📋 /sdd-collect with Confluence Sync (v4)")
    print("="*70)

    workspace = Path("/Users/ai/vscode/egov-demo/docs/00. confluence")
    workspace.mkdir(parents=True, exist_ok=True)

    run_id = f"REQ-MZ2026-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print(f"\n✓ 설정:")
    print(f"  Workspace: {workspace}")
    print(f"  Run ID: {run_id}")

    # JIRA Board에서 이슈 조회
    print(f"\n✓ Step 1: JIRA 이슈 조회")

    auth = (JIRA_EMAIL, JIRA_TOKEN)
    board_url = f"{JIRA_INSTANCE}/rest/agile/1.0/board/{BOARD_ID}/issue?maxResults=50"

    try:
        response = requests.get(board_url, auth=auth, timeout=30)
        if response.status_code != 200:
            print(f"  ✗ JIRA 조회 실패 ({response.status_code})")
            sys.exit(1)

        board_data = response.json()
        all_issues = board_data.get('issues', [])
        internal_review_issues = [
            issue for issue in all_issues
            if issue['fields']['status']['name'] == '내부검토'
        ]

        print(f"  발견: {len(all_issues)}개 이슈 중 {len(internal_review_issues)}개 (내부검토)")

    except Exception as e:
        print(f"  ✗ JIRA 조회 실패: {e}")
        sys.exit(1)

    # 문서 수집
    print(f"\n✓ Step 2: 문서 수집 + 첨부파일 다운로드")

    stats = {
        "run_id": run_id,
        "total_issues": len(internal_review_issues),
        "jira_attachments": 0,
        "confluence_pages": 0,
        "source_documents": [],
    }

    for issue in internal_review_issues:
        key = issue['key']
        fields = issue['fields']
        title = fields.get('summary', '')
        description = fields.get('description', '')
        
        # REQID 추출
        reqid_field = fields.get('customfield_10431')
        reqid_result = {"reqid": reqid_field, "source": "JIRA_FIELD"} if reqid_field else extract_reqid(key, title)
        reqid = reqid_result["reqid"]
        source = reqid_result["source"]
        
        print(f"\n  📌 {key} → {reqid} ({source})")
        print(f"     제목: {title[:50]}")

        # JIRA 첨부파일 처리
        attachments = fields.get('attachment', [])
        if attachments:
            print(f"     JIRA 첨부파일: {len(attachments)}개")
            for att in attachments:
                filename = att.get('filename', '')
                att_id = att.get('id', '')
                size = att.get('size', 0)
                
                if is_supported_format(filename):
                    print(f"       → {filename} 다운로드 중...")
                    
                    att_dir = workspace / key / reqid
                    result = download_attachment(att_id, filename, att_dir)
                    
                    if result.get('success'):
                        print(f"         ✓ {filename} ({result['size']} bytes)")
                        stats["source_documents"].append({
                            "type": "jira_attachment",
                            "issue": key,
                            "reqid": reqid,
                            "reqid_source": source,
                            "filename": filename,
                            "file_path": result['file_path'],
                            "size": result['size'],
                        })
                        stats["jira_attachments"] += 1
                    else:
                        print(f"         ✗ 다운로드 실패: {result.get('error')}")
                else:
                    print(f"       ⏭️ {filename} (미지원 형식)")

        # Confluence URL 처리
        confluence_urls = extract_confluence_urls(description)
        if confluence_urls:
            print(f"     Confluence: {len(confluence_urls)}개 링크 발견")

            for url in confluence_urls:
                page_id = extract_page_id(url)
                if page_id:
                    print(f"       → 페이지 ID: {page_id} 다운로드 중...")

                    page_dir = workspace / key / reqid
                    result = download_confluence_page(page_id, page_dir)

                    if result:
                        print(f"         ✓ {result['title']} ({result['size']} bytes)")
                        stats["source_documents"].append({
                            "type": "confluence_page",
                            "issue": key,
                            "reqid": reqid,
                            "reqid_source": source,
                            "page_id": page_id,
                            "title": result['title'],
                            "file": result['file'],
                        })
                        stats["confluence_pages"] += 1

    # 메타데이터 저장
    print(f"\n✓ Step 3: 메타데이터 저장")

    metadata = {
        "runId": run_id,
        "projectKey": PROJECT_KEY,
        "targetStatus": "내부검토",
        "phase": "1-collect",
        "startedAt": datetime.now().isoformat(),
        "summary": {
            "totalIssues": stats["total_issues"],
            "jiraAttachments": stats["jira_attachments"],
            "confluencePages": stats["confluence_pages"],
            "totalDocuments": stats["jira_attachments"] + stats["confluence_pages"],
        },
        "sourceDocuments": stats["source_documents"],
        "folderStructure": "issue_key/REQID/",
        "supportedFormats": SUPPORTED_FORMATS,
    }

    metadata_file = workspace / "source-metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 결과 출력
    print(f"\n" + "="*70)
    print(f"✅ /sdd-collect (v4) 완료!")
    print(f"="*70)

    print(f"\n📊 수집 결과:")
    print(f"  이슈: {stats['total_issues']}개")
    print(f"  JIRA 첨부파일: {stats['jira_attachments']}개")
    print(f"  Confluence 페이지: {stats['confluence_pages']}개")
    print(f"  총 문서: {metadata['summary']['totalDocuments']}개")

    print(f"\n📁 지원 형식: {', '.join(SUPPORTED_FORMATS)}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
