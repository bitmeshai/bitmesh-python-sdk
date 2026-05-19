"""Multipart field flattening parity with the PHP client."""

from __future__ import annotations

from bitmesh_ai.client import flatten_multipart_fields


def test_flatten_nested_dict_and_list() -> None:
    fields = {"speech_models": ["universal-2"], "meta": {"n": 1}}
    out = flatten_multipart_fields(fields)
    assert out["speech_models[0]"] == "universal-2"
    assert out["meta[n]"] == 1
