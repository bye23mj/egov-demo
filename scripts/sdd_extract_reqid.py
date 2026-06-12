#!/usr/bin/env python3
"""
REQID 추출 및 자동 생성 유틸리티
- 이슈 제목에서 패턴 추출
- Confluence 메타데이터에서 "산출물 ID" 추출
- 첨부파일명에서 추출
- 모두 실패시 자동 생성
"""

import re
from typing import Optional, Dict, Any
from pathlib import Path

class REQIDExtractor:
    """REQID 추출 및 생성"""
    
    # REQID 패턴 (우선순위 높은 순서)
    PATTERNS = [
        r'([A-Z]+-\d{3})',      # ERP-001, REQ-123
        r'([A-Z]+-\d{2})',      # ERP-01, REQ-23
        r'([A-Z]{2,}-\d+)',     # ERPPJT-1, REQ-999
        r'([A-Z]+-\d+)',        # 일반 형식
        r'(\d{3,})',            # 순번 (3자리 이상)
    ]
    
    @staticmethod
    def extract_from_title(title: str) -> Optional[str]:
        """제목에서 REQID 추출"""
        if not title or title.strip() in ['T', 'N/A', '']:
            return None
        
        for pattern in REQIDExtractor.PATTERNS:
            match = re.search(pattern, title)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def extract_from_confluence_content(content: str) -> Optional[str]:
        """Confluence 콘텐츠에서 "산출물 ID" 추출"""
        if not content:
            return None
        
        # HTML 테이블에서 "산출물 ID" 또는 "산출물ID" 찾기
        patterns = [
            r'산출물\s*ID[:\s]+([A-Z0-9\-]+)',
            r'산출물ID[:\s]+([A-Z0-9\-]+)',
            r'Artifact\s*ID[:\s]+([A-Z0-9\-]+)',
            r'Requirement\s*ID[:\s]+([A-Z0-9\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                reqid = match.group(1).strip()
                if reqid and len(reqid) > 1:
                    return reqid
        
        return None
    
    @staticmethod
    def extract_from_filename(filename: str) -> Optional[str]:
        """파일명에서 REQID 추출"""
        if not filename:
            return None
        
        # 파일명에서 첫 번째 패턴 찾기
        for pattern in REQIDExtractor.PATTERNS:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def generate_default(issue_key: str, project_key: str = "REQ") -> str:
        """기본값 생성"""
        # 형식: REQ-{PROJECT}-{ISSUE_NUMBER}
        # 예: REQ-MZ2026-1
        issue_num = re.search(r'\d+', issue_key)
        if issue_num:
            return f"{project_key}-{issue_num.group()}"
        return f"{project_key}-{issue_key}"
    
    @staticmethod
    def extract(
        issue_key: str,
        title: str = None,
        confluence_content: str = None,
        attachment_filename: str = None,
        project_key: str = "REQ"
    ) -> Dict[str, Any]:
        """
        종합 REQID 추출
        
        우선순위:
        1. 제목 (title)
        2. Confluence 메타데이터
        3. 첨부파일명
        4. 자동 생성
        """
        
        result = {
            "issue_key": issue_key,
            "reqid": None,
            "source": None,
            "alternatives": []
        }
        
        # 1. 제목에서 추출
        from_title = REQIDExtractor.extract_from_title(title)
        if from_title:
            result["reqid"] = from_title
            result["source"] = "TITLE"
            result["alternatives"].append({"source": "TITLE", "value": from_title})
            return result
        
        # 2. Confluence 메타데이터에서 추출
        from_confluence = REQIDExtractor.extract_from_confluence_content(confluence_content)
        if from_confluence:
            result["reqid"] = from_confluence
            result["source"] = "CONFLUENCE_METADATA"
            if from_title:
                result["alternatives"].append({"source": "TITLE", "value": from_title})
            return result
        
        # 3. 첨부파일명에서 추출
        from_filename = REQIDExtractor.extract_from_filename(attachment_filename)
        if from_filename:
            result["reqid"] = from_filename
            result["source"] = "ATTACHMENT_FILENAME"
            if from_title:
                result["alternatives"].append({"source": "TITLE", "value": from_title})
            if from_confluence:
                result["alternatives"].append({"source": "CONFLUENCE_METADATA", "value": from_confluence})
            return result
        
        # 4. 자동 생성
        generated = REQIDExtractor.generate_default(issue_key, project_key)
        result["reqid"] = generated
        result["source"] = "GENERATED"
        result["alternatives"] = [
            {"source": "TITLE", "value": from_title},
            {"source": "CONFLUENCE_METADATA", "value": from_confluence},
            {"source": "ATTACHMENT_FILENAME", "value": from_filename}
        ]
        result["alternatives"] = [a for a in result["alternatives"] if a["value"]]
        
        return result

def main():
    """테스트"""
    print("📋 REQID 추출 테스트\n")
    
    # 테스트 케이스
    test_cases = [
        {
            "issue_key": "MZ2026-1",
            "title": "ERP-01 요구사항확인",
            "confluence_content": "산출물 ID: ERP-001",
        },
        {
            "issue_key": "MZ2026-10",
            "title": "T",
            "confluence_content": None,
        },
        {
            "issue_key": "DEV-100",
            "title": "요구사항 정의",
            "confluence_content": "산출물 ID: REQ-2024-100",
        },
    ]
    
    for test in test_cases:
        print(f"이슈: {test['issue_key']}")
        print(f"  제목: {test.get('title', 'N/A')}")
        
        result = REQIDExtractor.extract(
            issue_key=test['issue_key'],
            title=test.get('title'),
            confluence_content=test.get('confluence_content'),
            attachment_filename=test.get('attachment_filename')
        )
        
        print(f"  추출 결과:")
        print(f"    REQID: {result['reqid']}")
        print(f"    출처: {result['source']}")
        if result['alternatives']:
            print(f"    대안:")
            for alt in result['alternatives']:
                print(f"      - {alt['source']}: {alt['value']}")
        print()

if __name__ == '__main__':
    main()
