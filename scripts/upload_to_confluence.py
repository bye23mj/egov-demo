#!/usr/bin/env python3
"""docs/{03,04,05} 폴더 내용을 Confluence 폴더(661520431, space TNYUU)에 미러 업로드.

- 디렉터리 → Confluence 페이지(트리 미러), 파일 → 해당 페이지 첨부.
- 보안 제외: .env(DB 비번), .dat(대용량 덤프), .DS_Store.
- 멱등: 같은 제목 페이지 있으면 재사용(중복 생성 방지). 첨부는 동일 파일명 시 새 버전.
- 사용: python3 scripts/upload_to_confluence.py [--dry-run]
"""
import sys, os, json, argparse, mimetypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))         # scripts/ (confluence 패키지)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 저장소 루트 (env_loader)
import env_loader; env_loader.load_env(override=True)
from confluence.api import ConfluenceAPI

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ["docs/03. metadata", "docs/04. db-deliverables", "docs/05. db-build"]
FOLDER_ID = "661520431"          # Confluence 폴더 "04. 설계"
SPACE_KEY = "TNYUU"
TITLE_PREFIX = "[DB] "           # 기존 페이지와 제목 충돌 방지
EXCLUDE_NAMES = {".DS_Store", ".env"}   # .env(DB 비번)는 파일명 기준 제외(suffix가 ''라 확장자 매칭 안 됨)
EXCLUDE_EXT = {".dat"}                   # 대용량 덤프 제외 (.env.example 은 허용)

c = ConfluenceAPI()
B = c.base_url.rstrip("/")
SPACE_ID = None


def space_id():
    global SPACE_ID
    if SPACE_ID is None:
        r = c.session.get(f"{B}/wiki/rest/api/space/{SPACE_KEY}")
        r.raise_for_status(); SPACE_ID = str(r.json()["id"])
    return SPACE_ID


def excluded(p: Path):
    return p.name in EXCLUDE_NAMES or p.suffix.lower() in EXCLUDE_EXT


def find_page(title, parent_id):
    """같은 제목+부모 페이지 검색(멱등)."""
    r = c.session.get(f"{B}/wiki/rest/api/content",
                      params={"title": title, "spaceKey": SPACE_KEY, "expand": "ancestors", "limit": 50})
    if r.status_code != 200:
        return None
    for it in r.json().get("results", []):
        anc = [a.get("id") for a in it.get("ancestors", [])]
        if str(parent_id) in anc:
            return it["id"]
    return None


def create_page(title, parent_id, body_html):
    body = {"spaceId": space_id(), "status": "current", "title": title,
            "parentId": str(parent_id),
            "body": {"representation": "storage", "value": body_html}}
    r = c.session.post(f"{B}/wiki/api/v2/pages", data=json.dumps(body),
                       headers={"Content-Type": "application/json"})
    if r.status_code in (200, 201):
        return r.json()["id"]
    raise RuntimeError(f"페이지 생성 실패 [{r.status_code}] {title}: {r.text[:160]}")


def get_or_create_page(title, parent_id, body_html):
    pid = find_page(title, parent_id)
    if pid:
        return pid, False
    return create_page(title, parent_id, body_html), True


def upload_attachment(page_id, filepath: Path):
    # 세션의 기본 Content-Type(application/json)을 제거해 multipart 로 전송
    ctype = mimetypes.guess_type(filepath.name)[0] or "application/octet-stream"
    with open(filepath, "rb") as fh:
        files = {"file": (filepath.name, fh, ctype)}
        r = c.session.post(
            f"{B}/wiki/rest/api/content/{page_id}/child/attachment",
            headers={"X-Atlassian-Token": "no-check", "Content-Type": None},
            files=files,
        )
    return r.status_code, (r.text[:150] if r.status_code >= 400 else "OK")


def walk_upload(dir_path: Path, parent_page_id, rel_title, dry):
    files = sorted([p for p in dir_path.iterdir() if p.is_file() and not excluded(p)])
    subdirs = sorted([p for p in dir_path.iterdir() if p.is_dir()])
    body = (f"<p><strong>{rel_title}</strong> — 자동 업로드</p>"
            f"<p>파일 {len(files)}개, 하위 {len(subdirs)}개</p>"
            f"<ul>" + "".join(f"<li>{p.name}</li>" for p in files) + "</ul>")
    title = TITLE_PREFIX + rel_title
    print(f"{'· PAGE':8} {title}")
    if dry:
        page_id = "DRY"
    else:
        page_id, created = get_or_create_page(title, parent_page_id, body)
        print(f"{'  '}{'생성' if created else '재사용'} id={page_id}")
    for f in files:
        if dry:
            print(f"{'    +att':8} {f.name}")
        else:
            sc, msg = upload_attachment(page_id, f)
            print(f"{'    +att':8} [{sc}] {f.name} {('' if sc<400 else msg)}")
    for sd in subdirs:
        walk_upload(sd, page_id, f"{rel_title} / {sd.name}", dry)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print(f"대상 Confluence 폴더: {FOLDER_ID} (space {SPACE_KEY})  | dry-run={a.dry_run}")
    if not a.dry_run and not c.test_connection():
        print("Confluence 연결 실패 — 중단"); sys.exit(1)
    for src in SOURCES:
        d = ROOT / src
        if not d.exists():
            print("skip(없음):", src); continue
        walk_upload(d, FOLDER_ID, Path(src).name, a.dry_run)
    print("완료")


if __name__ == "__main__":
    main()
