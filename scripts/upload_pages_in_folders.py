#!/usr/bin/env python3
"""기존 Confluence 폴더 구조(677871627)를 유지한 채, 파일 있는 폴더마다 **페이지**를 만들고
파일을 페이지에 첨부한다(폴더 직접첨부는 UI 미표시 → 페이지로 전환). 업로드 후 다운로드 검증.

- 폴더는 그대로 사용(경로 기반 제목으로 탐색). 폴더 직접첨부(이전 잔여)는 정리(삭제).
- 페이지 첨부 후 실제 다운로드하여 바이트 크기 == 로컬 크기, xlsx는 ZIP 시그니처(PK) 확인.
- 보안 제외: .env, .dat, .DS_Store.
"""
import sys, mimetypes
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import env_loader; env_loader.load_env(override=True)
from confluence.api import ConfluenceAPI

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ["docs/03. metadata", "docs/04. db-deliverables", "docs/05. db-build"]
TARGET_FOLDER_ID = "677871627"
SPACE_KEY = "TNYUU"
EXCLUDE_NAMES = {".DS_Store", ".env"}
EXCLUDE_EXT = {".dat"}

c = ConfluenceAPI(); B = c.base_url.rstrip("/")
AUTH = c.session.auth          # (email, API_TOKEN) — 예시 코드의 AUTH 와 동일
_SID = None
stats = {"pages": 0, "attach": 0, "attach_fail": 0, "verify_ok": 0, "verify_fail": 0,
         "body_updated": 0, "folder_att_deleted": 0}


def space_id():
    global _SID
    if _SID is None:
        r = c.session.get(f"{B}/wiki/rest/api/space/{SPACE_KEY}"); r.raise_for_status()
        _SID = str(r.json()["id"])
    return _SID


def excluded(p): return p.name in EXCLUDE_NAMES or p.suffix.lower() in EXCLUDE_EXT


def find_child_folder(title, parent_id):
    r = c.session.get(f"{B}/wiki/api/v2/folders/{parent_id}/direct-children", params={"limit": 250})
    if r.status_code != 200: return None
    for ch in r.json().get("results", []):
        if ch.get("type") == "folder" and ch.get("title") == title:
            return ch["id"]
    return None


def find_page_in_folder(title, folder_id):
    """폴더 direct-children(v2, 강한 일관성)으로 동일 제목 페이지 탐색.

    CQL content search는 최종일관성(인덱싱 지연)이라 재실행 시 기존 페이지를 못 찾고
    중복 생성/충돌을 유발하므로 사용하지 않는다.
    """
    r = c.session.get(f"{B}/wiki/api/v2/folders/{folder_id}/direct-children", params={"limit": 250})
    if r.status_code == 200:
        for ch in r.json().get("results", []):
            if ch.get("type") == "page" and ch.get("title") == title:
                return ch["id"]
    return None


def create_page(title, parent_id, body):
    # 예시 코드 패턴: requests.post + auth + json= (세션 기본 Content-Type 의존 제거)
    r = requests.post(
        f"{B}/wiki/api/v2/pages",
        auth=AUTH,
        json={
            "spaceId": space_id(),
            "status": "current",
            "title": title,
            "parentId": str(parent_id),       # 폴더 하위 생성 (예시엔 없지만 본 구조상 필수)
            "body": {"representation": "storage", "value": body},
        },
    )
    if r.status_code in (200, 201): return r.json()["id"]
    raise RuntimeError(f"페이지 생성 실패 [{r.status_code}] {title}: {r.text[:160]}")


def build_body_with_links(page_id, atts):
    """페이지 본문 HTML 생성: 첨부 전체보기 링크 + 파일별 다운로드 링크."""
    view = f"{B}/wiki/pages/viewpageattachments.action?pageId={page_id}"
    items = ""
    for a in sorted(atts, key=lambda x: x.get("title", "")):
        dl = a.get("_links", {}).get("download", "")
        url = (B + "/wiki" + dl) if dl.startswith("/") else dl
        items += f'<li><a href="{url}">{a["title"]}</a></li>'
    return (
        "<p>자동 업로드 산출물</p>"
        f'<p>📎 <a href="{view}">첨부파일 전체 보기</a></p>'
        f"<p><strong>첨부 파일 ({len(atts)})</strong></p><ul>{items}</ul>"
    )


