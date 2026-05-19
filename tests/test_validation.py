"""Local validation tests (no network)."""

from __future__ import annotations

import pytest

from bitmesh_ai import BitmeshClient, BitmeshError


def test_get_transcribe_recorded_rejects_empty_id() -> None:
    client = BitmeshClient("key", "secret")
    with pytest.raises(BitmeshError, match="Transcription job id is required."):
        client.get_transcribe_recorded("  ")


def test_get_video_rejects_empty_id() -> None:
    client = BitmeshClient("key", "secret")
    with pytest.raises(BitmeshError, match="Video job id is required."):
        client.get_video("\n")


def test_tools_query_async_task_result_rejects_empty_task_id() -> None:
    client = BitmeshClient("key", "secret")
    with pytest.raises(BitmeshError, match="Task id is required."):
        client.tools_query_async_task_result("\t")


def test_get_tools_result_rejects_empty_path() -> None:
    client = BitmeshClient("key", "secret")
    with pytest.raises(BitmeshError, match="Tools result path is required."):
        client.get_tools_result("")


def test_tools_portrait_try_on_rejects_missing_file() -> None:
    client = BitmeshClient("key", "secret")
    with pytest.raises(BitmeshError, match="File does not exist or is not readable"):
        client.tools_portrait_try_on_clothes({}, {"person_image": "/no/such/file.png"})


def test_transcribe_rejects_missing_audio() -> None:
    client = BitmeshClient("key", "secret")
    with pytest.raises(BitmeshError, match="Audio file does not exist"):
        client.transcribe_file("/no/such/file.mp3")
