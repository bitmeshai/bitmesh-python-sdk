"""Integration: POST /chat (live API; skipped if credentials unset)."""

from __future__ import annotations

import pytest

from bitmesh_ai import BitmeshError

from tests.support import create_client


def test_chat_calls_api() -> None:
    client = create_client(120)
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "Reply with exactly: sdk-ok",
            },
        ],
        "max_tokens": 16,
        "temperature": 0,
    }

    try:
        response = client.chat(payload)
    except BitmeshError as exc:
        if "This API key uses a fixed model" not in str(exc):
            raise
        payload.pop("model", None)
        response = client.chat(payload)

    assert isinstance(response, dict)
    assert response
    assert "id" in response
    assert str(response["id"]).strip() != ""


def test_chat_with_image_url_calls_api() -> None:
    client = create_client(120)
    payload = {
        "model": "google/gemma-3n-e4b-it",
        "messages": [
            {"role": "system", "content": "You are a riddle solver."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe the image in one short phrase."},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://placecats.com/600/400"},
                    },
                ],
            },
        ],
        "max_tokens": 64,
    }
    response = client.chat(payload)
    assert isinstance(response, dict)
    assert response
    assert "id" in response
    assert str(response["id"]).strip() != ""
