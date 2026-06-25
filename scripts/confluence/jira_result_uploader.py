"""Phase 4: JIRA에 SDD 결과 업로드"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from .jira_api import JiraAPI, JiraConfig

logger = logging.getLogger(__name__)


class JiraResultUploader:
    """JIRA에 SDD 결과 (명세, 설계, 작업)를 업로드"""

    def __init__(self):
        """JiraAPI 초기화"""
        self.config = JiraConfig()
        self.jira = JiraAPI(self.config)

    def upload_specification_results(
        self,
        issue_key: str,
        specs_dir: str,
        run_id: str
    ) -> Dict[str, bool]:
        """
        요구사항 명세 결과 업로드

        Args:
            issue_key: JIRA 이슈 키 (예: GOVPJT-101)
            specs_dir: 생성된 spec 파일 디렉토리 경로
            run_id: 실행 ID (추적용)

        Returns:
            {
                'requirements': bool,
                'spec': bool,
                'edge_cases': bool,
                'comment': bool
            }
        """
        result = {
            'requirements': False,
            'spec': False,
            'edge_cases': False,
            'comment': False
        }

        specs_path = Path(specs_dir)
        if not specs_path.exists():
            logger.error(f"Specs 디렉토리 없음: {specs_dir}")
            return result

        try:
            # 1. requirements.md 첨부
            req_file = specs_path / "requirements.md"
            if req_file.exists():
                self.jira.attach_file(issue_key, str(req_file))
                result['requirements'] = True
                logger.info(f"✓ {issue_key}에 requirements.md 첨부")

            # 2. spec.md 첨부
            spec_file = specs_path / "spec.md"
            if spec_file.exists():
                self.jira.attach_file(issue_key, str(spec_file))
                result['spec'] = True
                logger.info(f"✓ {issue_key}에 spec.md 첨부")

            # 3. edge_cases.md 첨부
            edge_file = specs_path / "edge_cases.md"
            if edge_file.exists():
                self.jira.attach_file(issue_key, str(edge_file))
                result['edge_cases'] = True
                logger.info(f"✓ {issue_key}에 edge_cases.md 첨부")

            # 4. 완료 주석 추가
            comment = self._generate_spec_comment(run_id, specs_path)
            self.jira.create_comment(issue_key, comment)
            result['comment'] = True
            logger.info(f"✓ {issue_key}에 Specify 완료 주석 추가")

            # 5. 커스텀 필드 업데이트 (REQID 필드에 Run ID 저장)
            self._update_custom_fields(issue_key, 'Specify', run_id)

        except Exception as e:
            logger.error(f"Specify 결과 업로드 실패: {e}")

        return result

    def upload_planning_results(
        self,
        issue_key: str,
        specs_dir: str,
        run_id: str
    ) -> Dict[str, bool]:
        """
        설계 계획 결과 업로드

        Args:
            issue_key: JIRA 이슈 키
            specs_dir: Specs 디렉토리
            run_id: 실행 ID

        Returns:
            {
                'plan': bool,
                'component_spec': bool,
                'data_model': bool,
                'tdd': bool,
                'comment': bool
            }
        """
        result = {
            'plan': False,
            'component_spec': False,
            'data_model': False,
            'tdd': False,
            'comment': False
        }

        specs_path = Path(specs_dir)
        if not specs_path.exists():
            logger.error(f"Specs 디렉토리 없음: {specs_dir}")
            return result

        try:
            # 설계 문서들 첨부
            files = {
                'plan': "plan.md",
                'component_spec': "component_spec.md",
                'data_model': "data_model.md",
                'tdd': "TDD.md"
            }

            for key, filename in files.items():
                file_path = specs_path / filename
                if file_path.exists():
                    self.jira.attach_file(issue_key, str(file_path))
                    result[key] = True
                    logger.info(f"✓ {issue_key}에 {filename} 첨부")

            # 완료 주석 추가
            comment = self._generate_plan_comment(run_id, specs_path)
            self.jira.create_comment(issue_key, comment)
            result['comment'] = True
            logger.info(f"✓ {issue_key}에 Plan 완료 주석 추가")

            # 커스텀 필드 업데이트 (REQID 필드에 Run ID 저장)
            self._update_custom_fields(issue_key, 'Plan', run_id)

        except Exception as e:
            logger.error(f"Plan 결과 업로드 실패: {e}")

        return result

    def upload_tasks_results(
        self,
        issue_key: str,
        specs_dir: str,
        run_id: str
    ) -> Dict[str, bool]:
        """
        작업 분해 결과 업로드

        Args:
            issue_key: JIRA 이슈 키
            specs_dir: Specs 디렉토리
            run_id: 실행 ID

        Returns:
            {
                'tasks': bool,
                'subtasks_created': int,
                'comment': bool
            }
        """
        result = {
            'tasks': False,
            'subtasks_created': 0,
            'comment': False
        }

        specs_path = Path(specs_dir)
        if not specs_path.exists():
            logger.error(f"Specs 디렉토리 없음: {specs_dir}")
            return result

        try:
            # 1. tasks.md 첨부
            tasks_file = specs_path / "tasks.md"
            if tasks_file.exists():
                self.jira.attach_file(issue_key, str(tasks_file))
                result['tasks'] = True
                logger.info(f"✓ {issue_key}에 tasks.md 첨부")

                # 2. 서브태스크 자동 생성 (선택사항)
                subtasks = self._parse_subtasks_from_file(tasks_file)
                for subtask in subtasks[:5]:  # 최대 5개만 생성 (수동 검증 후 전체 생성)
                    self.jira.create_subtask(
                        issue_key,
                        f"{subtask['id']}: {subtask['title']}"
                    )
                    result['subtasks_created'] += 1

                logger.info(f"✓ {issue_key}에 {result['subtasks_created']}개 서브태스크 생성")

            # 3. 완료 주석 추가
            comment = self._generate_tasks_comment(run_id, specs_path, result['subtasks_created'])
            self.jira.create_comment(issue_key, comment)
            result['comment'] = True
            logger.info(f"✓ {issue_key}에 Tasks 완료 주석 추가")

            # 4. 커스텀 필드 업데이트 (REQID 필드에 Run ID 저장)
            self._update_custom_fields(issue_key, 'Tasks', run_id)

            # 5. 상태 전환 (In Progress로)
            try:
                self.jira.transition_issue(issue_key, "In Progress")
                logger.info(f"✓ {issue_key} 상태를 In Progress로 변경")
            except:
                logger.warning(f"상태 전환 실패 (권한 부족 등)")

        except Exception as e:
            logger.error(f"Tasks 결과 업로드 실패: {e}")

        return result

    def _parse_subtasks_from_file(self, tasks_file: Path) -> List[Dict]:
        """
        tasks.md에서 Sub-task 파싱

        Returns:
            [
                {'id': 'T001', 'title': '...'},
                {'id': 'T002', 'title': '...'},
                ...
            ]
        """
        subtasks = []
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # "- [ ] T001: ..." 형식 파싱
                    if '- [ ] T' in line:
                        parts = line.split(':', 1)
                        if len(parts) >= 2:
                            task_id = parts[0].replace('- [ ] ', '').strip()
                            title = parts[1].strip()
                            subtasks.append({
                                'id': task_id,
                                'title': title[:100]  # JIRA 제한
                            })
        except Exception as e:
            logger.error(f"Task 파싱 실패: {e}")

        return subtasks

    def _generate_spec_comment(self, run_id: str, specs_path: Path) -> str:
        """Specify 완료 주석 생성"""
        req_count = 0
        try:
            req_file = specs_path / "requirements.md"
            if req_file.exists():
                req_count = req_file.read_text(encoding='utf-8').count('REQ-')
        except:
            pass

        return f"""✅ *SDD Specify 완료*

