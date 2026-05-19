"""Minimal chat example using BITMESH_CONSUMER_KEY / BITMESH_CONSUMER_SECRET."""

from __future__ import annotations

import os
import sys

from bitmesh_ai import BitmeshClient, BitmeshError

from env_loader import load_examples_dotenv


def main() -> int:
    load_examples_dotenv()
    key = os.environ.get("BITMESH_CONSUMER_KEY", "").strip()
    secret = os.environ.get("BITMESH_CONSUMER_SECRET", "").strip()
    if not key or not secret:
        print(
            "Set BITMESH_CONSUMER_KEY and BITMESH_CONSUMER_SECRET "
            "(e.g. in examples/.env — see examples/README.md)",
            file=sys.stderr,
        )
        return 1

    client = BitmeshClient(key, secret, timeout_seconds=120)
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Reply with exactly: ok"},
        ],
        "max_tokens": 32,
        "temperature": 0,
    }

    try:
        response = client.chat(payload)
    except BitmeshError as exc:
        if "This API key uses a fixed model" not in str(exc):
            raise
        payload.pop("model", None)
        response = client.chat(payload)

    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
