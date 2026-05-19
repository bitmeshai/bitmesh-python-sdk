"""Minimal image generation example."""

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
    try:
        response = client.image(
            {
                "prompt": "A red bicycle by a canal",
                "model": "wan-ai/wan2.6-image",
                "reference_images": ["https://placecats.com/800/600"],
            }
        )
    except BitmeshError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
