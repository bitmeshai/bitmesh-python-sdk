"""Integration: tools – try-on clothes."""

from __future__ import annotations

from tests.support import create_client, fixture_path


def test_tools_portrait_try_on_clothes_calls_api() -> None:
    person_path = fixture_path("person.png")
    top_path = fixture_path("top_garment.png")
    bottom_path = fixture_path("bottom_garment.png")
    assert person_path.is_file()
    assert top_path.is_file()
    assert bottom_path.is_file()

    client = create_client(120)
    response = client.tools_portrait_try_on_clothes(
        {
            "task_type": "async",
            "resolution": "-1",
            "restore_face": "true",
        },
        {
            "person_image": str(person_path),
            "top_garment": str(top_path),
            "bottom_garment": str(bottom_path),
        },
    )
    assert isinstance(response, dict)
    assert response.get("status") == "success"
    assert str(response.get("task_id", "")).strip() != ""
