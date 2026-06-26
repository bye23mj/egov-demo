#!/usr/bin/env python3
"""docs/{03,04,05} 폴더 내용을 Confluence **폴더 구조**로 미러 업로드(페이지 생성 안 함).

- 디렉터리 → Confluence 폴더(folder), 파일 → 해당 폴더에 직접 첨부.
- 보안 제외: .env(DB 비번), .dat(대용량 덤프), .DS_Store.
- 멱등: 같은 제목 폴더 있으면 재사용(중복 생성 방지). 첨부는 동일 파일명 시 새 버전.
- 사용: python3 scripts/upload_to_confluence_folders.py [--dry-run]
"""
import sys, json, argparse, mimetypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))         # scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 루트(env_loader)
import env_loader; env_loader.load_env(override=True)
from confluence.api import ConfluenceAPI

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ["docs/03. metadata", "docs/04. db-deliverables", "docs/05. db-build"]
TARGET_FOLDER_ID = "677871627"   # Confluence 폴더 "데이터모델링"
SPACE_KEY = "TNYUU"
EXCLUDE_NAMES = {".DS_Store", ".env"}
EXCLUDE_EXT = {".dat"}

c = ConfluenceAPI()
B = c.base_url.rstrip("/")
_SID = None


def space_id():
    global _SID
    if _SID is None:
        r = c.session.get(f"{B}/wiki/rest/api/space/{SPACE_KEY}"); r.raise_for_status()
        _SID = str(r.json()["id"])
    return _SID


def excluded(p: Path):
    return p.name in EXCLUDE_NAMES or p.suffix.lower() in EXCLUDE_EXT


def find_child_folder(title, parent_id):
    """parent 폴더의 직속 자식 중 같은 제목 folder 검색(멱등)."""
    r = c.session.get(f"{B}/wiki/api/v2/folders/{parent_id}/direct-children", params={"limit": 250})
    if r.status_code != 200:
        return None
    for ch in r.json().get("results", []):
        if ch.get("type") == "folder" and ch.get("title") == title:
            return ch.get("id")
    return None


def get_or_create_folder(title, parent_id):
    fid = find_child_folder(title, parent_id)
    if fid:
        return fid, False
    body = {"spaceId": space_id(), "title": title, "parentId": str(parent_id)}
    r = c.session.post(f"{B}/wiki/api/v2/folders", data=json.dumps(body),
                       headers={"Content-Type": "application/json"})
    if r.status_code in (200, 201):
        return r.json()["id"], True
    raise RuntimeError(f"폴더 생성 실패 [{r.status_code}] {title}: {r.text[:160]}")


def upload_attachment(folder_id, filepath: Path):
    ctype = mimetypes.guess_type(filepath.name)[0] or "application/octet-stream"
    with open(filepath, "rb") as fh:
        files = {"file": (filepath.name, fh, ctype)}
        r = c.session.post(
            f"{B}/wiki/rest/api/content/{folder_id}/child/attachment",
            headers={"X-Atlassian-Token": "no-check", "Content-Type": None},
            files=files,
        )
    return r.status_code, ("OK" if r.status_code < 400 else r.text[:150])


def walk(dir_path: Path, parent_folder_id, rel_title, dry):
    files = sorted([p for p in dir_path.iterdir() if p.is_file() and not excluded(p)])
    subdirs = sorted([p for p in dir_path.iterdir() if p.is_dir()])
    print(f"📁 {rel_title}  (파일 {len(files)} / 하위 {len(subdirs)})")
    folder_id = "DRY"
    if not dry:
        # 폴더 제목은 스페이스 전역 유일이어야 하므로 경로 기반 제목 사용(test01/ddl 등 중복 회피)
        folder_id, created = get_or_create_folder(rel_title, parent_folder_id)
        print(f"    {'생성' if created else '재사용'} folder id={folder_id}")
    for f in files:
        if dry:
            print(f"      +file {f.name}")
        else:
            sc, msg = upload_attachment(folder_id, f)
            print(f"      +file [{sc}] {f.name} {('' if sc < 400 else msg)}")
    for sd in subdirs:
        walk(sd, folder_id, f"{rel_title} / {sd.name}", dry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(f"대상 폴더: {TARGET_FOLDER_ID} (space {SPACE_KEY}) | dry-run={a.dry_run}")
    for src in SOURCES:
        d = ROOT / src
        if not d.exists():
            print("skip(없음):", src); continue
        walk(d, TARGET_FOLDER_ID, Path(src).name, a.dry_run)
    print("완료")


if __name__ == "__main__":
    main()
