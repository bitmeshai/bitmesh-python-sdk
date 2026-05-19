"""Integration: transcription upload + poll."""

from __future__ import annotations

from tests.support import create_client, fixture_path


def test_transcribe_file_calls_api() -> None:
    audio_path = fixture_path("test_audio.mp3")
    assert audio_path.is_file(), f"Expected transcribe fixture: {audio_path}"

    client = create_client(600)
    response = client.transcribe_file(
        audio_path,
        {"speech_models": ["universal-2"]},
    )
    assert isinstance(response, dict)
    assert response
    assert "id" in response
    assert str(response["id"]).strip() != ""


def test_get_transcribe_recorded_calls_api() -> None:
    audio_path = fixture_path("test_audio.mp3")
    assert audio_path.is_file()

    client = create_client(600)
    accepted = client.transcribe_file(
        audio_path,
        {"speech_models": ["universal-2"]},
    )
    assert "id" in accepted
    transcript_id = str(accepted["id"])
    assert transcript_id

    status_payload = client.get_transcribe_recorded(transcript_id)
    assert isinstance(status_payload, dict)
    assert status_payload
    assert "status" in status_payload
    assert str(status_payload["status"]).strip() != ""
