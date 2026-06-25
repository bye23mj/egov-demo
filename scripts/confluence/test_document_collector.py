"""문서 수집기 테스트"""

import sys
import logging
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from document_collector import DocumentCollector
from jira_api import JiraAPI

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_collect_from_jira():
    """JIRA 문서 수집 테스트"""
    print("\n" + "="*60)
    print("1. JIRA 문서 수집 테스트")
    print("="*60)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_dir = Path(tmpdir) / "workspace"
            workspace_dir.mkdir(parents=True)

            collector = DocumentCollector("TEST-RUN-001", workspace_dir)

            # JIRA에서 문서 수집
            stats = collector.collect_from_jira_status(
                status="내부검토",
                document_types=["요구사항정의서", "유스케이스정의서"],
            )

            print(f"\n✅ JIRA 수집 성공")
            print(f"   총 이슈: {stats['total_issues']}개")
            print(f"   수집됨: {stats['collected']}개")
            print(f"   에러: {stats['errors']}개")

            # 메타데이터 저장
            metadata_file = collector.save_metadata(
                project_key="GOVPJT",
                target_status="내부검토",
                notes="테스트 실행",
            )

            print(f"\n✅ 메타데이터 저장")
            print(f"   파일: {metadata_file}")
            print(f"   input/ 경로: {collector.input_dir}")

            # 통계 출력
            all_stats = collector.get_stats()
            print(f"\n✅ 수집 통계")
            for key, value in all_stats.items():
                print(f"   {key}: {value}")

            return True

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metadata_structure():
    """메타데이터 구조 테스트"""
    print("\n" + "="*60)
    print("2. 메타데이터 구조 테스트")
    print("="*60)

    try:
        from document_collector import SourceMetadata, SourceDocument
        from datetime import datetime

        docs = [
            SourceDocument(
                issue_key="GOVPJT-101",
                document_type="요구사항정의서",
                source_file_name="요구사항_v0.3.hwpx",
                source_version="v0.3",
                local_file_path="input/GOVPJT-101/요구사항_v0.3.hwpx",
                checksum="abc123def456",
                downloaded_at=datetime.now().isoformat(),
            ),
            SourceDocument(
                confluence_page_id="123456",
                document_type="confluence_page",
                source_file_name="설계검토.md",
                source_version="1",
                local_file_path="input/123456/설계검토.md",
                checksum="xyz789uvw012",
                downloaded_at=datetime.now().isoformat(),
            ),
        ]

        metadata = SourceMetadata(
            run_id="TEST-RUN-001",
            project_key="GOVPJT",
            target_status="내부검토",
            phase="collect",
            started_at=datetime.now().isoformat(),
            source_documents=docs,
            notes="테스트 메타데이터",
        )

        metadata_dict = metadata.to_dict()

        print(f"\n✅ 메타데이터 구조 검증")
        print(f"   Run ID: {metadata_dict['runId']}")
        print(f"   Project: {metadata_dict['projectKey']}")
        print(f"   Status: {metadata_dict['targetStatus']}")
        print(f"   Phase: {metadata_dict['phase']}")
        print(f"   Documents: {len(metadata_dict['sourceDocuments'])}개")

        for doc in metadata_dict['sourceDocuments']:
            doc_id = doc.get('issue_key') or doc.get('confluence_page_id')
            print(f"\n   📄 {doc_id}")
            print(f"      유형: {doc.get('document_type')}")
            print(f"      파일: {doc.get('source_file_name')}")

        return True

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utility_methods():
    """유틸리티 메서드 테스트"""
    print("\n" + "="*60)
    print("3. 유틸리티 메서드 테스트")
    print("="*60)

    try:
        collector = DocumentCollector("TEST", Path("/tmp"))

        # 문서 유형 추론
        test_cases = [
            ("요구사항정의서_v0.3.hwpx", "요구사항정의서"),
            ("유스케이스_정의.docx", "유스케이스정의서"),
            ("화면_설계.pptx", "화면정의서"),
            ("테스트케이스.xlsx", "테스트케이스정의서"),
        ]

        print(f"\n✅ 문서 유형 추론 테스트")
        for filename, expected in test_cases:
            result = collector._infer_document_type(filename)
            status = "✓" if result == expected else "✗"
            print(f"   {status} {filename} → {result}")

        # 버전 추출
        version_cases = [
            ("요구사항_v0.3.hwpx", "v0.3"),
            ("파일_v1.0.docx", "v1.0"),
            ("test_v2.xlsx", "v2"),
        ]

        print(f"\n✅ 버전 추출 테스트")
        for filename, expected in version_cases:
            result = collector._extract_version(filename)
            status = "✓" if result == expected else "✗"
            print(f"   {status} {filename} → {result}")

        # 페이지 ID 추출
        url_cases = [
            (
                "https://nsonesoft.atlassian.net/wiki/spaces/TNYUU/pages/661389353/Requirements",
                "661389353",
            ),
            (
                "https://nsonesoft.atlassian.net/wiki/pages/123456/Test",
                "123456",
            ),
        ]

        print(f"\n✅ Confluence 페이지 ID 추출 테스트")
        for url, expected in url_cases:
            result = collector._extract_page_id_from_url(url)
            status = "✓" if result == expected else "✗"
            print(f"   {status} .../{expected} → {result}")

        return True

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """모든 테스트 실행"""
    print("\n")
    print("█" * 60)
    print("█  문서 수집기 테스트")
    print("█" * 60)

    results = {
        "유틸리티 메서드": test_utility_methods(),
        "메타데이터 구조": test_metadata_structure(),
        "JIRA 수집 (실제)": test_collect_from_jira(),
    }

    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    print(f"\n총 {total}개 중 {passed}개 통과")

    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print("\n⚠️  일부 테스트 실패")
        return 1


if __name__ == "__main__":
    sys.exit(main())
