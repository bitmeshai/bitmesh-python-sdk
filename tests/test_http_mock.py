"""Offline checks for request wiring (mocked HTTP)."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import patch

import pytest
import responses

from bitmesh_ai import BitmeshClient


@pytest.fixture
def frozen_oauth() -> Generator[None, None, None]:
    with (
        patch("bitmesh_ai.client.time.time", return_value=1700000000.0),
        patch("bitmesh_ai.client.secrets.token_hex", return_value="a" * 32),
    ):
        yield


@responses.activate
def test_chat_posts_json_with_oauth_headers(frozen_oauth: None) -> None:
    responses.post(
        "https://api.bitmesh.ai/chat",
        json={"id": "mock-id", "choices": []},
        status=200,
    )

    client = BitmeshClient("ck", "cs", timeout_seconds=30)
    out = client.chat({"messages": [{"role": "user", "content": "hi"}]})
    assert out["id"] == "mock-id"

    assert len(responses.calls) == 1
    req = responses.calls[0].request
    assert req.headers.get("Authorization", "").startswith("OAuth ")
    assert "X-Payload-Signature" in req.headers
    assert req.headers.get("Content-Type", "").startswith("application/json")


@responses.activate
def test_get_tools_result_is_unsigned(frozen_oauth: None) -> None:
    responses.get(
        "https://api.bitmesh.ai/tools-result/foo/bar.png",
        body=b"\x89PNG\r\n\x1a\n",
        status=200,
    )

    client = BitmeshClient("ck", "cs")
    body = client.get_tools_result("foo/bar.png")
    assert body.startswith(b"\x89PNG")

    req = responses.calls[0].request
    assert req.headers.get("Authorization") is None
