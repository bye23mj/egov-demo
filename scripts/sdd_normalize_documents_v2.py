#!/usr/bin/env python3
"""
Phase 2: 문서 정규화 (Normalization) - v2
HTML 파싱 및 메타데이터 추출로 문서 품질 개선
"""

import os
import json
import sys
import re
import html2text
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ BeautifulSoup4가 필요합니다. 설치해주세요:")
    print("   pip install beautifulsoup4")
    sys.exit(1)


def convert_html_to_markdown(html_content: str) -> str:
    """HTML → Markdown 변환 (BeautifulSoup 사용)"""
    if not html_content or not html_content.strip():
        return ""

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # html2text로 변환
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.body_width = 0

        markdown = h.handle(str(soup))
        return markdown.strip()
    except Exception as e:
        print(f"    ⚠️  HTML 변환 실패: {e}")
        return html_content


def extract_html_structure(html_content: str) -> Dict[str, Any]:
    """HTML에서 구조 정보 추출"""
    structure = {
        "headings": [],
        "tables": 0,
        "lists": 0,
        "code_blocks": 0,
        "images": 0,
        "links": 0,
    }

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # 제목 추출
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            structure["headings"].extend([
                {"level": i, "text": h.get_text().strip()}
                for h in headings
            ])

        # 표, 리스트, 코드블록, 이미지, 링크 개수
        structure["tables"] = len(soup.find_all('table'))
        structure["lists"] = len(soup.find_all(['ul', 'ol']))
        structure["code_blocks"] = len(soup.find_all(['code', 'pre']))
        structure["images"] = len(soup.find_all('img'))
        structure["links"] = len(soup.find_all('a'))

    except Exception:
        pass

    return structure


def extract_metadata_fields(content: str) -> Dict[str, Optional[str]]:
    """
    문서 내에서 메타데이터 필드 추출
    "필드명: 값" 형식의 정보를 찾음
    """
    metadata = {}

    patterns = {
        "산출물ID": r"산출물\s*ID\s*[:\:]\s*([^\n]+)",
        "버전": r"버전\s*[:\:]\s*([^\n]+)",
        "담당자": r"담당자\s*[:\:]\s*([^\n]+)",
        "상태": r"상태\s*[:\:]\s*([^\n]+)",
        "프로젝트": r"프로젝트\s*[:\:]\s*([^\n]+)",
        "작성일": r"작성일\s*[:\:]\s*([^\n]+)",
    }

    for field_name, pattern in patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        metadata[field_name] = match.group(1).strip() if match else None

    return {k: v for k, v in metadata.items() if v}


def analyze_document(file_path: Path) -> Dict[str, Any]:
    """문서 분석 및 메타데이터 추출"""
    result = {
        "file_path": str(file_path),
        "file_name": file_path.name,
        "file_size": file_path.stat().st_size,
        "content_type": "markdown" if file_path.suffix == ".md" else "unknown",
        "extracted_metadata": {},
        "document_metadata": {},
        "sections": [],
        "links": [],
        "tables": [],
        "html_structure": {},
        "markdown_content": None,
    }

    try:
        content = file_path.read_text(encoding='utf-8')

        # 원본이 HTML인 경우 Markdown으로 변환
        if '<html>' in content.lower() or '<table' in content.lower():
            markdown_content = convert_html_to_markdown(content)
            result["markdown_content"] = markdown_content
            result["html_structure"] = extract_html_structure(content)
            # 메타데이터는 원본 HTML에서 추출
            analysis_content = content
        else:
            markdown_content = content
            result["markdown_content"] = markdown_content
            analysis_content = content

        # 제목 추출
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        if title_match:
            result["extracted_metadata"]["title"] = title_match.group(1)

        # 섹션 추출 (H2, H3)
        sections = re.findall(r'^(#{2,3})\s+(.+)$', markdown_content, re.MULTILINE)
        for level, section_title in sections:
            result["sections"].append({
                "level": len(level),
                "title": section_title,
            })

        # 링크 추출
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
        result["links"] = [{"text": text, "url": url} for text, url in links]

        # 표 감지 (Markdown 형식)
        markdown_tables = re.findall(r'\|.+\|', markdown_content)
        result["tables"] = [{"count": len(markdown_tables), "note": "마크다운 표"}] if markdown_tables else []

        # 메타필드 추출
        result["document_metadata"] = extract_metadata_fields(analysis_content)

        # 통계 계산
        lines = markdown_content.split('\n')
        result["stats"] = {
            "total_lines": len(lines),
            "total_words": len(markdown_content.split()),
            "has_code_blocks": bool(re.search(r'```', markdown_content)),
            "has_lists": bool(re.search(r'^\s*[-*+]\s', markdown_content, re.MULTILINE)),
            "has_tables": len(markdown_tables) > 0 or len(result.get("html_structure", {}).get("tables", [])) > 0,
            "has_images": result.get("html_structure", {}).get("images", 0) > 0,
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
            "html_elements": analysis.get("html_structure", {}),
        },
        "metadata": analysis.get("document_metadata", {}),
        "quality_score": calculate_quality_score_v2(analysis),
        "missing_elements": identify_missing_elements(analysis),
        "markdown_preview": analysis.get("markdown_content", "")[:500] if analysis.get("markdown_content") else None,
    }

    return normalized