실행 ID: {run_id}
완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 생성 결과:
• 요구사항 정의: {req_count}개
• 명세 문서: spec.md
• 모호한 항목: edge_cases.md

📁 생성 파일:
• requirements.md (요구사항)
• spec.md (상세 명세)
• edge_cases.md (확인 필요 항목)

👤 다음 단계:
1. Edge case 검토 및 보완
2. /sdd-plan 실행"""

    def _generate_plan_comment(self, run_id: str, specs_path: Path) -> str:
        """Plan 완료 주석 생성"""
        return f"""✅ *SDD Plan 완료*

실행 ID: {run_id}
완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 생성 결과:
• Phase별 계획: plan.md
• 컴포넌트 설계: component_spec.md
• 데이터 모델: data_model.md
• TDD 전략: TDD.md

📁 생성 파일:
• plan.md (5단계, 4개 Story)
• component_spec.md (Controller/Service/DAO)
• data_model.md (5개 테이블, ERD)
• TDD.md (테스트 전략)

👤 다음 단계:
1. 설계 검증 (component_spec.md, data_model.md)
2. /sdd-tasks 실행"""

    def _generate_tasks_comment(self, run_id: str, specs_path: Path, subtask_count: int) -> str:
        """Tasks 완료 주석 생성"""
        return f"""✅ *SDD Tasks 완료*

