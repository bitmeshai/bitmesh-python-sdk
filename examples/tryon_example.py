"""Virtual try-on clothes: POST /tools/portrait/try-on-clothes (submit only).

Uploads three images and calls ``tools_portrait_try_on_clothes`` with async defaults. The JSON response
usually includes ``task_id`` — use ``tryon_poll_example.py <task_id>`` to poll for the result.

Image paths: defaults to ``../tests/fixtures/`` from a clone, or set ``BITMESH_TRYON_*_IMAGE``. Credentials:
``BITMESH_CONSUMER_KEY`` / ``BITMESH_CONSUMER_SECRET`` (e.g. in ``examples/.env`` via ``env_loader``).
"""

from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path

from bitmesh_ai import BitmeshClient, BitmeshError

from env_loader import load_examples_dotenv


def _resolve_path(env_name: str, default: Path) -> Path:
    override = os.environ.get(env_name, "").strip()
    return Path(override) if override else default


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

    here = Path(__file__).resolve().parent
    repo_fixtures = here.parent / "tests" / "fixtures"

    person = _resolve_path("BITMESH_TRYON_PERSON_IMAGE", repo_fixtures / "person.png")
    top_g = _resolve_path("BITMESH_TRYON_TOP_IMAGE", repo_fixtures / "top_garment.png")
    bottom_g = _resolve_path("BITMESH_TRYON_BOTTOM_IMAGE", repo_fixtures / "bottom_garment.png")

    for label, path in (("person", person), ("top_garment", top_g), ("bottom_garment", bottom_g)):
        if not path.is_file():
            print(
                f"Missing image for {label}: {path}\n"
                "Use env BITMESH_TRYON_PERSON_IMAGE / _TOP_IMAGE / _BOTTOM_IMAGE "
                "or run from the SDK repo clone so ../tests/fixtures/ exists.",
                file=sys.stderr,
            )
            return 1

    client = BitmeshClient(key, secret, timeout_seconds=120)

    try:
        submit = client.tools_portrait_try_on_clothes(
            {
                "task_type": "async",
                "resolution": "-1",
                "restore_face": "true",
            },
            {
                "person_image": str(person),
                "top_garment": str(top_g),
                "bottom_garment": str(bottom_g),
            },
        )
    except BitmeshError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(submit)

    task_id = str(submit.get("task_id") or "").strip()
    if task_id:
        quoted = shlex.quote(task_id)
        print(f"\nPoll for results: python tryon_poll_example.py {quoted}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
