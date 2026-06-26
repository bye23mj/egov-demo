"""의존성 없는 .env 로더.

저장소 루트의 `.env` 파일을 읽어 `os.environ` 으로 적재한다.
기존 환경변수가 있으면 우선하며(override=False), python-dotenv 없이 동작한다.

사용:
    from env_loader import load_env
    load_env()            # 저장소 루트 .env 자동 탐색·적재
"""
import os
from pathlib import Path


def find_dotenv(start=None):
    """start(또는 이 파일) 기준 상위로 올라가며 첫 .env 를 찾는다."""
    p = Path(start or __file__).resolve()
    for d in [p, *p.parents]:
        f = d / ".env"
        if f.is_file():
            return f
    return None


def load_env(path=None, override=False):
    """`.env` 를 os.environ 으로 적재한다. 적재한 파일 경로(또는 None)를 반환."""
    f = Path(path) if path else find_dotenv()
    if not f or not f.is_file():
        return None
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if override or k not in os.environ:
            os.environ[k] = v
    return f


if __name__ == "__main__":
    p = load_env()
    print(f"로드: {p}" if p else "⚠️ .env 미발견")
