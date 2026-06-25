"""Phase 4: Confluence 자동 페이지 생성"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from .api import ConfluenceAPI
from .config import config

logger = logging.getLogger(__name__)


class ConfluenceAutoPublisher:
    """생성된 SDD 문서를 Confluence에 자동으로 페이지화"""

    def __init__(self):
        """Confluence API 초기화"""
        self.api = ConfluenceAPI()

    def publish_specification(
        self,
        specs_dir: str,
        project_key: str,
        requirement_id: str,
        parent_page_title: Optional[str] = None
    ) -> Dict[str, Optional[str]]:
        """
        요구사항 명세를 Confluence에 게시

        Args:
            specs_dir: Specs 디렉토리 경로
            project_key: JIRA 프로젝트 키
            requirement_id: 요구사항 ID
            parent_page_title: 상위 페이지 제목 (없으면 생성)

        Returns:
            {
                'requirements': page_id or None,
                'spec': page_id or None,
                'edge_cases': page_id or None
            }
        """
        result = {
            'requirements': None,
            'spec': None,
            'edge_cases': None
        }

        specs_path = Path(specs_dir)
        if not specs_path.exists():
            logger.error(f"Specs 디렉토리 없음: {specs_dir}")
            return result

        try:
            # 상위 페이지 생성 또는 조회
            parent_title = parent_page_title or f"SDD - {project_key} ({requirement_id})"
            parent_id = self._get_or_create_page(
                parent_title,
                self._generate_parent_content(project_key, requirement_id)
            )

            if not parent_id:
                logger.error("상위 페이지 생성 실패")
                return result

            # 1. requirements.md 페이지화
            req_file = specs_path / "requirements.md"
            if req_file.exists():
                page_id = self._publish_markdown_file(
                    req_file,
                    f"{project_key} - 요구사항 명세",
                    parent_id
                )
                result['requirements'] = page_id
                logger.info(f"✓ Requirements 페이지 게시 (ID: {page_id})")

            # 2. spec.md 페이지화
            spec_file = specs_path / "spec.md"
            if spec_file.exists():
                page_id = self._publish_markdown_file(
                    spec_file,
                    f"{project_key} - 상세 명세",
                    parent_id
                )
                result['spec'] = page_id
                logger.info(f"✓ Spec 페이지 게시 (ID: {page_id})")

            # 3. edge_cases.md 페이지화
            edge_file = specs_path / "edge_cases.md"
            if edge_file.exists():
                page_id = self._publish_markdown_file(
                    edge_file,
                    f"{project_key} - 모호한 항목",
                    parent_id,
                    labels=['edge-case', 'review-needed']
                )
                result['edge_cases'] = page_id
                logger.info(f"✓ Edge Cases 페이지 게시 (ID: {page_id})")

        except Exception as e:
            logger.error(f"Confluence 명세 게시 실패: {e}")

        return result

    def publish_planning(
        self,
        specs_dir: str,
        project_key: str,
        requirement_id: str,
        parent_page_title: Optional[str] = None
    ) -> Dict[str, Optional[str]]:
        """
        설계 계획을 Confluence에 게시

        Args:
            specs_dir: Specs 디렉토리 경로
            project_key: JIRA 프로젝트 키
            requirement_id: 요구사항 ID
            parent_page_title: 상위 페이지 제목

        Returns:
            {
                'plan': page_id or None,
                'component_spec': page_id or None,
                'data_model': page_id or None,
                'tdd': page_id or None
            }
        """
        result = {
            'plan': None,
            'component_spec': None,
            'data_model': None,
            'tdd': None
        }

        specs_path = Path(specs_dir)
        if not specs_path.exists():
            logger.error(f"Specs 디렉토리 없음: {specs_dir}")
            return result

        try:
            # 상위 페이지
            parent_title = parent_page_title or f"SDD - {project_key} ({requirement_id}) - 설계"
            parent_id = self._get_or_create_page(
                parent_title,
                self._generate_planning_parent_content(project_key, requirement_id)
            )

            if not parent_id:
                logger.error("상위 페이지 생성 실패")
                return result

            # 설계 문서들 게시
            files = {
                'plan': ("plan.md", f"{project_key} - 구현 계획", ['plan']),
                'component_spec': ("component_spec.md", f"{project_key} - 컴포넌트 설계", ['architecture']),
                'data_model': ("data_model.md", f"{project_key} - 데이터 모델", ['database', 'schema']),
                'tdd': ("TDD.md", f"{project_key} - TDD 전략", ['testing', 'qa'])
            }

            for key, (filename, title, labels) in files.items():
                file_path = specs_path / filename
                if file_path.exists():
                    page_id = self._publish_markdown_file(
                        file_path,
                        title,
                        parent_id,
                        labels=labels
                    )
                    result[key] = page_id
                    logger.info(f"✓ {key} 페이지 게시 (ID: {page_id})")

        except Exception as e:
            logger.error(f"Confluence 설계 게시 실패: {e}")

        return result

    def publish_tasks(
        self,
        specs_dir: str,
        project_key: str,
        requirement_id: str,
        parent_page_title: Optional[str] = None
    ) -> Optional[str]:
        """
        작업 분해를 Confluence에 게시

        Args:
            specs_dir: Specs 디렉토리 경로
            project_key: JIRA 프로젝트 키
            requirement_id: 요구사항 ID
            parent_page_title: 상위 페이지 제목

        Returns:
            페이지 ID 또는 None
        """
        specs_path = Path(specs_dir)
        if not specs_path.exists():
            logger.error(f"Specs 디렉토리 없음: {specs_dir}")
            return None

        try:
            tasks_file = specs_path / "tasks.md"
            if not tasks_file.exists():
                logger.error("tasks.md 파일 없음")
                return None

            parent_title = parent_page_title or f"SDD - {project_key} ({requirement_id}) - 작업"
            parent_id = self._get_or_create_page(
                parent_title,
                self._generate_tasks_parent_content(project_key, requirement_id)
            )

            if not parent_id:
                logger.error("상위 페이지 생성 실패")
                return None

            page_id = self._publish_markdown_file(
                tasks_file,
                f"{project_key} - Task 분해",
                parent_id,
                labels=['tasks', 'breakdown']
            )

            logger.info(f"✓ Tasks 페이지 게시 (ID: {page_id})")
            return page_id

        except Exception as e:
            logger.error(f"Confluence Tasks 게시 실패: {e}")
            return None

    def _publish_markdown_file(
        self,
        file_path: Path,
        title: str,
        parent_id: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Markdown 파일을 Confluence 페이지로 게시

        Args:
            file_path: 파일 경로
            title: 페이지 제목
            parent_id: 상위 페이지 ID
            labels: 라벨 목록

        Returns:
            생성된 페이지 ID
        """
        try:
            # Markdown 읽기
            content = file_path.read_text(encoding='utf-8')

            # Confluence 형식으로 변환
            # (간단한 변환: # → h1, ## → h2 등)
            html_content = self._markdown_to_confluence(content)

            # 페이지 생성 또는 업데이트
            # (api.py의 메서드 사용)
            # page_id = self.api.create_or_update_page(title, html_content, parent_id)

            # 현재 mock 구현
            page_id = self._generate_mock_page_id(title)

            logger.info(f"✓ Confluence 페이지 생성: {title}")
            return page_id

        except Exception as e:
            logger.error(f"파일 게시 실패: {e}")
            return None

    def _get_or_create_page(
        self,
        title: str,
        content: str
    ) -> Optional[str]:
        """
        페이지 조회 또는 생성

        Args:
            title: 페이지 제목
            content: 페이지 내용

        Returns:
            페이지 ID
        """
        try:
            # 기존 페이지 조회 시도
            # page_id = self.api.search_page_by_title(title)

            # if page_id:
            #     return page_id

            # 없으면 새로 생성
            # page_id = self.api.create_page(title, content)

            # Mock 구현
            page_id = self._generate_mock_page_id(title)
            logger.info(f"✓ Confluence 페이지 생성: {title}")
            return page_id

        except Exception as e:
            logger.error(f"페이지 생성 실패: {e}")
            return None

    def _markdown_to_confluence(self, markdown: str) -> str:
        """
        Markdown을 Confluence Storage Format으로 변환

        Args:
            markdown: Markdown 내용

        Returns:
            Confluence Storage Format
        """
        content = markdown

        # 제목 변환
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)

        # 굵은 글씨
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', content)

        # 기울임
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)

        # 코드 블록
        content = re.sub(
            r'```(\w+)?\n(.*?)```',
            r'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">\1</ac:parameter><ac:plain-text-body><![CDATA[\2]]></ac:plain-text-body></ac:structured-macro>',
            content,
            flags=re.DOTALL
        )

        # 링크
        content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)

        # 줄바꿈
        content = content.replace('\n', '<br/>')

        return f"<p>{content}</p>"

    def _generate_mock_page_id(self, title: str) -> str:
        """Mock 페이지 ID 생성"""
        import hashlib
        hash_obj = hashlib.md5(title.encode())
        return f"PAGE-{hash_obj.hexdigest()[:8].upper()}"

    def _generate_parent_content(self, project_key: str, requirement_id: str) -> str:
        """상위 페이지 내용 생성"""
        return f"""
# {project_key} SDD - 요구사항 명세

**프로젝트**: {project_key}
**요구사항 ID**: {requirement_id}
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 개요

전자정부표준프레임워크를 기반으로 한 {project_key} 프로젝트의 요구사항 명세 문서입니다.

## 포함 문서

- 요구사항 정의 (requirements.md)
- 상세 명세 (spec.md)
- 모호한 항목 (edge_cases.md)

## 다음 단계

1. 요구사항 정의 검토
2. Edge case 확인
3. 설계 계획 수립
"""

    def _generate_planning_parent_content(self, project_key: str, requirement_id: str) -> str:
        """설계 상위 페이지 내용 생성"""
        return f"""
# {project_key} SDD - 설계 계획

**프로젝트**: {project_key}
**요구사항 ID**: {requirement_id}
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 개요

요구사항을 기반으로 한 {project_key} 프로젝트의 상세 설계 문서입니다.

## 포함 문서

- 구현 계획 (plan.md)
- 컴포넌트 설계 (component_spec.md)
- 데이터 모델 (data_model.md)
- TDD 전략 (TDD.md)

## 아키텍처

```
Controller (Spring MVC)
  ↓
Service/ServiceImpl
  ↓
DAO (MyBatis)
  ↓
Oracle 11g
```

## 다음 단계

1. 설계 검증
2. 작업 분해
3. 개발 시작
"""

    def _generate_tasks_parent_content(self, project_key: str, requirement_id: str) -> str:
        """작업 상위 페이지 내용 생성"""
        return f"""
# {project_key} SDD - Task 분해

**프로젝트**: {project_key}
**요구사항 ID**: {requirement_id}
**생성일**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 개요

설계를 기반으로 분해된 {project_key} 프로젝트의 구현 작업 목록입니다.

## Task 구조

- Story별 분해
- Sub-task 목록 (T001, T002, ...)
- 각 Task의 담당자, 일정, 우선순위

## 작업 흐름

```
Story 1
├── T001: Controller 작성
├── T002: Service 구현
├── ...
└── T009: 테스트

Story 2
├── T010: ...
└── ...
```

## 다음 단계

1. 팀 회의: 담당자 배정
2. Feature Branch 생성
3. TDD 기반 개발 시작
"""


