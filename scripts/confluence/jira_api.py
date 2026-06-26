"""JIRA REST API 클라이언트"""

import os
import requests
import json
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin, quote
from pathlib import Path
from .config import config

logger = logging.getLogger(__name__)


class JiraConfig:
    """JIRA 설정 관리"""

    CONFIG_DIR = Path.home() / ".jira-sync"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULTS = {
        "jira_url": "https://nsonesoft.atlassian.net",
        "project_key": "GOVPJT",
        "account": "bye23mj@nsonesoft.com",
        "token": None,  # 보안: 환경변수 또는 별도 저장
    }

    def __init__(self):
        """설정 초기화"""
        self.ensure_config_dir()
        self.config = self.load_config()

    @classmethod
    def ensure_config_dir(cls):
        """설정 디렉토리 생성"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(cls.CONFIG_DIR, 0o700)

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """설정 파일 로드"""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return {**cls.DEFAULTS, **config}
        return cls.DEFAULTS.copy()

    def save_config(self):
        """설정 파일 저장"""
        self.ensure_config_dir()
        config_to_save = {k: v for k, v in self.config.items() if k != "token"}
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config_to_save, f, indent=2)

    def set(self, key: str, value: Any):
        """설정값 변경"""
        self.config[key] = value
        self.save_config()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """설정값 조회"""
        return self.config.get(key, default)

    def get_token(self) -> str:
        """토큰 조회 (환경변수 우선)"""
        token = os.getenv("JIRA_TOKEN")
        if token:
            return token

        # 폴백 대상: ~/.confluence-sync/.env + 저장소 루트 .env
        env_files = [self.CONFIG_DIR / ".env"]
        _r = Path(__file__).resolve()
        while _r.parent != _r:
            if (_r / ".env").is_file():
                env_files.append(_r / ".env")
                break
            _r = _r.parent
        for env_file in env_files:
            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("JIRA_TOKEN="):
                            token = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if token:
                                return token

        token = self.config.get("token")
        if not token:
            raise ValueError("JIRA token not found. Run: python scripts/confluence-sync.py jira config --set-token <token>")
        return token

    def display(self):
        """현재 설정 표시 (토큰 마스킹)"""
        config_display = self.config.copy()
        if "token" in config_display and config_display["token"]:
            config_display["token"] = config_display["token"][:20] + "..." + config_display["token"][-5:]
        return config_display


class JiraAPI:
    """JIRA Cloud REST API 클라이언트"""

    def __init__(self, token: Optional[str] = None):
        """
        초기화

        Args:
            token: JIRA API Token (기본값: 설정에서 로드)
        """
        jira_config = JiraConfig()
        self.base_url = jira_config.get("jira_url")
        self.project_key = jira_config.get("project_key")
        self.token = token or jira_config.get_token()
        self.account = jira_config.get("account")
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """인증된 세션 생성"""
        session = requests.Session()
        auth = (self.account, self.token)
        session.auth = auth
        session.headers.update({
            "User-Agent": "egov-demo/sdd-sync",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        return session

    def _url(self, path: str) -> str:
        """API URL 생성"""
        return urljoin(self.base_url, f"/rest/api/3/{path}")

    def test_connection(self) -> bool:
        """연결 테스트"""
        try:
            response = self.session.get(self._url("myself"))
            response.raise_for_status()
            logger.info("✓ JIRA connection successful")
            return True
        except requests.RequestException as e:
            logger.error(f"✗ JIRA connection failed: {e}")
            return False

    def get_issues_by_jql(self, jql: str, fields: Optional[List[str]] = None,
                         max_results: int = 50) -> List[Dict[str, Any]]:
        """
        JQL 기반 이슈 검색

        Args:
            jql: JQL 쿼리
            fields: 조회할 필드 목록 (기본: 모든 필드)
            max_results: 최대 결과 수

        Returns:
            이슈 목록
        """
        # Jira는 구 /rest/api/3/search 를 폐기(410)하고 /search/jql(토큰 페이지네이션)로 이관함
        all_issues = []
        next_page_token = None

        while True:
            params = {
                "jql": jql,
                "maxResults": max_results,
            }
            if fields:
                params["fields"] = ",".join(fields)
            if next_page_token:
                params["nextPageToken"] = next_page_token

            try:
                response = self.session.get(self._url("search/jql"), params=params)
                response.raise_for_status()
                data = response.json()

                issues = data.get("issues", [])
                all_issues.extend(issues)
                logger.debug(f"✓ Fetched {len(issues)} issues (누적 {len(all_issues)})")

                next_page_token = data.get("nextPageToken")
                if data.get("isLast", True) or not next_page_token or not issues:
                    break

            except requests.RequestException as e:
                logger.error(f"✗ Failed to search issues: {e}")
                break

        return all_issues

    def get_issues_by_status(self, status: str,
                            document_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        상태별 이슈 조회

        Args:
            status: Kanban 상태 (예: "내부검토")
            document_types: 문서 유형 필터 (예: ["요구사항정의서", "유스케이스정의서"])

        Returns:
            이슈 목록
        """
        jql_parts = [
            f'project = {self.project_key}',
            f'status = "{status}"',
            'issuetype = Deliverable',
        ]

        if document_types:
            doc_filter = ' OR '.join([f'"Document Type" = "{dt}"' for dt in document_types])
            jql_parts.append(f'({doc_filter})')

        jql = ' AND '.join(jql_parts) + ' ORDER BY updated DESC'

        logger.debug(f"JQL: {jql}")
        return self.get_issues_by_jql(jql)

    def get_issue_detail(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        이슈 상세 정보 조회

        Args:
            issue_key: 이슈 키 (예: GOVPJT-101)

        Returns:
            이슈 데이터
        """
        try:
            response = self.session.get(self._url(f"issue/{issue_key}"))
            response.raise_for_status()
            logger.debug(f"✓ Fetched issue {issue_key}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"✗ Failed to fetch issue {issue_key}: {e}")
            return None

    def get_attachments(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        이슈의 첨부파일 목록 조회

        Args:
            issue_key: 이슈 키

        Returns:
            첨부파일 목록
        """
        try:
            issue = self.get_issue_detail(issue_key)
            if not issue:
                return []

            attachments = issue.get("fields", {}).get("attachment", [])
            logger.debug(f"✓ Found {len(attachments)} attachments in {issue_key}")
            return attachments
        except Exception as e:
            logger.error(f"✗ Failed to fetch attachments for {issue_key}: {e}")
            return []

    def download_attachment(self, attachment_id: str, filename: str) -> Optional[bytes]:
        """
        첨부파일 다운로드

        Args:
            attachment_id: 첨부파일 ID
            filename: 파일명

        Returns:
            파일 바이너리 또는 None
        """
        try:
            # JIRA 첨부파일 다운로드 URL
            url = urljoin(self.base_url, f"/secure/attachment/{attachment_id}/{quote(filename)}")
            response = self.session.get(url)
            response.raise_for_status()
            logger.debug(f"✓ Downloaded attachment: {filename}")
            return response.content
        except requests.RequestException as e:
            logger.error(f"✗ Failed to download attachment {attachment_id}: {e}")
            return None

    def create_comment(self, issue_key: str, comment_body: str,
                      is_internal: bool = False) -> Optional[str]:
        """
        이슈에 댓글 추가

        Args:
            issue_key: 이슈 키
            comment_body: 댓글 본문 (ADF 형식)
            is_internal: 내부 댓글 여부

        Returns:
            생성된 댓글 ID
        """
        payload = {
            "body": {
                "version": 1,
                "type": "doc",
                "content": self._markdown_to_adf(comment_body),
            }
        }

        if is_internal:
            payload["visibility"] = {
                "type": "role",
                "value": "Administrators",
            }

        try:
            response = self.session.post(
                self._url(f"issue/{issue_key}/comment"),
                json=payload
            )
            response.raise_for_status()
            comment_id = response.json().get("id")
            logger.info(f"✓ Created comment in {issue_key}")
            return comment_id
        except requests.RequestException as e:
            logger.error(f"✗ Failed to create comment in {issue_key}: {e}")
            return None

    def attach_file(self, issue_key: str, file_path: str, filename: str) -> Optional[str]:
        """
        이슈에 파일 첨부

        Args:
            issue_key: 이슈 키
            file_path: 로컬 파일 경로
            filename: 첨부될 파일명

        Returns:
            첨부파일 ID
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f)}
                response = self.session.post(
                    self._url(f"issue/{issue_key}/attachments"),
                    files=files,
                    headers={"X-Atlassian-Token": "no-check"}
                )
                response.raise_for_status()

            attachment_id = response.json().get("id")
            logger.info(f"✓ Attached file to {issue_key}: {filename}")
            return attachment_id
        except (requests.RequestException, IOError) as e:
            logger.error(f"✗ Failed to attach file to {issue_key}: {e}")
            return None

    def create_subtask(self, parent_issue_key: str, summary: str,
                      description: str, assignee: Optional[str] = None) -> Optional[str]:
        """
        Sub-task 생성

        Args:
            parent_issue_key: 부모 이슈 키
            summary: 제목
            description: 설명
            assignee: 담당자 ID

        Returns:
            생성된 Sub-task 키
        """
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "parent": {"key": parent_issue_key},
                "issuetype": {"name": "Sub-task"},
                "summary": summary,
                "description": {
                    "version": 1,
                    "type": "doc",
                    "content": self._markdown_to_adf(description),
                },
            }
        }

        if assignee:
            payload["fields"]["assignee"] = {"name": assignee}

        try:
            response = self.session.post(
                self._url("issue"),
                json=payload
            )
            response.raise_for_status()
            subtask_key = response.json().get("key")
            logger.info(f"✓ Created Sub-task: {subtask_key}")
            return subtask_key
        except requests.RequestException as e:
            logger.error(f"✗ Failed to create Sub-task: {e}")
            return None

    def update_custom_field(self, issue_key: str, field_name: str,
                           field_value: Any) -> bool:
        """
        커스텀 필드 업데이트

        Args:
            issue_key: 이슈 키
            field_name: 필드 이름 (예: "customfield_10000")
            field_value: 필드 값

        Returns:
            성공 여부
        """
        payload = {
            "fields": {
                field_name: field_value,
            }
        }

        try:
            response = self.session.put(
                self._url(f"issue/{issue_key}"),
                json=payload
            )
            response.raise_for_status()
            logger.info(f"✓ Updated custom field in {issue_key}")
            return True
        except requests.RequestException as e:
            logger.error(f"✗ Failed to update custom field in {issue_key}: {e}")
            return False

    def transition_issue(self, issue_key: str, transition_id: str) -> bool:
        """
        이슈 상태 변경

        Args:
            issue_key: 이슈 키
            transition_id: 전환 ID (예: "31" for "완료")

        Returns:
            성공 여부
        """
        payload = {
            "transition": {"id": transition_id}
        }

        try:
            response = self.session.post(
                self._url(f"issue/{issue_key}/transitions"),
                json=payload
            )
            response.raise_for_status()
            logger.info(f"✓ Transitioned issue {issue_key}")
            return True
        except requests.RequestException as e:
            logger.error(f"✗ Failed to transition issue {issue_key}: {e}")
            return False

    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        가능한 상태 전환 목록 조회

        Args:
            issue_key: 이슈 키

        Returns:
            전환 목록
        """
        try:
            response = self.session.get(self._url(f"issue/{issue_key}/transitions"))
            response.raise_for_status()
            transitions = response.json().get("transitions", [])
            logger.debug(f"✓ Fetched transitions for {issue_key}")
            return transitions
        except requests.RequestException as e:
            logger.error(f"✗ Failed to fetch transitions for {issue_key}: {e}")
            return []

    def _markdown_to_adf(self, markdown: str) -> List[Dict[str, Any]]:
        """
        Markdown을 JIRA ADF 형식으로 변환 (간단한 버전)

        실제 프로덕션에서는 markdown2adf 라이브러리 사용 권장
        """
        # 간단한 변환: 줄 단위로 단락 처리
        content = []
        lines = markdown.split('\n')

        for line in lines:
            if line.strip():
                content.append({
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": line.strip(),
                        }
                    ]
                })

        return content if content else [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": ""}]
            }
        ]


# 글로벌 설정 인스턴스
jira_config = JiraConfig()
