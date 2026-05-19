"""OAuth signature parity with the PHP reference client."""

from __future__ import annotations

from bitmesh_ai.client import generate_oauth_signature


def test_oauth_signature_matches_php_reference() -> None:
    method = "POST"
    url = "https://api.bitmesh.ai/chat"
    params = {
        "oauth_consumer_key": "ck",
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": "1700000000",
        "oauth_nonce": "abcd1234" * 4,
        "oauth_version": "1.0",
    }
    expected = "a7CpVIS/uRWBYBWxYg9kDIwZHl8="
    assert generate_oauth_signature(method, url, params, "cs") == expected


def test_oauth_includes_query_string_params() -> None:
    method = "GET"
    url = "https://api.bitmesh.ai/video/job-1?test=1"
    params = {
        "oauth_consumer_key": "ck",
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": "1",
        "oauth_nonce": "n",
        "oauth_version": "1.0",
    }
    sig1 = generate_oauth_signature(method, url, params, "secret")
    sig2 = generate_oauth_signature(method, url, params, "secret")
    assert sig1 == sig2
    assert len(sig1) > 0
