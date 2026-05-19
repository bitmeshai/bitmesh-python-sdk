"""Pytest hooks: load local integration credentials from ``.env.test`` (optional)."""

from __future__ import annotations

from pathlib import Path


def pytest_configure() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    root = Path(__file__).resolve().parent.parent
    env_file = root / ".env.test"
    if env_file.is_file():
        load_dotenv(env_file, override=False)
