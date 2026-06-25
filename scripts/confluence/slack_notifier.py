"""Phase 4: Slack 알림 (완료 보고)"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Slack으로 SDD 자동화 완료를 알림"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        초기화

        Args:
            webhook_url: Slack Webhook URL
                        (기본값: SLACK_WEBHOOK_URL 환경변수)
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')

        if not self.webhook_url:
            logger.warning("Slack 알림 비활성화 (SLACK_WEBHOOK_URL 미설정)")
            self.enabled = False
        else:
            self.enabled = True

    def notify_collection_complete(
        self,
        project_key: str,
        run_id: str,
        issue_count: int,
        document_count: int
    ) -> bool:
        """
        [Phase 1] 문서 수집 완료 알림

        Args:
            project_key: JIRA 프로젝트 키
            run_id: 실행 ID
            issue_count: 수집된 이슈 개수
            document_count: 수집된 문서 개수

        Returns:
            성공 여부
        """
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *SDD Phase 1 완료: Document Collection*\n프로젝트: `{project_key}`"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"📋 *이슈 개수*\n{issue_count}개"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"📄 *문서 개수*\n{document_count}개"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"🆔 *Run ID*\n`{run_id}`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"⏰ *완료*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "▶️ *다음 단계*\n`/sdd-normalize` 실행"
                    }
                }
            ]
        }

        return self._send(payload)

    def notify_normalization_complete(
        self,
        project_key: str,
        run_id: str,
        converted_count: int
    ) -> bool:
        """[Phase 2] 정규화 완료 알림"""
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *SDD Phase 2 완료: Document Normalization*\n프로젝트: `{project_key}`"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"✨ *정규화된 파일*\n{converted_count}개"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"📁 *형식*\nMarkdown (.md)"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"🆔 *Run ID*\n`{run_id}`"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"⏰ *완료*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "▶️ *다음 단계*\n`/sdd-specify` 실행"
                    }
                }
            ]
        }

        return self._send(payload)

    def notify_specification_complete(
        self,
        project_key: str,
        run_id: str,
        requirement_count: int,
        edge_case_count: int
    ) -> bool:
        """[Phase 3] 명세 완료 알림"""
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *SDD Phase 3 완료: Specification Generation*\n프로젝트: `{project_key}`"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"📋 *요구사항*\n{requirement_count}개"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"⚠️ *확인 필요*\n{edge_case_count}개"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"📄 *생성 파일*\n• requirements.md\n• spec.md\n• edge_cases.md"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"⏰ *완료*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "▶️ *다음 단계*\n Edge case 검토 → `/sdd-plan` 실행"
                    }
                }
            ]
        }

        return self._send(payload)

    def notify_planning_complete(
        self,
        project_key: str,
        run_id: str,
        phase_count: int,
        story_count: int,
        table_count: int
    ) -> bool:
        """[Phase 4] 설계 계획 완료 알림"""
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *SDD Phase 4 완료: Design Planning*\n프로젝트: `{project_key}`"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"🔄 *Phase*\n{phase_count}개"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"📖 *Story*\n{story_count}개"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"🗂️ *테이블*\n{table_count}개"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"📄 *생성 파일*\n• plan.md\n• component_spec.md\n• data_model.md\n• TDD.md"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"⏰ *완료*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "▶️ *다음 단계*\n 설계 검증 → `/sdd-tasks` 실행"
                    }
                }
            ]
        }

        return self._send(payload)

    def notify_tasks_complete(
        self,
        project_key: str,
        run_id: str,
        story_count: int,
        subtask_count: int
    ) -> bool:
        """[Phase 5] 작업 분해 완료 알림"""
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *SDD Phase 5 완료: Task Breakdown*\n프로젝트: `{project_key}`"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"📖 *Story*\n{story_count}개"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"✂️ *Sub-task*\n{subtask_count}개"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"📄 *생성 파일*\n• tasks.md (전체 작업)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"⏰ *완료*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "▶️ *다음 단계*\n 팀 회의: 담당자 배정 → 개발 시작"
                    }
                }
            ]
        }

        return self._send(payload)

    def notify_pipeline_complete(
        self,
        project_key: str,
        run_id: str,
        stats: Dict
    ) -> bool:
        """전체 파이프라인 완료 알림"""
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎉 SDD 자동화 파이프라인 완료!"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"프로젝트: `{project_key}`\nRun ID: `{run_id}`"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": self._format_stats(stats)
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⏰ *완료 시간*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📝 *다음 단계*\n1. 생성된 문서 검토\n2. JIRA에 결과 동기화\n3. Confluence에 페이지 생성\n4. 팀 회의 및 개발 시작"
                    }
                }
            ]
        }

        return self._send(payload)

    def notify_error(
        self,
        phase: str,
        error_message: str,
        run_id: str
    ) -> bool:
        """에러 발생 알림"""
        payload = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ *SDD {phase} 실패*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"⚠️ *에러*\n```{error_message}```"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"🆔 *Run ID*\n`{run_id}`"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "📞 *담당자 연락*\n팀에 알림이 전송되었습니다."
                    }
                }
            ]
        }

        return self._send(payload, is_error=True)

    def _format_stats(self, stats: Dict) -> str:
        """통계 포맷팅"""
        lines = ["*📊 생성 결과*\n"]

        if 'requirements' in stats:
            lines.append(f"• 요구사항: {stats['requirements']}개")
        if 'stories' in stats:
            lines.append(f"• Story: {stats['stories']}개")
        if 'subtasks' in stats:
            lines.append(f"• Sub-task: {stats['subtasks']}개")
        if 'tables' in stats:
            lines.append(f"• 테이블: {stats['tables']}개")
        if 'files' in stats:
            lines.append(f"• 생성 파일: {stats['files']}개")

        return "\n".join(lines)

    def _send(self, payload: Dict, is_error: bool = False) -> bool:
        """
        Slack 메시지 전송

        Args:
            payload: Slack Block Kit 페이로드
            is_error: 에러 메시지 여부

        Returns:
            성공 여부
        """
        if not self.enabled:
            logger.debug("Slack 알림 비활성화")
            return False

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✓ Slack 알림 전송")
                return True
            else:
                logger.error(f"Slack 전송 실패 ({response.status_code})")
                return False

        except Exception as e:
            logger.error(f"Slack 전송 에러: {e}")
            return False


if __name__ == "__main__":
    # 테스트
    notifier = SlackNotifier()

    # 테스트 메시지
    stats = {
        'requirements': 30,
        'stories': 4,
        'subtasks': 33,
        'tables': 5,
        'files': 8
    }

    notifier.notify_pipeline_complete("GOVPJT", "REQ-001", stats)
    print("✓ Slack 알림 테스트 완료")
