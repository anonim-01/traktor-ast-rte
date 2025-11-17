from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = (BASE_DIR / "static").resolve()
ADMIN_STATIC_DIR = (STATIC_DIR / "admin").resolve()
BAN_REDIRECT_URL = "https://www.youtube.com/watch?v=KaInAwef530&ab_channel=AliDemirdal"


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "on", "yes"}


class AppConfig:
    secret_key: str = os.getenv("FLASK_SECRET_KEY", "edevlet-dev-secret")
    database_path: Path = Path(os.getenv("DATABASE_PATH", BASE_DIR / "db.sqlite3")).resolve()
    frontend_encryption_enabled: bool = _env_flag("FRONTEND_ENCRYPTION_ENABLED", True)

__all__ = [
    "AppConfig",
    "BASE_DIR",
    "STATIC_DIR",
    "ADMIN_STATIC_DIR",
    "BAN_REDIRECT_URL",
    "_env_flag",
]
