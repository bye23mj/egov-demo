"""JIRA API 클라이언트 테스트"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from jira_api import JiraAPI, JiraConfig

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_connection():
    """JIRA 연결 테스트"""
    print("\n" + "="*60)
    print("1. JIRA 연결 테스트")
    print("="*60)

    try:
        api = JiraAPI()
        if api.test_connection():
            print("✅ JIRA 연결 성공")
            print(f"   Project: {api.project_key}")
            print(f"   URL: {api.base_url}")
            return True
        else:
            print("❌ JIRA 연결 실패")
            return False
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_search_issues():
    """JIRA 이슈 검색 테스트"""
    print("\n" + "="*60)
    print("2. JIRA 이슈 검색 테스트")
    print("="*60)

    try:
        api = JiraAPI()

        # 테스트: 최근 변경된 모든 Deliverable 이슈 조회
        jql = f"project = {api.project_key} AND issuetype = Deliverable ORDER BY updated DESC"
        issues = api.get_issues_by_jql(jql, max_results=5)

        print(f"✅ 이슈 검색 성공: {len(issues)}건 조회됨")

        for issue in issues[:3]:  # 처음 3개만 출력
            key = issue.get("key")
            summary = issue.get("fields", {}).get("summary", "")
            status = issue.get("fields", {}).get("status", {}).get("name", "")
            print(f"\n   {key}: {summary}")
            print(f"   상태: {status}")

        return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_get_attachments():
    """첨부파일 조회 테스트"""
    print("\n" + "="*60)
    print("3. 첨부파일 조회 테스트")
    print("="*60)

    try:
        api = JiraAPI()

        # 테스트 이슈 키 찾기
        jql = f"project = {api.project_key} AND issuetype = Deliverable AND attachment is not EMPTY"
        issues = api.get_issues_by_jql(jql, max_results=1)

        if not issues:
            print("⚠️  첨부파일이 있는 이슈를 찾을 수 없음")
            return True

        issue_key = issues[0].get("key")
        attachments = api.get_attachments(issue_key)

        print(f"✅ 첨부파일 조회 성공: {issue_key} ({len(attachments)}건)")

        for att in attachments[:2]:
            filename = att.get("filename", "")
            size = att.get("size", 0)
            print(f"\n   {filename} ({size} bytes)")

        return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def test_config():
    """JIRA 설정 테스트"""
    print("\n" + "="*60)
    print("4. JIRA 설정 조회")
    print("="*60)

    try:
        config = JiraConfig()
        cfg = config.display()

        print("✅ 설정 조회 성공")
        for key, value in cfg.items():
            print(f"   {key}: {value}")

        return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


def main():
    """모든 테스트 실행"""
    print("\n")
    print("█" * 60)
    print("█  JIRA API 클라이언트 테스트")
    print("█" * 60)

    results = {
        "연결 테스트": test_connection(),
        "설정 조회": test_config(),
        "이슈 검색": test_search_issues(),
        "첨부파일 조회": test_get_attachments(),
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
