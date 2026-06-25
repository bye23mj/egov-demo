"""JIRA + Confluence 문서 수집기"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from .jira_api import JiraAPI
from .api import ConfluenceAPI

logger = logging.getLogger(__name__)


@dataclass
class SourceDocument:
    """소스 문서 메타데이터"""
    issue_key: Optional[str] = None
    confluence_page_id: Optional[str] = None
    document_type: str = ""
    source_file_name: str = ""
    source_version: str = ""
    local_file_path: str = ""
    checksum: str = ""
    downloaded_at: str = ""


@dataclass
class SourceMetadata:
    """전체 실행 메타데이터"""
    run_id: str
    project_key: str
    target_status: str
    phase: str
    started_at: str
    source_documents: List[SourceDocument]
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "runId": self.run_id,
            "projectKey": self.project_key,
            "targetStatus": self.target_status,
            "phase": self.phase,
            "startedAt": self.started_at,
            "sourceDocuments": [asdict(doc) for doc in self.source_documents],
            "notes": self.notes,
        }


class DocumentCollector:
    """JIRA + Confluence 문서 수집기"""

    def __init__(self, run_id: str, workspace_dir: Path):
        """
        초기화

        Args:
            run_id: 실행 ID (예: RUN-20260611-001)
            workspace_dir: Speckit Workspace 디렉터리
        """
        self.run_id = run_id
        self.workspace_dir = Path(workspace_dir)
        self.input_dir = self.workspace_dir / "input"
        self.input_dir.mkdir(parents=True, exist_ok=True)

        self.jira_api = JiraAPI()
        self.confluence_api = ConfluenceAPI()

        self.documents: List[SourceDocument] = []

    def collect_from_jira_status(
        self,
        status: str,
        document_types: List[str],
        project_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        JIRA 상태별 문서 수집

        Args:
            status: Kanban 상태 (예: "내부검토")
            document_types: 문서 유형 리스트
            project_key: JIRA 프로젝트 키 (기본값: 설정값)

        Returns:
            수집 통계
        """
        logger.info(f"🔍 JIRA에서 문서 수집 중: {status}")

        stats = {
            "total_issues": 0,
            "collected": 0,
            "errors": 0,
        }

        try:
            # JIRA에서 이슈 검색
            issues = self.jira_api.get_issues_by_status(status, document_types)
            stats["total_issues"] = len(issues)

            for issue in issues:
                issue_key = issue.get("key")
                fields = issue.get("fields", {})
                attachments = fields.get("attachment", [])

                if not attachments:
                    logger.debug(f"⏭  {issue_key}: 첨부파일 없음")
                    continue

                try:
                    self._collect_from_issue(issue_key, attachments)
                    stats["collected"] += 1
                except Exception as e:
                    logger.error(f"✗ {issue_key} 수집 실패: {e}")
                    stats["errors"] += 1

        except Exception as e:
            logger.error(f"✗ JIRA 검색 실패: {e}")
            stats["errors"] += 1

        logger.info(f"✓ JIRA 수집 완료: {stats['collected']}건 수집됨")
        return stats

    def _collect_from_issue(self, issue_key: str, attachments: List[Dict[str, Any]]):
        """JIRA 이슈에서 첨부파일 수집"""
        logger.debug(f"📎 {issue_key}: {len(attachments)}개 첨부파일 처리 중")

        for att in attachments:
            filename = att.get("filename", "")
            att_id = att.get("id", "")
            size = att.get("size", 0)

            # 지원 포맷 필터 (Phase 2에서 확장)
            if not self._is_supported_format(filename):
                logger.debug(f"   ⏭  {filename}: 미지원 형식")
                continue

            # 파일 다운로드
            try:
                content = self.jira_api.download_attachment(att_id, filename)
                if not content:
                    logger.warning(f"   ✗ {filename} 다운로드 실패")
                    continue

                # 로컬 저장
                local_path = self._save_attachment(
                    filename,
                    content,
                    issue_key,
                )

                # 메타데이터 기록
                doc = SourceDocument(
                    issue_key=issue_key,
                    document_type=self._infer_document_type(filename),
                    source_file_name=filename,
                    source_version=self._extract_version(filename),
                    local_file_path=str(local_path.relative_to(self.workspace_dir)),
                    checksum=self._compute_checksum(content),
                    downloaded_at=datetime.now().isoformat(),
                )
                self.documents.append(doc)

                logger.info(f"   ✓ {filename} ({size} bytes)")

            except Exception as e:
                logger.error(f"   ✗ {filename} 처리 실패: {e}")

    def collect_from_confluence(
        self,
        page_urls: List[str],
    ) -> Dict[str, Any]:
        """
        Confluence 페이지에서 문서 수집

        Args:
            page_urls: Confluence 페이지 URL 리스트

        Returns:
            수집 통계
        """
        logger.info(f"🔍 Confluence에서 문서 수집 중")

        stats = {
            "total_pages": len(page_urls),
            "collected": 0,
            "errors": 0,
        }

        for url in page_urls:
            try:
                page_id = self._extract_page_id_from_url(url)
                if not page_id:
                    logger.warning(f"✗ 페이지 ID 추출 실패: {url}")
                    stats["errors"] += 1
                    continue

                # 페이지 본문 조회
                page_data = self.confluence_api.get_page_content(page_id)
                if not page_data:
                    logger.warning(f"✗ 페이지 조회 실패: {page_id}")
                    stats["errors"] += 1
                    continue

                # 첨부파일 조회
                attachments = self.confluence_api.get_attachments(page_id)

                self._collect_from_confluence_page(
                    page_id,
                    page_data,
                    attachments,
                )
                stats["collected"] += 1

            except Exception as e:
                logger.error(f"✗ Confluence 처리 실패: {e}")
                stats["errors"] += 1

        logger.info(f"✓ Confluence 수집 완료: {stats['collected']}건 수집됨")
        return stats

    def _collect_from_confluence_page(
        self,
        page_id: str,
        page_data: Dict[str, Any],
        attachments: List[Dict[str, Any]],
    ):
        """Confluence 페이지 및 첨부파일 수집"""
        title = page_data.get("title", "untitled")
        logger.debug(f"📄 {page_id}: {title}")

        # 페이지 본문을 Markdown으로 저장
        from .converter import html_to_markdown

        html = page_data.get("body", {}).get("view", {}).get("value", "")
        markdown = f"# {title}\n\n" + html_to_markdown(html)

        filename = f"{title}.md"
        local_path = self._save_content(markdown.encode("utf-8"), filename, page_id)

        doc = SourceDocument(
            confluence_page_id=page_id,
            document_type="confluence_page",
            source_file_name=filename,
            source_version="1",
            local_file_path=str(local_path.relative_to(self.workspace_dir)),
            checksum=self._compute_checksum(markdown.encode("utf-8")),
            downloaded_at=datetime.now().isoformat(),
        )
        self.documents.append(doc)

        # 첨부파일도 처리
        for att in attachments:
            att_filename = att.get("title", "")
            att_id = att.get("id", "")

            try:
                content = self.confluence_api.download_attachment(att_id, att_filename)
                if not content:
                    continue

                local_path = self._save_attachment(
                    att_filename,
                    content,
                    page_id,
                )

                doc = SourceDocument(
                    confluence_page_id=page_id,
                    document_type="confluence_attachment",
                    source_file_name=att_filename,
                    local_file_path=str(local_path.relative_to(self.workspace_dir)),
                    checksum=self._compute_checksum(content),
                    downloaded_at=datetime.now().isoformat(),
                )
                self.documents.append(doc)

                logger.info(f"   ✓ {att_filename}")

            except Exception as e:
                logger.error(f"   ✗ {att_filename} 처리 실패: {e}")

    def _save_attachment(
        self,
        filename: str,
        content: bytes,
        source_id: str,
    ) -> Path:
        """첨부파일 저장"""
        # 디렉터리 구조: input/<source_id>/filename
        target_dir = self.input_dir / source_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename

        with open(target_path, "wb") as f:
            f.write(content)

        return target_path

    def _save_content(
        self,
        content: bytes,
        filename: str,
        source_id: str,
    ) -> Path:
        """콘텐츠 저장"""
        target_dir = self.input_dir / source_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename

        with open(target_path, "wb") as f:
            f.write(content)

        return target_path

    def save_metadata(
        self,
        project_key: str,
        target_status: str,
        phase: str = "collect",
        notes: str = "",
    ) -> Path:
        """메타데이터 저장"""
        metadata = SourceMetadata(
            run_id=self.run_id,
            project_key=project_key,
            target_status=target_status,
            phase=phase,
            started_at=datetime.now().isoformat(),
            source_documents=self.documents,
            notes=notes,
        )

        metadata_file = self.workspace_dir / "source-metadata.json"

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)

        logger.info(f"✓ 메타데이터 저장: {metadata_file}")
        return metadata_file

    def get_stats(self) -> Dict[str, Any]:
        """수집 통계"""
        jira_docs = sum(1 for d in self.documents if d.issue_key)
        confluence_docs = sum(1 for d in self.documents if d.confluence_page_id)

        return {
            "total_documents": len(self.documents),
            "from_jira": jira_docs,
            "from_confluence": confluence_docs,
            "workspace_path": str(self.workspace_dir),
            "input_directory": str(self.input_dir),
        }

    # ===== 유틸리티 메서드 =====

    @staticmethod
    def _is_supported_format(filename: str) -> bool:
        """지원 형식 확인 (Phase 1: 모든 형식 허용, Phase 2: 확장)"""
        return True

    @staticmethod
    def _infer_document_type(filename: str) -> str:
        """파일명에서 문서 유형 추론"""
        filename_lower = filename.lower()

        if "요구사항" in filename_lower or "requirement" in filename_lower:
            return "요구사항정의서"
        elif "유스케이스" in filename_lower or "usecase" in filename_lower:
            return "유스케이스정의서"
        elif "컴포넌트" in filename_lower or "component" in filename_lower:
            return "컴포넌트정의서"
        elif "화면" in filename_lower or "screen" in filename_lower:
            return "화면정의서"
        elif "테스트" in filename_lower or "test" in filename_lower:
            return "테스트케이스정의서"
        else:
            return "기타"

    @staticmethod
    def _extract_version(filename: str) -> str:
        """파일명에서 버전 추출"""
        import re

        # v0.3, v1.0, _v2 등의 패턴 찾기
        match = re.search(r'v(\d+\.\d+|\d+)', filename, re.IGNORECASE)
        return match.group(0) if match else "1.0"

    @staticmethod
    def _compute_checksum(content: bytes) -> str:
        """콘텐츠 체크섬 계산"""
        import hashlib

        return hashlib.sha256(content).hexdigest()[:16]

    @staticmethod
    def _extract_page_id_from_url(url: str) -> Optional[str]:
        """Confluence 페이지 URL에서 pageId 추출"""
        import re

        # URL 형식: https://xxx.atlassian.net/wiki/spaces/SPACE/pages/123456/Title
        # 또는: https://xxx.atlassian.net/wiki/pages/123456
        match = re.search(r'/pages/(\d+)', url)
        return match.group(1) if match else None
