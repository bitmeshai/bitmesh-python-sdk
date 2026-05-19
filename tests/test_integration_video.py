"""Integration: POST /video (expensive / higher cost)."""

from __future__ import annotations

import pytest

from tests.support import create_client


@pytest.mark.expensive
def test_video_calls_api() -> None:
    client = create_client(180)
    response = client.video(
        {
            "prompt": "Make this car run fast",
            "model": "bytedance/seedance-1.0-lite",
            "frame_images": [
                {
                    "input_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
                    "frame": 0,
                },
            ],
        }
    )
    assert isinstance(response, dict)
    assert response
    assert "id" in response
    assert str(response["id"]).strip() != ""
