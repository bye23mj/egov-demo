"""Confluence 동기화 설정 관리"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ConfluenceConfig:
    """설정 파일 관리 클래스"""

    CONFIG_DIR = Path.home() / ".confluence-sync"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULTS = {
        "confluence_url": "https://nsonesoft.atlassian.net",
        "space_key": "TNYUU",
        "folder_id": "661389353",
        "account": "bye23mj@nsonesoft.com",
        "local_folder": "/Users/ai/vscode/egov-demo/docs/00. confluence",
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
        # 보안: 홈 디렉토리 내 설정 폴더는 700 권한
        os.chmod(cls.CONFIG_DIR, 0o700)

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """설정 파일 로드"""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r') as f:
                config = json.load(f)
            # 기본값과 병합
            return {**cls.DEFAULTS, **config}
        return cls.DEFAULTS.copy()

    def save_config(self):
        """설정 파일 저장"""
        self.ensure_config_dir()
        # 토큰은 저장하지 않음 (환경변수 사용)
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

    # Atlassian 토큰은 계정 단위라 Confluence/Jira 공용. 아래 키들을 우선순위로 탐색.
    TOKEN_KEYS = ("CONFLUENCE_API_TOKEN", "CONFLUENCE_TOKEN", "JIRA_TOKEN", "JIRA_API_TOKEN")

    def get_token(self) -> str:
        """토큰 조회 (환경변수 → 저장소 루트 .env → ~/.confluence-sync/.env → 저장된 값)."""
        # 1: 환경변수 (env_loader 가 저장소 .env 를 os.environ 으로 적재한 상태 포함)
        for key in self.TOKEN_KEYS:
            token = os.getenv(key)
            if token:
                return token
        # 2: .env 파일들 (저장소 루트 + ~/.confluence-sync)
        env_files = []
        _r = Path(__file__).resolve()
        while _r.parent != _r:
            if (_r / ".env").is_file():
                env_files.append(_r / ".env")
                break
            _r = _r.parent
        env_files.append(self.CONFIG_DIR / ".env")
        for env_file in env_files:
            if env_file.exists():
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    if k.strip() in self.TOKEN_KEYS and v.strip():
                        return v.strip().strip('"').strip("'")
        # 3: 저장된 설정값
        token = self.config.get("token")
        if not token:
            raise ValueError("Confluence token not found. .env 에 CONFLUENCE_API_TOKEN 또는 JIRA_TOKEN 설정")
        return token

    def display(self):
        """현재 설정 표시 (토큰 마스킹)"""
        config_display = self.config.copy()
        if "token" in config_display and config_display["token"]:
            config_display["token"] = config_display["token"][:20] + "..." + config_display["token"][-5:]
        return config_display

# 글로벌 설정 인스턴스
config = ConfluenceConfig()