def update_page_body(page_id, html):
    """v2 PUT 으로 페이지 본문 갱신(버전 증가 필요)."""
    r = c.session.get(f"{B}/wiki/api/v2/pages/{page_id}")
    if r.status_code != 200:
        return r.status_code
    j = r.json()
    ver = j["version"]["number"] + 1
    rp = requests.put(
        f"{B}/wiki/api/v2/pages/{page_id}", auth=AUTH,
        json={"id": str(page_id), "status": "current", "title": j["title"],
              "body": {"representation": "storage", "value": html},
              "version": {"number": ver}},
    )
    return rp.status_code


def get_or_create_page(title, parent_id, body):
    pid = find_page_in_folder(title, parent_id)
    if pid:
        return pid, False
    try:
        return create_page(title, parent_id, body), True
    except RuntimeError:
        # 제목 중복(400) 등 경합 시: 폴더에서 다시 탐색해 재사용(크래시 방지)
        pid = find_page_in_folder(title, parent_id)
        if pid:
            return pid, False
        raise


def existing_attachment_id(page_id, filename):
    for a in list_attachments(page_id):
        if a.get("title") == filename:
            return a["id"]
    return None


def upload_attachment(page_id, fp):
    """첨부 생성/갱신(멱등). 동일 파일명이 있으면 update-data 로 새 버전 등록.

    create 엔드포인트는 같은 이름이 이미 있으면 400 을 반환하므로,
    기존 첨부는 `.../attachment/{id}/data` 로 갱신한다.
    """
    ctype = mimetypes.guess_type(fp.name)[0] or "application/octet-stream"
    aid = existing_attachment_id(page_id, fp.name)
    if aid:
        url = f"{B}/wiki/rest/api/content/{page_id}/child/attachment/{aid}/data"
    else:
        url = f"{B}/wiki/rest/api/content/{page_id}/child/attachment"
    with open(fp, "rb") as fh:
        files = {"file": (fp.name, fh, ctype)}
        r = requests.post(url, auth=AUTH,
                          headers={"X-Atlassian-Token": "no-check"}, files=files)
    return r.status_code


def list_attachments(content_id):
    r = c.session.get(f"{B}/wiki/rest/api/content/{content_id}/child/attachment",
                      params={"limit": 100, "expand": "version"})
    return r.json().get("results", []) if r.status_code == 200 else []


def download(att):
    dl = att.get("_links", {}).get("download")
    if not dl: return None
    url = B + "/wiki" + dl if dl.startswith("/") else dl
    r = c.session.get(url)
    return r.content if r.status_code == 200 else None


def verify_page(page_id, files):
    atts = {a["title"]: a for a in list_attachments(page_id)}
    for f in files:
        a = atts.get(f.name)
        local = f.stat().st_size
        data = download(a) if a else None
        ok = data is not None and len(data) == local
        sig = ""
        if data and f.suffix.lower() == ".xlsx":          # xlsx = ZIP(PK)
            sig = " zip-ok" if data[:2] == b"PK" else " ⚠️ZIP서명없음"
            ok = ok and data[:2] == b"PK"
        elif data and f.suffix.lower() == ".xls":          # 구형 xls = OLE2
            ok2 = data[:4] == b"\xd0\xcf\x11\xe0"
            sig = " ole2-ok" if ok2 else " ⚠️OLE2서명없음"
            ok = ok and ok2
        mark = "✅" if ok else "❌"
        stats["verify_ok" if ok else "verify_fail"] += 1
        print(f"        {mark} {f.name}  local={local} dl={len(data) if data else 'None'}{sig}")