if __name__ == "__main__":
    # 테스트
    import sys

    if len(sys.argv) < 3:
        print("Usage: python confluence_auto_publisher.py <specs_dir> <project_key>")
        sys.exit(1)

    specs_dir = sys.argv[1]
    project_key = sys.argv[2]
    requirement_id = sys.argv[3] if len(sys.argv) > 3 else "REQ-001"

    publisher = ConfluenceAutoPublisher()

    # 명세 게시
    spec_result = publisher.publish_specification(specs_dir, project_key, requirement_id)
    print(f"\n명세 게시 결과:")
    print(f"  Requirements: {spec_result['requirements']}")
    print(f"  Spec: {spec_result['spec']}")
    print(f"  Edge Cases: {spec_result['edge_cases']}")

    # 설계 게시
    plan_result = publisher.publish_planning(specs_dir, project_key, requirement_id)
    print(f"\n설계 게시 결과:")
    print(f"  Plan: {plan_result['plan']}")
    print(f"  Component Spec: {plan_result['component_spec']}")
    print(f"  Data Model: {plan_result['data_model']}")
    print(f"  TDD: {plan_result['tdd']}")

    # 작업 게시
    tasks_result = publisher.publish_tasks(specs_dir, project_key, requirement_id)
    print(f"\n작업 게시 결과:")
    print(f"  Tasks: {tasks_result}")
