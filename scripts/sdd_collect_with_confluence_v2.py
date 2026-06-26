#!/usr/bin/env python3
"""
/sdd-collect with Confluence Sync (v2)
JIRA 이슈 수집 + Confluence 콘텐츠 동기화 + REQID 기반 폴더 구조
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

# JIRA 설정
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "bye23mj@nsonesoft.com")
JIRA_TOKEN = os.getenv("JIRA_TOKEN", "")
JIRA_INSTANCE = "https://nsonesoft.atlassian.net"
PROJECT_KEY = "MZ2026"
BOARD_ID = "427"

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
    """Confluence 페이지 다운로드 (Content API 사용)"""
    try:
        auth = (JIRA_EMAIL, JIRA_TOKEN)

        # Confluence Content API 사용 (wiki/rest/api/content/)
        url = f"{JIRA_INSTANCE}/wiki/rest/api/content/{page_id}?expand=body.view,children.attachment"
        response = requests.get(
            url,
            auth=auth,
            headers={"Accept": "application/json"},
            timeout=30
        )

        if response.status_code == 401:
            print(f"  ⚠️ 인증 실패 (401): 토큰 확인 필요")
            return None

        if response.status_code == 404:
            print(f"  ⚠️ 페이지를 찾을 수 없음 (404)")
            return None

        if response.status_code != 200:
            print(f"  ⚠️ 페이지 조회 실패 ({response.status_code})")
            return None

        page_data = response.json()
        title = page_data.get("title", f"page_{page_id}")

        # HTML 콘텐츠 저장
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
        }

    except Exception as e:
        print(f"  ⚠️ 페이지 다운로드 실패: {e}")
        return None

def main():
    print("\n" + "="*70)
    print("📋 /sdd-collect with Confluence Sync (v2)")
    print("="*70)

    # 작업 디렉토리
    workspace = Path("/Users/ai/vscode/egov-demo/docs/00. confluence")
    workspace.mkdir(parents=True, exist_ok=True)

    run_id = f"REQ-MZ2026-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print(f"\n✓ 설정:")
    print(f"  Workspace: {workspace}")
    print(f"  Run ID: {run_id}")
    print(f"  JIRA Instance: {JIRA_INSTANCE}")
    print(f"  Project: {PROJECT_KEY}")
    print(f"  Account: {JIRA_EMAIL}")

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

        # 내부검토 상태만 필터링
        internal_review_issues = [
            issue for issue in all_issues
            if issue['fields']['status']['name'] == '내부검토'
        ]

        print(f"  발견: {len(all_issues)}개 이슈 중 {len(internal_review_issues)}개 (내부검토)")

    except Exception as e:
        print(f"  ✗ JIRA 조회 실패: {e}")
        sys.exit(1)

    # 수집 통계
    stats = {
        "run_id": run_id,
        "total_issues": len(internal_review_issues),
        "jira_attachments": 0,
        "confluence_pages": 0,
        "source_documents": [],
    }

    # 각 이슈 처리
    print(f"\n✓ Step 2: 문서 수집 (JIRA + Confluence)")

    for issue in internal_review_issues:
        key = issue['key']
        fields = issue['fields']
        description = fields.get('description', '')
        
        # REQID 추출 (customfield_10431)
        reqid = fields.get('customfield_10431', key)
        
        print(f"\n  📌 {key} ({reqid}): {fields.get('summary', '')[:50]}")

        # JIRA 첨부파일 처리
        attachments = fields.get('attachment', [])
        if attachments:
            print(f"     JIRA 첨부파일: {len(attachments)}개")
            for att in attachments:
                stats["source_documents"].append({
                    "type": "jira_attachment",
                    "issue": key,
                    "reqid": reqid,
                    "name": att.get('filename', ''),
                })
            stats["jira_attachments"] += len(attachments)

        # Confluence URL 추출
        confluence_urls = extract_confluence_urls(description)
        if confluence_urls:
            print(f"     Confluence: {len(confluence_urls)}개 링크 발견")

            for url in confluence_urls:
                page_id = extract_page_id(url)
                if page_id:
                    print(f"       → 페이지 ID: {page_id} 다운로드 중...")

                    # REQID 기반 폴더 생성
                    page_dir = workspace / key / reqid
                    result = download_confluence_page(page_id, page_dir)

                    if result:
                        print(f"         ✓ {result['title']} ({result['size']} bytes)")
                        print(f"         📁 폴더: {key}/{reqid}")
                        stats["source_documents"].append({
                            "type": "confluence_page",
                            "issue": key,
                            "reqid": reqid,
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
    }

    metadata_file = workspace / "source-metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # 결과 출력
    print(f"\n" + "="*70)
    print(f"✅ /sdd-collect 완료!")
    print(f"="*70)

    print(f"\n📊 수집 결과:")
    print(f"  이슈: {stats['total_issues']}개")
    print(f"  JIRA 첨부파일: {stats['jira_attachments']}개")
    print(f"  Confluence 페이지: {stats['confluence_pages']}개")
    print(f"  총 문서: {metadata['summary']['totalDocuments']}개")

    print(f"\n📁 저장 위치:")
    print(f"  Workspace: {workspace}")
    print(f"  메타데이터: {metadata_file}")
    print(f"  폴더 구조: issue_key/REQID/")

    if stats['confluence_pages'] > 0:
        print(f"\n✨ Confluence 콘텐츠:")
        for doc in stats['source_documents']:
            if doc['type'] == 'confluence_page':
                print(f"  - {doc['issue']}/{doc['reqid']}/{doc['title']}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