def clean_folder_attachments(folder_id, names):
    """폴더에 직접 붙은 동일 이름 첨부(이전 잔여, UI 미표시)만 삭제.

    안전장치: type=='attachment' 인 항목만 삭제(페이지/폴더 오삭제 방지).
    """
    for a in list_attachments(folder_id):
        if a.get("type") == "attachment" and a.get("title") in names:
            r = c.session.delete(f"{B}/wiki/rest/api/content/{a['id']}")
            if r.status_code in (200, 204):
                stats["folder_att_deleted"] += 1


def walk(dir_path, folder_id, rel_title):
    files = sorted([p for p in dir_path.iterdir() if p.is_file() and not excluded(p)])
    subdirs = sorted([p for p in dir_path.iterdir() if p.is_dir()])
    if files:
        page_title = f"{rel_title} — 산출물"
        body = "<p>자동 업로드 산출물</p><ul>" + "".join(f"<li>{p.name}</li>" for p in files) + "</ul>"
        page_id, created = get_or_create_page(page_title, folder_id, body)
        stats["pages"] += 1
        print(f"  📄 PAGE {page_title}  ({'생성' if created else '재사용'} id={page_id})")
        for f in files:
            sc = upload_attachment(page_id, f)
            stats["attach"] += 1
            if sc >= 400:
                stats["attach_fail"] += 1
            print(f"      +att [{sc}] {f.name}")
        verify_page(page_id, files)
        # 업로드 완료 후 본문에 첨부 링크(전체보기 + 파일별 다운로드) 추가
        usc = update_page_body(page_id, build_body_with_links(page_id, list_attachments(page_id)))
        stats["body_updated"] += 1 if usc < 400 else 0
        print(f"      🔗 본문 링크 갱신 [{usc}]")
        clean_folder_attachments(folder_id, {f.name for f in files})
    for sd in subdirs:
        child_title = f"{rel_title} / {sd.name}"
        cfid = find_child_folder(child_title, folder_id)
        if not cfid:
            print(f"  ⚠️ 폴더 없음(스킵): {child_title}"); continue
        walk(sd, cfid, child_title)


def integrity_check(dir_path, folder_id, rel_title, problems):
    """업로드 후 무결성: 파일 있는 폴더는 direct-children 에 페이지가 있고 첨부 수가 일치해야 함."""
    files = [p for p in dir_path.iterdir() if p.is_file() and not excluded(p)]
    if files:
        pid = find_page_in_folder(f"{rel_title} — 산출물", folder_id)
        if not pid:
            problems.append(f"❌ 페이지 없음: {rel_title} (파일 {len(files)})")
        else:
            n = len(list_attachments(pid))
            if n != len(files):
                problems.append(f"❌ 첨부 불일치: {rel_title} (기대 {len(files)} / 실제 {n})")
    for sd in [p for p in dir_path.iterdir() if p.is_dir()]:
        cfid = find_child_folder(f"{rel_title} / {sd.name}", folder_id)
        if cfid:
            integrity_check(sd, cfid, f"{rel_title} / {sd.name}", problems)


def main():
    print(f"대상 폴더: {TARGET_FOLDER_ID} (space {SPACE_KEY})")
    for src in SOURCES:
        d = ROOT / src
        if not d.exists(): continue
        top_title = Path(src).name
        fid = find_child_folder(top_title, TARGET_FOLDER_ID)
        if not fid:
            print(f"⚠️ 최상위 폴더 없음(스킵): {top_title}"); continue
        print(f"📁 {top_title} (id {fid})")
        walk(d, fid, top_title)
    print("\n=== 요약 ===")
    for k, v in stats.items(): print(f"  {k}: {v}")
    # 업로드 후 무결성 재검증(지속성 확인)
    print("\n=== 무결성 재검증 ===")
    problems = []
    for src in SOURCES:
        d = ROOT / src
        if not d.exists(): continue
        fid = find_child_folder(Path(src).name, TARGET_FOLDER_ID)
        if fid:
            integrity_check(d, fid, Path(src).name, problems)
    if problems:
        print("\n".join(problems))
        print(f"⚠️ 문제 {len(problems)}건")
    else:
        print("✅ 전 폴더 페이지·첨부 정상(지속성 확인)")


if __name__ == "__main__":
    main()
