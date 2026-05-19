"""Integration: POST /image."""

from __future__ import annotations

from tests.support import create_client


def test_image_calls_api() -> None:
    client = create_client(120)
    response = client.image(
        {
            "prompt": "Make this cat smile",
            "model": "wan-ai/wan2.6-image",
            "reference_images": [
                "https://placecats.com/800/600",
            ],
        }
    )
    assert isinstance(response, dict)
    assert response
    assert "id" in response
    assert str(response["id"]).strip() != ""
