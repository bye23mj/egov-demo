"""Confluence 동기화 기능 추가 (document_collector.py에 추가할 메서드들)"""

import re
import requests
from typing import List, Optional, Dict, Any
from pathlib import Path

def extract_confluence_urls(text: str) -> List[str]:
    """JIRA 이슈 설명에서 Confluence URL 추출"""
    if not text:
        return []
    
    # Confluence URL 패턴
    # https://xxx.atlassian.net/wiki/spaces/SPACE/pages/123456
    # https://xxx.atlassian.net/wiki/pages/123456
    pattern = r'https://[^\s\]]+/wiki/(?:spaces/[^\s/]+/)?pages/\d+'
    matches = re.findall(pattern, text)
    
    # 중복 제거
    return list(set(matches))

def extract_page_id_from_url(url: str) -> Optional[str]:
    """Confluence URL에서 pageId 추출"""
    match = re.search(r'/pages/(\d+)', url)
    return match.group(1) if match else None

def collect_confluence_content(
    page_id: str,
    confluence_api,
    workspace_dir: Path,
    issue_key: str
) -> Dict[str, Any]:
    """Confluence 페이지 콘텐츠 및 첨부파일 수집"""
    result = {
        "page_id": page_id,
        "success": False,
        "downloaded_items": [],
        "error": None,
    }
    
    try:
        # 페이지 정보 조회
        page_data = confluence_api.get_page_content(page_id)
        if not page_data:
            result["error"] = "페이지 조회 실패"
            return result
        
        title = page_data.get("title", "untitled")
        
        # 페이지 본문 저장
        try:
            html = page_data.get("body", {}).get("view", {}).get("value", "")
            markdown = f"# {title}\n\n{html}"
            
            target_dir = workspace_dir / "input" / issue_key
            target_dir.mkdir(parents=True, exist_ok=True)
            
            md_file = target_dir / f"{title}.md"
            md_file.write_text(markdown, encoding='utf-8')
            
            result["downloaded_items"].append({
                "type": "page",
                "name": f"{title}.md",
                "path": str(md_file),
            })
        except Exception as e:
            result["error"] = f"페이지 본문 저장 실패: {e}"
            return result
        
        # 첨부파일 수집
        try:
            attachments = confluence_api.get_attachments(page_id)
            
            for att in attachments:
                att_filename = att.get("title", "")
                att_id = att.get("id", "")
                
                try:
                    content = confluence_api.download_attachment(att_id, att_filename)
                    if content:
                        att_file = target_dir / att_filename
                        att_file.write_bytes(content)
                        
                        result["downloaded_items"].append({
                            "type": "attachment",
                            "name": att_filename,
                            "path": str(att_file),
                        })
                except Exception as e:
                    print(f"⚠️  첨부파일 {att_filename} 다운로드 실패: {e}")
        
        except Exception as e:
            print(f"⚠️  첨부파일 조회 실패: {e}")
        
        result["success"] = True
        return result
        
    except Exception as e:
        result["error"] = str(e)
        return result

