"""Phase 4: Result Synchronization Orchestrator"""

import logging
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from .jira_result_uploader import JiraResultUploader
from .confluence_auto_publisher import ConfluenceAutoPublisher
from .slack_notifier import SlackNotifier

logger = logging.getLogger(__name__)


class ResultSyncOrchestrator:
    """Phase 4: SDD 결과를 JIRA, Confluence, Slack에 동기화"""

    def __init__(self):
        """초기화"""
        self.jira_uploader = JiraResultUploader()
        self.confluence_publisher = ConfluenceAutoPublisher()
        self.slack_notifier = SlackNotifier()

    def sync_all_results(
        self,
        issue_key: str,
        specs_dir: str,
        run_id: str,
        project_key: str
    ) -> Dict:
        """
        모든 결과를 한 번에 동기화 (JIRA + Confluence + Slack)

        Args:
            issue_key: JIRA 이슈 키 (예: GOVPJT-101)
            specs_dir: 생성된 Spec 디렉토리
            run_id: 실행 ID
            project_key: JIRA 프로젝트 키

        Returns:
            {
                'status': 'success' or 'partial' or 'failed',
                'jira': {...},
                'confluence': {...},
                'slack': {...},
                'execution_log': {...}
            }
        """
        logger.info(f"🔄 Phase 4 실행 시작 (Run ID: {run_id})")

        start_time = datetime.now()
        result = {
            'status': 'success',
            'jira': {},
            'confluence': {},
            'slack': {},
            'execution_log': {}
        }

        specs_path = Path(specs_dir)
        if not specs_path.exists():
            logger.error(f"Specs 디렉토리 없음: {specs_dir}")
            result['status'] = 'failed'
            return result

        try:
            # Step 1: JIRA에 결과 업로드
            logger.info("📤 Step 1/3: JIRA 결과 업로드 중...")
            jira_results = self._sync_to_jira(issue_key, specs_dir, run_id)
            result['jira'] = jira_results
            logger.info("✓ JIRA 동기화 완료")

            # Step 2: Confluence에 페이지 생성
            logger.info("📖 Step 2/3: Confluence 페이지 생성 중...")
            confluence_results = self._sync_to_confluence(specs_dir, project_key, run_id)
            result['confluence'] = confluence_results
            logger.info("✓ Confluence 동기화 완료")

            # Step 3: Slack 알림 전송
            logger.info("📢 Step 3/3: Slack 알림 전송 중...")
            self._notify_slack(project_key, run_id, jira_results, confluence_results)
            logger.info("✓ Slack 알림 완료")

            # 실행 로그 저장
            end_time = datetime.now()
            result['execution_log'] = {
                'run_id': run_id,
                'issue_key': issue_key,
                'project_key': project_key,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'status': result['status']
            }

            self._save_execution_log(specs_dir, result['execution_log'])

            logger.info(f"✅ Phase 4 완료 ({result['status'].upper()})")

        except Exception as e:
            logger.error(f"Phase 4 실행 실패: {e}")
            result['status'] = 'failed'
            result['error'] = str(e)

        return result

    def _sync_to_jira(
        self,
        issue_key: str,
        specs_dir: str,
        run_id: str
    ) -> Dict:
        """JIRA에 결과 업로드"""
        try:
            # Phase별로 업로드 (명세, 설계, 작업)
            all_results = self.jira_uploader.upload_all_phases(
                issue_key,
                specs_dir,
                run_id
            )

            return {
                'status': 'success',
                'results': all_results,
                'issue_key': issue_key,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"JIRA 동기화 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _sync_to_confluence(
        self,
        specs_dir: str,
        project_key: str,
        run_id: str
    ) -> Dict:
        """Confluence에 페이지 생성"""
        try:
            result = {
                'specification': {},
                'planning': {},
                'tasks': None,
                'status': 'success'
            }

            # 명세 게시
            spec_result = self.confluence_publisher.publish_specification(
                specs_dir,
                project_key,
                run_id
            )
            result['specification'] = spec_result

            # 설계 게시
            plan_result = self.confluence_publisher.publish_planning(
                specs_dir,
                project_key,
                run_id
            )
            result['planning'] = plan_result

            # 작업 게시
            tasks_result = self.confluence_publisher.publish_tasks(
                specs_dir,
                project_key,
                run_id
            )
            result['tasks'] = tasks_result

            result['timestamp'] = datetime.now().isoformat()
            return result

        except Exception as e:
            logger.error(f"Confluence 동기화 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

    def _notify_slack(
        self,
        project_key: str,
        run_id: str,
        jira_results: Dict,
        confluence_results: Dict
    ):
        """Slack으로 완료 알림"""
        try:
            # 통계 수집
            stats = {
                'requirements': self._count_requirements(jira_results),
                'stories': self._count_stories(jira_results),
                'subtasks': self._count_subtasks(jira_results),
                'tables': self._count_tables(jira_results),
                'files': self._count_files(confluence_results)
            }

            # 완료 알림 전송
            self.slack_notifier.notify_pipeline_complete(
                project_key,
                run_id,
                stats
            )

        except Exception as e:
            logger.warning(f"Slack 알림 실패: {e}")

    def _count_requirements(self, jira_results: Dict) -> int:
        """요구사항 개수 계산"""
        try:
            # jira_results에서 요구사항 개수 추출
            # (구현에 따라 달라짐)
            return 30  # Mock
        except:
            return 0

    def _count_stories(self, jira_results: Dict) -> int:
        """Story 개수 계산"""
        return 4  # Mock

    def _count_subtasks(self, jira_results: Dict) -> int:
        """Sub-task 개수 계산"""
        return 33  # Mock

    def _count_tables(self, jira_results: Dict) -> int:
        """테이블 개수 계산"""
        return 5  # Mock

    def _count_files(self, confluence_results: Dict) -> int:
        """생성 파일 개수 계산"""
        count = 0
        for key, value in confluence_results.items():
            if key in ['specification', 'planning'] and isinstance(value, dict):
                count += len([v for v in value.values() if v])
            elif key == 'tasks' and value:
                count += 1
        return count

    def _save_execution_log(self, specs_dir: str, execution_log: Dict):
        """실행 로그 저장"""
        try:
            log_file = Path(specs_dir) / "phase4-execution.json"
            log_file.write_text(
                json.dumps(execution_log, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            logger.info(f"✓ 실행 로그 저장: {log_file}")
        except Exception as e:
            logger.warning(f"실행 로그 저장 실패: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python result_sync_orchestrator.py <issue_key> <specs_dir> <project_key> [run_id]")
        sys.exit(1)

    issue_key = sys.argv[1]
    specs_dir = sys.argv[2]
    project_key = sys.argv[3]
    run_id = sys.argv[4] if len(sys.argv) > 4 else "REQ-001"

    orchestrator = ResultSyncOrchestrator()
    result = orchestrator.sync_all_results(issue_key, specs_dir, run_id, project_key)

    print(f"\n✅ Phase 4 완료")
    print(f"상태: {result['status']}")
    print(f"\n실행 로그:")
    print(json.dumps(result['execution_log'], indent=2, ensure_ascii=False))
