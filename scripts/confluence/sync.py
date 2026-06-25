"""Confluence 동기화 로직"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .api import ConfluenceAPI
from .config import config
from .converter import html_to_markdown, markdown_to_html, extract_title_from_markdown

logger = logging.getLogger(__name__)

META_FILENAME = ".confluence-meta.json"


class ConfluenceSync:
    """Confluence ↔ 로컬 파일 동기화 클래스"""

    def __init__(self):
        self.api = ConfluenceAPI()
        self.local_folder = Path(config.get("local_folder"))
        self.local_folder.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.local_folder / META_FILENAME
        self.meta = self._load_meta()

    # ── 메타데이터 관리 ─────────────────────────────────────────

    def _load_meta(self) -> Dict:
        """메타데이터 로드"""
        if self.meta_file.exists():
            with open(self.meta_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"pages": {}, "last_sync": None}

    def _save_meta(self):
        """메타데이터 저장"""
        self.meta["last_sync"] = datetime.now().isoformat()
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

    def _get_page_meta(self, page_id: str) -> Optional[Dict]:
        """페이지 메타데이터 조회"""
        return self.meta["pages"].get(page_id)

    def _set_page_meta(self, page_id: str, data: Dict):
        """페이지 메타데이터 저장"""
        self.meta["pages"][page_id] = data
        self._save_meta()

    def _checksum(self, text: str) -> str:
        """텍스트 체크섬 계산"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    # ── 파일 경로 유틸 ──────────────────────────────────────────

    def _safe_filename(self, title: str) -> str:
        """제목을 파일명으로 변환 (특수문자 제거)"""
        import re
        filename = re.sub(r'[<>:"/\\|?*]', '-', title)
        filename = re.sub(r'\s+', '-', filename.strip())
        return f"{filename}.md"

    def _get_local_path(self, title: str) -> Path:
        """로컬 파일 경로 생성"""
        return self.local_folder / self._safe_filename(title)

    # ── 다운로드 ─────────────────────────────────────────────────

    def download(self, force: bool = False) -> Dict[str, int]:
        """
        Confluence → 로컬 다운로드

        Args:
            force: True면 변경 여부 무시하고 강제 다운로드

        Returns:
            {"downloaded": N, "updated": N, "skipped": N, "errors": N}
        """
        stats = {"downloaded": 0, "updated": 0, "skipped": 0, "errors": 0}

        logger.info("🔄 Fetching pages from Confluence...")
        pages = self.api.list_all_pages()

        if not pages:
            logger.info("No pages found in Confluence folder")
            return stats

        for page in pages:
            page_id = page.get("id")
            title = page.get("title", "untitled")
            remote_version = page.get("version", {}).get("number", 1)
            local_path = self._get_local_path(title)
            existing_meta = self._get_page_meta(page_id)

            # 이미 최신 상태인지 확인
            if not force and existing_meta:
                if existing_meta.get("version") == remote_version and local_path.exists():
                    logger.debug(f"⏭ Skipped (up-to-date): {title}")
                    stats["skipped"] += 1
                    continue

            # 페이지 콘텐츠 조회
            page_data = self.api.get_page_content(page_id)
            if not page_data:
                stats["errors"] += 1
                continue

            # HTML → Markdown 변환
            html = page_data.get("body", {}).get("view", {}).get("value", "")
            markdown = f"# {title}\n\n" + html_to_markdown(html)

            # 파일 저장
            try:
                local_path.write_text(markdown, encoding="utf-8")

                # 첨부파일 다운로드
                attachments = self.api.get_attachments(page_id)
                self._download_attachments(page_id, attachments)

                # 메타데이터 갱신
                self._set_page_meta(page_id, {
                    "page_id": page_id,
                    "title": title,
                    "local_file": local_path.name,
                    "version": remote_version,
                    "checksum": self._checksum(markdown),
                    "last_synced": datetime.now().isoformat(),
                    "space_key": self.api.space_key,
                    "url": page_data.get("_links", {}).get("webui", ""),
                })

                if existing_meta:
                    logger.info(f"⬇ Updated: {title}")
                    stats["updated"] += 1
                else:
                    logger.info(f"⬇ Downloaded: {title}")
                    stats["downloaded"] += 1

            except Exception as e:
                logger.error(f"✗ Failed to save {title}: {e}")
                stats["errors"] += 1

        return stats

    def _download_attachments(self, page_id: str, attachments: List[Dict]):
        """첨부파일 다운로드"""
        if not attachments:
            return
        att_folder = self.local_folder / "attachments"
        att_folder.mkdir(exist_ok=True)
        for att in attachments:
            att_id = att.get("id")
            filename = att.get("title", "attachment")
            data = self.api.download_attachment(att_id, filename)
            if data:
                (att_folder / filename).write_bytes(data)
                logger.debug(f"  📎 Downloaded attachment: {filename}")

    # ── 업로드 ───────────────────────────────────────────────────

    def upload(self, dry_run: bool = False) -> Dict[str, int]:
        """
        로컬 → Confluence 업로드

        Args:
            dry_run: True면 실제 업로드 없이 대상만 출력

        Returns:
            {"created": N, "updated": N, "skipped": N, "errors": N}
        """
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

        # 로컬 .md 파일 목록 (메타 파일 제외)
        local_files = [
            f for f in self.local_folder.glob("*.md")
            if not f.name.startswith(".")
        ]

        # Confluence에 등록된 파일 역방향 맵 (filename → page_id)
        registered_files = {
            v["local_file"]: k
            for k, v in self.meta["pages"].items()
        }

        for md_file in local_files:
            markdown = md_file.read_text(encoding="utf-8")
            title = extract_title_from_markdown(markdown) or md_file.stem
            html = markdown_to_html(markdown)

            if md_file.name in registered_files:
                # 기존 페이지 업데이트 여부 확인
                page_id = registered_files[md_file.name]
                meta = self._get_page_meta(page_id)
                current_checksum = self._checksum(markdown)

                if meta and meta.get("checksum") == current_checksum:
                    logger.debug(f"⏭ Skipped (no changes): {title}")
                    stats["skipped"] += 1
                    continue

                if dry_run:
                    logger.info(f"[DRY-RUN] Would update: {title}")
                    stats["updated"] += 1
                    continue

                success = self.api.update_page(
                    page_id, title, html, meta.get("version", 1)
                )
                if success:
                    meta["checksum"] = current_checksum
                    meta["version"] = meta.get("version", 1) + 1
                    self._set_page_meta(page_id, meta)
                    logger.info(f"⬆ Updated: {title}")
                    stats["updated"] += 1
                else:
                    stats["errors"] += 1

            else:
                # 신규 페이지 생성
                if dry_run:
                    logger.info(f"[DRY-RUN] Would create: {title}")
                    stats["created"] += 1
                    continue

                page_id = self.api.create_page(title, html)
                if page_id:
                    self._set_page_meta(page_id, {
                        "page_id": page_id,
                        "title": title,
                        "local_file": md_file.name,
                        "version": 1,
                        "checksum": self._checksum(markdown),
                        "last_synced": datetime.now().isoformat(),
                        "space_key": self.api.space_key,
                    })
                    logger.info(f"⬆ Created: {title}")
                    stats["created"] += 1
                else:
                    stats["errors"] += 1

        return stats

    # ── 양방향 동기화 ─────────────────────────────────────────────

    def sync(self, local_overwrite: bool = False,
             confluence_overwrite: bool = False) -> Dict[str, int]:
        """
        양방향 동기화

        Args:
            local_overwrite: 충돌 시 로컬 버전 우선
            confluence_overwrite: 충돌 시 Confluence 버전 우선

        Returns:
            통합 통계
        """
        logger.info("🔄 Starting bidirectional sync...")

        # 1. 다운로드
        download_stats = self.download()

        # 2. 업로드
        upload_stats = self.upload()

        return {
            "downloaded": download_stats["downloaded"],
            "updated_local": download_stats["updated"],
            "created": upload_stats["created"],
            "updated_remote": upload_stats["updated"],
            "skipped": download_stats["skipped"] + upload_stats["skipped"],
            "errors": download_stats["errors"] + upload_stats["errors"],
        }

    # ── 상태 조회 ─────────────────────────────────────────────────

    def status(self) -> Dict:
        """동기화 상태 조회"""
        local_files = list(self.local_folder.glob("*.md"))
        registered = self.meta.get("pages", {})

        return {
            "local_folder": str(self.local_folder),
            "local_files": len(local_files),
            "registered_pages": len(registered),
            "last_sync": self.meta.get("last_sync", "Never"),
            "confluence_url": config.get("confluence_url"),
            "space_key": config.get("space_key"),
            "folder_id": config.get("folder_id"),
        }
