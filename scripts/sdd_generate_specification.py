#!/usr/bin/env python3
"""
Phase 3: 스펙 생성 (Specification)
정규화된 문서를 기반으로 구조화된 요구사항 스펙 생성
"""

import os
import json
import sys
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def extract_requirements_from_document(file_path: Path) -> List[Dict[str, Any]]:
    """문서에서 요구사항 추출"""
    requirements = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # HTML 태그 제거
        content_clean = re.sub(r'<[^>]+>', '', content)
        
        # 메타 정보 테이블에서 요구사항 ID 추출
        req_id_match = re.search(r'산출물\s*ID[:\s]+([A-Z0-9\-]+)', content_clean)
        req_id = req_id_match.group(1) if req_id_match else "REQ-001"
        
        # 제목 추출
        title_match = re.search(r'#\s+(.+)', content_clean)
        title = title_match.group(1) if title_match else "Unnamed"
        
        # 주요 요구사항 항목 추출
        if "기능" in content_clean or "기능" in title.lower():
            requirements.append({
                "req_id": f"{req_id}-FUNC-001",
                "type": "FUNCTIONAL",
                "category": "기능 요구사항",
                "description": "기능 정의 문서 작성",
                "priority": "HIGH",
                "status": "DRAFT",
            })
        
        if "보안" in content_clean:
            requirements.append({
                "req_id": f"{req_id}-SEC-001",
                "type": "SECURITY",
                "category": "보안 요구사항",
                "description": "보안 요구사항 정의",
                "priority": "HIGH",
                "status": "DRAFT",
            })
        
        if "연계" in content_clean:
            requirements.append({
                "req_id": f"{req_id}-INT-001",
                "type": "INTEGRATION",
                "category": "연계 요구사항",
                "description": "외부 시스템 연계 요구사항",
                "priority": "MEDIUM",
                "status": "DRAFT",
            })
        
        # 기본 요구사항 (항상 추가)
        if not requirements:
            requirements.append({
                "req_id": f"{req_id}-001",
                "type": "FUNCTIONAL",
                "category": "일반 요구사항",
                "description": f"{title} - 요구사항 정의",
                "priority": "MEDIUM",
                "status": "DRAFT",
            })
        
    except Exception as e:
        print(f"⚠️ 요구사항 추출 오류: {e}")
    
    return requirements

def generate_specification(source_doc: Dict[str, Any], normalized_doc: Dict[str, Any]) -> Dict[str, Any]:
    """스펙 생성"""
    file_path = Path(source_doc["file"])
    requirements = extract_requirements_from_document(file_path)
    
    spec = {
        "specId": f"SPEC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "sourceDocument": {
            "issue": source_doc.get("issue"),
            "title": source_doc.get("title"),
            "page_id": source_doc.get("page_id"),
        },
        "documentQuality": normalized_doc.get("quality_score", 0),
        "generatedAt": datetime.now().isoformat(),
        "requirements": requirements,
        "statistics": {
            "total_requirements": len(requirements),
            "by_type": {},
            "by_priority": {},
        },
        "next_steps": [],
    }
    
    # 통계 계산
    for req in requirements:
        req_type = req["type"]
        priority = req["priority"]
        
        spec["statistics"]["by_type"][req_type] = spec["statistics"]["by_type"].get(req_type, 0) + 1
        spec["statistics"]["by_priority"][priority] = spec["statistics"]["by_priority"].get(priority, 0) + 1
    
    # 다음 단계 제안
    if normalized_doc.get("quality_score", 0) < 70:
        spec["next_steps"].append("문서 품질 개선 (보다 상세한 섹션 구조화)")
    
    if len(requirements) < 3:
        spec["next_steps"].append("추가 요구사항 분석 및 추출")
    
    spec["next_steps"].extend([
        "요구사항 검토 및 검증 (Peer Review)",
        "요구사항 추적성 매트릭스 생성",
        "설계 단계로 이동",
    ])
    
    return spec