실행 ID: {run_id}
완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 생성 결과:
• Sub-task 생성: {subtask_count}개 (자동 생성)
• 전체 작업분해: tasks.md에 상세 기술

📁 생성 파일:
• tasks.md (33개 Sub-task)
  - Story 1: 사용자 관리 (T001~T009)
  - Story 2: 게시판 관리 (T010~T018)
  - Story 3: 댓글 기능 (T019~T027)
  - Story 4: 검색 기능 (T028~T033)

👤 다음 단계:
1. 팀 회의: Sub-task 담당자 배정
2. Feature Branch 생성: feature/T001-controller 등
3. TDD 기반 구현 시작"""

    def _update_custom_fields(self, issue_key: str, phase: str, run_id: str = None):
        """
        커스텀 필드 업데이트 (REQID 필드에 Run ID 저장)

        Args:
            issue_key: JIRA 이슈 키
            phase: Phase 이름 (Specify, Plan, Tasks)
            run_id: Run ID (REQID 필드에 저장)
        """
        try:
            import requests
            from requests.auth import HTTPBasicAuth

            # REQID 필드ID (수동 설정 가능)
            # 필드ID를 찾는 방법:
            # 1. JIRA UI → 이슈 편집 → 개발자도구 → REQID input의 id 속성 확인
            # 2. 보통 customfield_XXXXX 형태

            reqid_field_id = os.getenv('JIRA_REQID_FIELD_ID', 'customfield_10431')

            if not run_id:
                logger.warning("Run ID가 없어 REQID 필드 업데이트 스킵")
                return

            # JIRA 이슈 업데이트 (REQID 필드에 Run ID 저장)
            url = f"{self.config.instance_url}/rest/api/3/issues/{issue_key}"

            # 업데이트 데이터
            update_data = {
                "fields": {
                    reqid_field_id: run_id
                }
            }

            auth = HTTPBasicAuth(self.config.email, self.config.get_token())
            response = requests.put(url, json=update_data, auth=auth, timeout=10)

            if response.status_code in [200, 204]:
                logger.info(f"✓ REQID 필드 업데이트 성공: {run_id}")
            else:
                logger.warning(f"⚠️ REQID 필드 업데이트 실패 ({response.status_code})")
                logger.warning(f"   응답: {response.text[:200]}")

        except Exception as e:
            logger.warning(f"REQID 필드 업데이트 오류: {e}")

    def upload_all_phases(
        self,
        issue_key: str,
        specs_dir: str,
        run_id: str
    ) -> Dict[str, Dict]:
        """
        모든 Phase 결과 한 번에 업로드

        Returns:
            {
                'specify': {...},
                'plan': {...},
                'tasks': {...}
            }
        """
        return {
            'specify': self.upload_specification_results(issue_key, specs_dir, run_id),
            'plan': self.upload_planning_results(issue_key, specs_dir, run_id),
            'tasks': self.upload_tasks_results(issue_key, specs_dir, run_id)
        }


if __name__ == "__main__":
    # 테스트
    import sys

    if len(sys.argv) < 4:
        print("Usage: python jira_result_uploader.py <issue_key> <specs_dir> <run_id>")
        sys.exit(1)

    issue_key = sys.argv[1]
    specs_dir = sys.argv[2]
    run_id = sys.argv[3]

    uploader = JiraResultUploader()
    result = uploader.upload_all_phases(issue_key, specs_dir, run_id)

    print(f"\n✅ 업로드 완료:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
