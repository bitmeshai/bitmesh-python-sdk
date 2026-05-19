"""Load ``examples/.env`` into the process environment when ``python-dotenv`` is installed."""

from __future__ import annotations

import sys
from pathlib import Path

_EXAMPLES_DIR = Path(__file__).resolve().parent


def load_examples_dotenv() -> None:
    """If ``.env`` exists in the ``examples/`` directory, load it.

    Requires ``python-dotenv`` (``pip install python-dotenv`` or ``pip install -e ".[examples]"``).

    Uses ``override=False`` so variables already set in your shell or OS take precedence.

    If ``.env`` is present but ``python-dotenv`` is not installed, prints a one-line hint to stderr.
    """
    path = _EXAMPLES_DIR / ".env"
    if not path.is_file():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        print(
            "Found examples/.env but python-dotenv is not installed. "
            "Install with: pip install python-dotenv",
            file=sys.stderr,
        )
        return
    load_dotenv(path, override=False)