def main():
    print("\n" + "="*70)
    print("📋 Phase 3: 스펙 생성 (Specification)")
    print("="*70)
    
    # 작업 디렉토리
    workspace = Path("/Users/ai/vscode/egov-demo/docs/00. confluence")
    
    source_metadata_file = workspace / "source-metadata.json"
    normalized_metadata_file = workspace / "normalized-metadata.json"
    
    if not source_metadata_file.exists() or not normalized_metadata_file.exists():
        print(f"✗ 메타데이터 파일을 찾을 수 없습니다")
        sys.exit(1)
    
    # 메타데이터 로드
    with open(source_metadata_file) as f:
        source_metadata = json.load(f)
    
    with open(normalized_metadata_file) as f:
        normalized_metadata = json.load(f)
    
    # 문서별 정규화 정보 매핑
    normalized_by_title = {d["title"]: d for d in normalized_metadata["documents"]}
    
    print(f"\n✓ Step 1: 요구사항 분석")
    
    specifications = []
    for source_doc in source_metadata["sourceDocuments"]:
        if source_doc["type"] == "confluence_page":
            title = source_doc.get("title")
            normalized_doc = normalized_by_title.get(title, {})
            
            print(f"\n  분석 중: {title}")
            spec = generate_specification(source_doc, normalized_doc)
            specifications.append(spec)
            
            print(f"    - 요구사항: {spec['statistics']['total_requirements']}개")
            print(f"    - 유형: {dict(spec['statistics']['by_type'])}")
            print(f"    - 우선순위: {dict(spec['statistics']['by_priority'])}")
    
    print(f"\n✓ Step 2: 스펙 생성")
    
    spec_output = {
        "runId": source_metadata["runId"],
        "phase": "3-specification",
        "generatedAt": datetime.now().isoformat(),
        "statistics": {
            "total_specifications": len(specifications),
            "total_requirements": sum(len(s["requirements"]) for s in specifications),
        },
        "specifications": specifications,
    }
    
    # 스펙 저장
    spec_file = workspace / "specification.json"
    with open(spec_file, 'w', encoding='utf-8') as f:
        json.dump(spec_output, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ 저장: {spec_file}")
    
    # 마크다운 형식 스펙도 생성
    print(f"\n✓ Step 3: 마크다운 스펙 생성")
    
    for spec in specifications:
        spec_md = f"""# {spec['sourceDocument']['title']}

## 스펙 정보
- Spec ID: `{spec['specId']}`
- 소스: {spec['sourceDocument']['issue']}
- 생성일: {spec['generatedAt']}
- 문서 품질: {spec['documentQuality']:.1f}/100

## 요구사항 요약
- 총 요구사항: {spec['statistics']['total_requirements']}개
- 유형 분포: {dict(spec['statistics']['by_type'])}
- 우선순위: {dict(spec['statistics']['by_priority'])}

## 요구사항 목록

"""
        
        for req in spec['requirements']:
            spec_md += f"""### {req['req_id']}: {req['description']}
- **유형**: {req['type']}
- **카테고리**: {req['category']}
- **우선순위**: {req['priority']}
- **상태**: {req['status']}

"""
        
        spec_md += """## 다음 단계
"""
        for i, step in enumerate(spec.get('next_steps', []), 1):
            spec_md += f"- [ ] {step}\n"
        
        spec_md_file = workspace / f"SPEC-{spec['sourceDocument']['issue']}.md"
        spec_md_file.write_text(spec_md, encoding='utf-8')
        print(f"  ✓ {spec_md_file.name}")
    
    # 결과 요약
    print(f"\n" + "="*70)
    print(f"✅ 스펙 생성 완료!")
    print(f"="*70)
    
    print(f"\n📊 생성 결과:")
    print(f"  스펙: {len(specifications)}개")
    print(f"  총 요구사항: {spec_output['statistics']['total_requirements']}개")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
