"""Test helpers (shared by integration tests)."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import pytest

from bitmesh_ai import BitmeshClient


def consumer_key() -> str:
    return os.environ.get("BITMESH_TEST_CONSUMER_KEY", "").strip()


def consumer_secret() -> str:
    return os.environ.get("BITMESH_TEST_CONSUMER_SECRET", "").strip()


def skip_if_integration_credentials_missing() -> None:
    if consumer_key() == "" or consumer_secret() == "":
        pytest.skip(
            "Set BITMESH_TEST_CONSUMER_KEY and BITMESH_TEST_CONSUMER_SECRET "
            "to run integration tests."
        )


def create_client(timeout_seconds: int = 120) -> BitmeshClient:
    skip_if_integration_credentials_missing()
    return BitmeshClient(consumer_key(), consumer_secret(), timeout_seconds)


def fixture_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / "fixtures" / filename


def tools_result_path_from_image_url(image_url: str) -> str:
    path = urlparse(image_url).path or ""
    prefix = "/tools-result/"
    if prefix not in path:
        raise ValueError(f"URL does not contain /tools-result/ path: {image_url}")
    idx = path.index(prefix)
    return path[idx + len(prefix) :].lstrip("/")
