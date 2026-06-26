"""Confluence REST API 클라이언트"""

import requests
import json
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin
from .config import config

logger = logging.getLogger(__name__)


class ConfluenceAPI:
    """Confluence Cloud REST API 클라이언트"""

    def __init__(self, token: Optional[str] = None):
        """
        초기화

        Args:
            token: Confluence API Token (기본값: 설정에서 로드)
        """
        self.base_url = config.get("confluence_url")
        self.space_key = config.get("space_key")
        self.folder_id = config.get("folder_id")
        self.token = token or config.get_token()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """인증된 세션 생성"""
        session = requests.Session()
        # Confluence Cloud는 이메일:토큰 형식의 Basic Auth 사용
        account = config.get("account")
        auth = (account, self.token)
        session.auth = auth
        session.headers.update({
            "User-Agent": "egov-demo/confluence-sync",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        return session

    def _url(self, path: str) -> str:
        """API URL 생성 (v2)"""
        return urljoin(self.base_url, f"/wiki/api/v2/{path}")

    def _url_v1(self, path: str) -> str:
        """API URL 생성 (v1) — 일부 인스턴스에서 v2가 404라 v1 사용"""
        return urljoin(self.base_url, f"/wiki/rest/api/{path}")

    def test_connection(self) -> bool:
        """연결 테스트 (v1 space 엔드포인트 — v2 spaces가 404인 인스턴스 대응)"""
        try:
            response = self.session.get(self._url_v1("space"), params={"limit": 1})
            response.raise_for_status()
            logger.info("✓ Confluence connection successful")
            return True
        except requests.RequestException as e:
            logger.error(f"✗ Confluence connection failed: {e}")
            return False

    def get_pages_in_folder(self, folder_id: Optional[str] = None,
                           start: int = 0) -> Dict[str, Any]:
        """
        폴더 내 페이지 조회 (CQL 검색 기반)

        Confluence의 Folder는 page가 아닌 별도 타입이므로
        CQL ancestor 검색으로 하위 콘텐츠를 조회한다.

        Args:
            folder_id: 폴더 ID, 기본값은 설정의 folder_id
            start: 페이징 시작 위치

        Returns:
            {
                "results": [...],
                "totalSize": N,
                "start": N
            }
        """
        folder_id = folder_id or self.folder_id

        # CQL: 폴더의 모든 하위 콘텐츠 (page 타입만)
        cql = f"space.key={self.space_key} AND ancestor={folder_id} AND type=page"
        params = {
            "cql": cql,
            "limit": 50,
            "start": start,
            "expand": "version,ancestors",
        }

        try:
            response = self.session.get(
                urljoin(self.base_url, "/wiki/rest/api/search"),
                params=params
            )
            response.raise_for_status()
            data = response.json()
            # search API 결과를 표준화
            pages = []
            for result in data.get("results", []):
                content = result.get("content", {})
                if content.get("type") == "page":
                    pages.append({
                        "id": content.get("id"),
                        "title": content.get("title"),
                        "version": content.get("version", {}) if content.get("version") else {},
                        "type": "page",
                    })
            logger.debug(f"✓ Fetched {len(pages)} pages from folder {folder_id}")
            return {
                "results": pages,
                "totalSize": data.get("totalSize", len(pages)),
                "start": data.get("start", start),
            }
        except requests.RequestException as e:
            logger.error(f"✗ Failed to fetch pages via CQL: {e}")
            return {"results": [], "totalSize": 0, "start": 0}

    def get_folder_info(self, folder_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        폴더 정보 조회

        Args:
            folder_id: 폴더 ID

        Returns:
            폴더 데이터
        """
        folder_id = folder_id or self.folder_id
        try:
            response = self.session.get(self._url(f"folders/{folder_id}"))
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"✗ Failed to get folder info: {e}")
            return None

    def get_page_content(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        페이지 상세 콘텐츠 조회

        Args:
            page_id: 페이지 ID

        Returns:
            페이지 데이터 (title, body, version 등)
        """
        params = {
            "body-format": "view",  # HTML 형식
        }

        try:
            response = self.session.get(
                self._url(f"pages/{page_id}"),
                params=params
            )
            response.raise_for_status()
            logger.debug(f"✓ Fetched page {page_id}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"✗ Failed to fetch page {page_id}: {e}")
            return None

    def create_page(self, title: str, body_html: str,
                   parent_id: Optional[str] = None) -> Optional[str]:
        """
        새 페이지 생성

        Args:
            title: 페이지 제목
            body_html: 페이지 본문 (HTML)
            parent_id: 부모 페이지 ID, 기본값은 folder_id

        Returns:
            생성된 페이지 ID
        """
        parent_id = parent_id or self.folder_id

        payload = {
            "spaceId": self._get_space_id(),
            "parentId": parent_id,
            "title": title,
            "body": {
                "representation": "storage",
                "value": body_html,
            },
        }

        try:
            response = self.session.post(
                self._url("pages"),
                json=payload
            )
            response.raise_for_status()
            page_id = response.json().get("id")
            logger.info(f"✓ Created page: {title} (ID: {page_id})")
            return page_id
        except requests.RequestException as e:
            logger.error(f"✗ Failed to create page {title}: {e}")
            return None

    def update_page(self, page_id: str, title: str, body_html: str,
                   version_number: int) -> bool:
        """
        페이지 업데이트

        Args:
            page_id: 페이지 ID
            title: 새 제목
            body_html: 새 본문 (HTML)
            version_number: 현재 버전 번호 (낙관적 잠금)

        Returns:
            성공 여부
        """
        payload = {
            "id": page_id,
            "title": title,
            "version": {
                "number": version_number + 1,
            },
            "body": {
                "representation": "storage",
                "value": body_html,
            },
        }

        try:
            response = self.session.put(
                self._url(f"pages/{page_id}"),
                json=payload
            )
            response.raise_for_status()
            logger.info(f"✓ Updated page {page_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"✗ Failed to update page {page_id}: {e}")
            return False

    def get_attachments(self, page_id: str) -> List[Dict[str, Any]]:
        """
        페이지의 첨부파일 목록 조회

        Args:
            page_id: 페이지 ID

        Returns:
            첨부파일 목록
        """
        try:
            response = self.session.get(
                self._url(f"pages/{page_id}/attachments"),
                params={"limit": 50}
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.RequestException as e:
            logger.error(f"✗ Failed to fetch attachments for {page_id}: {e}")
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
            response = self.session.get(
                self._url(f"attachments/{attachment_id}/file")
            )
            response.raise_for_status()
            logger.debug(f"✓ Downloaded attachment: {filename}")
            return response.content
        except requests.RequestException as e:
            logger.error(f"✗ Failed to download attachment {attachment_id}: {e}")
            return None

    def _get_space_id(self) -> str:
        """Space ID 조회 (캐시 없음, 매번 조회)"""
        try:
            response = self.session.get(
                self._url("spaces"),
                params={"space-key": self.space_key, "limit": 1}
            )
            response.raise_for_status()
            space_id = response.json()["results"][0]["id"]
            return space_id
        except (requests.RequestException, IndexError, KeyError) as e:
            logger.error(f"✗ Failed to get space ID: {e}")
            raise

    def list_all_pages(self) -> List[Dict[str, Any]]:
        """
        폴더 내 모든 페이지 조회 (페이징 처리)

        Returns:
            모든 페이지의 flat 리스트
        """
        all_pages = []
        start = 0
        page_size = 50

        while True:
            response = self.get_pages_in_folder(start=start)
            pages = response.get("results", [])
            all_pages.extend(pages)

            total = response.get("totalSize", 0)
            start += len(pages)

            # 모든 페이지 로드 완료
            if start >= total or not pages:
                break

        logger.info(f"✓ Found {len(all_pages)} pages in folder")
        return all_pages
