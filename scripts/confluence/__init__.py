"""confluence 패키지 — import 시 저장소 루트 .env 자동 로드."""
import sys as _sys
from pathlib import Path as _Path

_root = _Path(__file__).resolve()
while _root.parent != _root and not (_root / ".env").is_file():
    _root = _root.parent
_sys.path.insert(0, str(_root))
try:
    from env_loader import load_env as _load_env
    _load_env()
except Exception:
    pass
