"""Integration: tools – background removal + unsigned tools-result fetch."""

from __future__ import annotations

from tests.support import create_client, fixture_path, tools_result_path_from_image_url


def test_tools_general_background_removal_and_get_tools_result() -> None:
    image_path = fixture_path("stool.png")
    assert image_path.is_file()

    client = create_client(120)
    response = client.tools_general_background_removal({"return_form": "mask"}, image_path)
    assert isinstance(response, dict)
    assert response.get("status") == "success"
    image_url = (response.get("data") or {}).get("image_url")
    assert image_url

    result_path = tools_result_path_from_image_url(str(image_url))
    image_bytes = client.get_tools_result(result_path)
    assert image_bytes
