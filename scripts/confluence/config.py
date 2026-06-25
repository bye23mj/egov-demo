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

    def get_token(self) -> str:
        """토큰 조회 (환경변수 → .env 파일 → 저장된 값)"""
        # 우선순위 1: 환경변수
        token = os.getenv("CONFLUENCE_TOKEN")
        if token:
            return token
        # 우선순위 2: ~/.confluence-sync/.env 파일
        env_file = self.CONFIG_DIR / ".env"
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("CONFLUENCE_TOKEN="):
                        token = line.split("=", 1)[1].strip()
                        if token:
                            return token
        # 우선순위 3: 저장된 설정값
        token = self.config.get("token")
        if not token:
            raise ValueError("Confluence token not found. Run: python scripts/confluence-sync.py config --set-token <token>")
        return token

    def display(self):
        """현재 설정 표시 (토큰 마스킹)"""
        config_display = self.config.copy()
        if "token" in config_display and config_display["token"]:
            config_display["token"] = config_display["token"][:20] + "..." + config_display["token"][-5:]
        return config_display

# 글로벌 설정 인스턴스
config = ConfluenceConfig()
