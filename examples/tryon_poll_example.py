"""Poll async try-on result: ``tools_query_async_task_result`` until done or timeout.

Pass ``task_id`` on the command line (the value from ``tryon_example.py`` submit response).

Polling stops when ``task_status`` is **2** (checked at the top level or under ``data``), or when
``status`` indicates a failure (``failed``, ``error``, …), or when the time window ends.

By default polls for **60 seconds** with **3** seconds between calls. Optional env (see ``examples/README.md``):
``BITMESH_TRYON_POLL_SECONDS``, ``BITMESH_TRYON_POLL_INTERVAL``, ``BITMESH_TRYON_OUTPUT``.

Credentials: ``BITMESH_CONSUMER_KEY`` / ``BITMESH_CONSUMER_SECRET`` (e.g. ``examples/.env``).

Usage::

    python tryon_poll_example.py YOUR_TASK_ID
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from bitmesh_ai import BitmeshClient, BitmeshError

from env_loader import load_examples_dotenv

# Failure ``status`` values that should end polling even if ``task_status`` is not 2 yet.
_FAILURE_STATUSES = frozenset(
    {
        "failed",
        "error",
        "failure",
        "cancelled",
        "canceled",
    }
)


def _task_status_value(response: dict) -> object | None:
    if "task_status" in response:
        return response.get("task_status")
    data = response.get("data")
    if isinstance(data, dict) and "task_status" in data:
        return data.get("task_status")
    return None


def _is_task_finished(task_status: object) -> bool:
    """API convention: ``task_status`` ``2`` means the async job is done."""
    return task_status == 2 or task_status == "2"


def _tools_result_relative_path(image_url: str) -> str:
    path = urlparse(image_url).path or ""
    prefix = "/tools-result/"
    if prefix not in path:
        raise ValueError(f"URL does not contain {prefix}: {image_url!r}")
    idx = path.index(prefix)
    return path[idx + len(prefix) :].lstrip("/")


def _poll_finished(response: dict) -> bool:
    """Stop when ``task_status`` is 2, or on HTTP-level failure status."""
    if _is_task_finished(_task_status_value(response)):
        return True
    st = str(response.get("status", "")).strip().lower()
    if st in _FAILURE_STATUSES:
        return True
    return False


def _poll_until_done(
    client: BitmeshClient,
    task_id: str,
    *,
    interval: float,
    duration_seconds: float,
) -> dict:
    deadline = time.monotonic() + duration_seconds
    last: dict = {}
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        print(
            f"\n--- Poll attempt {attempt} "
            f"(polling window: {duration_seconds:g}s, tools_query_async_task_result) ---",
        )
        last = client.tools_query_async_task_result(task_id)
        print(last)
        if _poll_finished(last):
            return last
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(interval, remaining))
    print(
        f"\nStopped after the {duration_seconds:g}s polling window (task may still be running). "
        "Increase BITMESH_TRYON_POLL_SECONDS if needed.",
        file=sys.stderr,
    )
    return last


def _maybe_save_result_image(client: BitmeshClient, poll_response: dict) -> None:
    out = os.environ.get("BITMESH_TRYON_OUTPUT", "").strip()
    if not out:
        return
    data = poll_response.get("data")
    if not isinstance(data, dict):
        print("BITMESH_TRYON_OUTPUT is set but response has no data.image_url; skipping save.", file=sys.stderr)
        return
    url = data.get("image_url") or data.get("result_image_url")
    if not url:
        print("BITMESH_TRYON_OUTPUT is set but no image_url in poll response; skipping save.", file=sys.stderr)
        return
    try:
        rel = _tools_result_relative_path(str(url))
    except ValueError as exc:
        print(f"Could not parse tools-result path: {exc}", file=sys.stderr)
        return
    try:
        raw = client.get_tools_result(rel)
    except BitmeshError as exc:
        print(f"get_tools_result failed: {exc}", file=sys.stderr)
        return
    path = Path(out).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    print(f"\nSaved result image to {path} ({len(raw)} bytes).")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Poll Bitmesh async try-on task status (tools_query_async_task_result).",
    )
    parser.add_argument(
        "task_id",
        help="task_id from tryon_example.py (or async try-on submit response)",
    )
    args = parser.parse_args()
    task_id = args.task_id.strip()
    if not task_id:
        print("task_id must be non-empty.", file=sys.stderr)
        return 1

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

    poll_interval = float(os.environ.get("BITMESH_TRYON_POLL_INTERVAL", "3").strip() or "3")
    poll_seconds = float(os.environ.get("BITMESH_TRYON_POLL_SECONDS", "60").strip() or "60")
    if poll_interval <= 0:
        poll_interval = 3.0
    if poll_seconds <= 0:
        poll_seconds = 60.0

    client = BitmeshClient(key, secret, timeout_seconds=120)

    print(f"Polling task_id={task_id!r} for up to {poll_seconds:g}s…", file=sys.stderr)
    try:
        final = _poll_until_done(
            client,
            task_id,
            interval=poll_interval,
            duration_seconds=poll_seconds,
        )
    except BitmeshError as exc:
        print(f"Poll failed: {exc}", file=sys.stderr)
        return 1

    _maybe_save_result_image(client, final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