def calculate_quality_score_v2(analysis: Dict[str, Any]) -> float:
    """향상된 품질 점수 계산 (0-100)"""
    score = 50.0

    stats = analysis.get("stats", {})

    # 1. 문서 크기
    lines = stats.get("total_lines", 0)
    if lines > 100:
        score += 20
    elif lines > 50:
        score += 10

    # 2. 섹션 구조 (개선: 더 높은 점수)
    sections_count = len(analysis.get("sections", []))
    if sections_count >= 5:
        score += 20
    elif sections_count >= 3:
        score += 15
    elif sections_count > 0:
        score += 5

    # 3. 표 (HTML + Markdown 모두 감지)
    has_tables = (
        len(analysis.get("tables", [])) > 0 or
        analysis.get("html_structure", {}).get("tables", 0) > 0
    )
    if has_tables:
        score += 10

    # 4. 링크
    if len(analysis.get("links", [])) > 0:
        score += 5

    # 🆕 5. 메타데이터 완성도
    metadata = analysis.get("document_metadata", {})
    if metadata:
        metadata_count = len(metadata)
        metadata_score = min(metadata_count * 2.5, 15)  # 최대 15점
        score += metadata_score

    # 🆕 6. 가독성 (코드블록, 리스트, 이미지)
    readability_score = 0
    if stats.get("has_code_blocks"):
        readability_score += 3
    if stats.get("has_lists"):
        readability_score += 3
    if stats.get("has_images"):
        readability_score += 4
    score += readability_score  # 최대 10점

    # 🆕 7. HTML 요소 풍부성
    html_struct = analysis.get("html_structure", {})
    if html_struct.get("tables", 0) > 1:
        score += 5
    if html_struct.get("images", 0) > 0:
        score += 3

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

    if not analysis.get("document_metadata"):
        missing.append("메타데이터 (산출물ID, 버전 등)")

    return missing


