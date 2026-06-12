#!/usr/bin/env python3
"""
Phase 2: 문서 정규화 (Normalization)
다운로드한 문서를 분석하고 구조화된 형식으로 정규화
"""

import os
import json
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def analyze_document(file_path: Path) -> Dict[str, Any]:
    """문서 분석 및 메타데이터 추출"""
    result = {
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_size": file_path.stat().st_size,
        "content_type": "markdown" if file_path.suffix == ".md" else "unknown",
        "extracted_metadata": {},
        "sections": [],
        "links": [],
        "tables": [],
    }

    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 제목 추출
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            result["extracted_metadata"]["title"] = title_match.group(1)
        
        # 섹션 추출 (H2, H3)
        sections = re.findall(r'^(#{2,3})\s+(.+)$', content, re.MULTILINE)
        for level, section_title in sections:
            result["sections"].append({
                "level": len(level),
                "title": section_title,
            })
        
        # 링크 추출
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        result["links"] = [{"text": text, "url": url} for text, url in links]
        
        # HTML 테이블 감지
        tables = re.findall(r'<table[^>]*>.*?</table>', content, re.DOTALL)
        result["tables"] = [{"count": len(tables), "note": "테이블 감지됨"}] if tables else []
        
        # 문서 요약
        lines = content.split('\n')
        result["stats"] = {
            "total_lines": len(lines),
            "total_words": len(content.split()),
            "has_code_blocks": bool(re.search(r'```', content)),
            "has_lists": bool(re.search(r'^\s*[-*+]\s', content, re.MULTILINE)),
            "has_tables": len(tables) > 0,
        }
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

def normalize_document_structure(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """문서 구조 정규화"""
    normalized = {
        "documentId": analysis["file_path"].replace("/", "_").replace(".", "_"),
        "title": analysis["extracted_metadata"].get("title", "Untitled"),
        "fileName": analysis["file_name"],
        "contentType": analysis["content_type"],
        "stats": analysis.get("stats", {}),
        "structure": {
            "sections": analysis.get("sections", []),
            "links": analysis.get("links", []),
            "tables": len(analysis.get("tables", [])),
        },
        "quality_score": calculate_quality_score(analysis),
        "missing_elements": identify_missing_elements(analysis),
    }
    
    return normalized

def calculate_quality_score(analysis: Dict[str, Any]) -> float:
    """문서 품질 점수 계산 (0-100)"""
    score = 50.0  # 기본 점수
    
    stats = analysis.get("stats", {})
    
    # 문서 크기에 따른 점수
    if stats.get("total_lines", 0) > 100:
        score += 20
    elif stats.get("total_lines", 0) > 50:
        score += 10
    
    # 구조에 따른 점수
    if len(analysis.get("sections", [])) > 3:
        score += 15
    elif len(analysis.get("sections", [])) > 0:
        score += 5
    
    # 링크에 따른 점수
    if len(analysis.get("links", [])) > 0:
        score += 5
    
    # 표에 따른 점수
    if analysis.get("tables"):
        score += 10
    
    return min(score, 100.0)

def identify_missing_elements(analysis: Dict[str, Any]) -> List[str]:
    """누락된 요소 식별"""
    missing = []
    
    if not analysis["extracted_metadata"].get("title"):
        missing.append("제목")
    
    if len(analysis.get("sections", [])) == 0:
        missing.append("섹션 구조")
    
    if analysis["stats"].get("total_lines", 0) < 20:
        missing.append("충분한 콘텐츠")
    
    if not analysis.get("links"):
        missing.append("참조 링크")
    
    return missing

def main():
    print("\n" + "="*70)
    print("📖 Phase 2: 문서 정규화 (Normalization)")
    print("="*70)
    
    # 작업 디렉토리
    workspace = Path("/Users/ai/vscode/egov-demo/docs/00. confluence")
    metadata_file = workspace / "source-metadata.json"
    
    if not metadata_file.exists():
        print(f"✗ source-metadata.json을 찾을 수 없습니다")
        sys.exit(1)
    
    # 수집된 문서 목록 로드
    with open(metadata_file) as f:
        source_metadata = json.load(f)
    
    print(f"\n✓ 수집된 문서: {len(source_metadata['sourceDocuments'])}개")
    
    # Step 1: 문서 분석
    print(f"\n✓ Step 1: 문서 분석")
    
    analyses = []
    for doc in source_metadata["sourceDocuments"]:
        if doc["type"] == "confluence_page":
            file_path = Path(doc["file"])
            if file_path.exists():
                print(f"  분석 중: {doc['title']}")
                analysis = analyze_document(file_path)
                analyses.append(analysis)
                
                print(f"    - 라인: {analysis['stats'].get('total_lines', 0)}")
                print(f"    - 섹션: {len(analysis['sections'])}")
                print(f"    - 링크: {len(analysis['links'])}")
                print(f"    - 표: {len(analysis.get('tables', []))}")
    
    # Step 2: 정규화
    print(f"\n✓ Step 2: 문서 정규화")
    
    normalized_docs = []
    for analysis in analyses:
        normalized = normalize_document_structure(analysis)
        normalized_docs.append(normalized)
        
        print(f"\n  📄 {normalized['title']}")
        print(f"     품질 점수: {normalized['quality_score']:.1f}/100")
        print(f"     섹션: {len(normalized['structure']['sections'])}개")
        if normalized["missing_elements"]:
            print(f"     누락 요소: {', '.join(normalized['missing_elements'])}")
    
    # Step 3: 정규화 결과 저장
    print(f"\n✓ Step 3: 정규화 결과 저장")
    
    normalization_output = {
        "runId": source_metadata["runId"],
        "phase": "2-normalize",
        "normalizedAt": datetime.now().isoformat(),
        "statistics": {
            "total_documents": len(normalized_docs),
            "average_quality_score": sum(d["quality_score"] for d in normalized_docs) / len(normalized_docs) if normalized_docs else 0,
        },
        "documents": normalized_docs,
    }
    
    output_file = workspace / "normalized-metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalization_output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ 저장: {output_file}")
    
    # 결과 요약
    print(f"\n" + "="*70)
    print(f"✅ 문서 정규화 완료!")
    print(f"="*70)
    
    print(f"\n📊 정규화 결과:")
    print(f"  처리 문서: {len(normalized_docs)}개")
    print(f"  평균 품질: {normalization_output['statistics']['average_quality_score']:.1f}/100")
    
    if normalized_docs:
        low_quality = [d for d in normalized_docs if d["quality_score"] < 60]
        if low_quality:
            print(f"\n⚠️ 품질 개선 필요 (< 60점):")
            for doc in low_quality:
                print(f"  - {doc['title']} ({doc['quality_score']:.1f}/100)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