def main():
    print("\n" + "="*70)
    print("📖 Phase 2: 문서 정규화 v2 (HTML 파싱 + 메타데이터 추출)")
    print("="*70)

    # 작업 디렉토리 (환경변수 또는 기본값)
    workspace_path = os.getenv("SDD_WORKSPACE")
    if not workspace_path:
        # 기본값: 스크립트 위치 기반 상대 경로
        workspace_path = Path(__file__).parent.parent / "docs" / "00. confluence"

    workspace = Path(workspace_path)
    if not workspace.exists():
        print(f"✗ Workspace 디렉토리가 없습니다: {workspace}")
        print(f"   환경변수 설정: export SDD_WORKSPACE=/path/to/workspace")
        sys.exit(1)

    metadata_file = workspace / "source-metadata.json"

    if not metadata_file.exists():
        print(f"✗ source-metadata.json을 찾을 수 없습니다")
        sys.exit(1)

    # 수집된 문서 목록 로드
    with open(metadata_file) as f:
        source_metadata = json.load(f)

    print(f"\n✓ 수집된 문서: {len(source_metadata['sourceDocuments'])}개")

    # Step 1: 문서 분석
    print(f"\n✓ Step 1: 문서 분석 (HTML 파싱)")

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
                print(f"    - HTML 구조: 표 {analysis['html_structure'].get('tables', 0)}개, 제목 {len(analysis['html_structure'].get('headings', []))}개")
                print(f"    - 메타데이터: {len(analysis.get('document_metadata', {}))}개 필드")

    # Step 2: 정규화
    print(f"\n✓ Step 2: 문서 정규화")

    normalized_docs = []
    for analysis in analyses:
        normalized = normalize_document_structure(analysis)
        normalized_docs.append(normalized)

        print(f"\n  📄 {normalized['title']}")
        print(f"     품질 점수: {normalized['quality_score']:.1f}/100", end="")

        # 점수 개선 표시
        if normalized['quality_score'] >= 80:
            print(" ✅ (우수)")
        elif normalized['quality_score'] >= 70:
            print(" 👍 (양호)")
        elif normalized['quality_score'] >= 60:
            print(" 👌 (보통)")
        else:
            print(" ⚠️  (개선필요)")

        print(f"     섹션: {len(normalized['structure']['sections'])}개")
        if normalized['metadata']:
            print(f"     메타: {', '.join(normalized['metadata'].keys())}")
        if normalized["missing_elements"]:
            print(f"     누락: {', '.join(normalized['missing_elements'])}")

    # Step 3: 정규화 결과 저장
    print(f"\n✓ Step 3: 정규화 결과 저장")

    normalization_output = {
        "runId": source_metadata["runId"],
        "phase": "2-normalize",
        "version": "2.0",
        "improvementNotes": "HTML 파싱, 메타데이터 추출, 가독성 분석",
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

    # Step 4: Markdown 파일 업데이트 (백업 포함)
    print(f"\n✓ Step 4: Markdown 파일 업데이트 (백업)")

    backup_dir = workspace / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    update_count = 0
    for analysis in analyses:
        if analysis.get("markdown_content"):
            file_path = Path(analysis["file_path"])
            if not file_path.exists():
                print(f"  ⚠️  파일을 찾을 수 없음: {file_path.name}")
                continue

            # 1. 원본 파일 백업
            backup_file = backup_dir / f"{file_path.name}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            try:
                import shutil
                shutil.copy2(file_path, backup_file)
            except OSError as e:
                print(f"  ✗ 백업 실패: {file_path.name} - {e}")
                continue

            # 2. 임시 파일에 쓰기
            temp_file = file_path.with_suffix('.md.tmp')
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(analysis["markdown_content"])
            except OSError as e:
                print(f"  ✗ 임시 파일 쓰기 실패: {temp_file.name} - {e}")
                continue

            # 3. 임시 파일을 원본으로 이동
            try:
                temp_file.replace(file_path)
                update_count += 1
                print(f"  ✓ 업데이트: {file_path.name} (백업: {backup_file.name})")
            except OSError as e:
                print(f"  ✗ 파일 이동 실패: {file_path.name} - {e}")
                # 실패한 경우 임시 파일 정리
                if temp_file.exists():
                    temp_file.unlink()

    print(f"  총 업데이트: {update_count}개 파일")

    # 결과 요약
    print(f"\n" + "="*70)
    print(f"✅ 문서 정규화 v2 완료!")
    print(f"="*70)

    print(f"\n📊 정규화 결과:")
    print(f"  처리 문서: {len(normalized_docs)}개")
    print(f"  평균 품질: {normalization_output['statistics']['average_quality_score']:.1f}/100")

    if normalized_docs:
        high_quality = [d for d in normalized_docs if d["quality_score"] >= 80]
        medium_quality = [d for d in normalized_docs if 60 <= d["quality_score"] < 80]
        low_quality = [d for d in normalized_docs if d["quality_score"] < 60]

        if high_quality:
            print(f"\n✅ 우수 (80점+): {len(high_quality)}개")
            for doc in high_quality:
                print(f"  - {doc['title']} ({doc['quality_score']:.1f}/100)")

        if medium_quality:
            print(f"\n👍 양호 (60~79점): {len(medium_quality)}개")
            for doc in medium_quality:
                print(f"  - {doc['title']} ({doc['quality_score']:.1f}/100)")

        if low_quality:
            print(f"\n⚠️  개선필요 (<60점): {len(low_quality)}개")
            for doc in low_quality:
                print(f"  - {doc['title']} ({doc['quality_score']:.1f}/100)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
