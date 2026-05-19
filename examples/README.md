# Bitmesh Python SDK — examples

Small scripts that load credentials from the environment and call `BitmeshClient`. Payload **dicts** match the HTTP API.

## Setup

**1. Install the SDK** (from the repository root):

```bash
cd /path/to/bitmesh-python-sdk
pip install -e .
```

**2. Install `python-dotenv`** so scripts can read **`examples/.env`**:

```bash
pip install python-dotenv
# or, from the repo root (includes the same dependency):
pip install -e ".[examples]"
```

**3. Create `examples/.env`** with your OAuth consumer key and secret:

```bash
cd examples
cp example.env .env
# Edit .env — set BITMESH_CONSUMER_KEY and BITMESH_CONSUMER_SECRET
```

The example scripts call `load_examples_dotenv()` first; it loads **`examples/.env`** only if that file exists. Values already set in your shell are **not** overridden (`override=False`).

**4. Run a script** (from the `examples/` directory):

```bash
python chat_example.py
```

You can still `export BITMESH_CONSUMER_KEY=...` instead of using `.env` if you prefer.

## Scripts

- `chat_example.py` — `POST /chat`
- `image_example.py` — `POST /image`
- `tryon_example.py` — `POST /tools/portrait/try-on-clothes` (submit try-on only; prints `task_id` when async)
- `tryon_poll_example.py` — poll `tools_query_async_task_result(<task_id>)` until done or timeout (pass **`task_id` as the first argument**)
- `env_loader.py` — helper used by the examples to load `.env` (not run directly)

### Try-on: submit then poll

```bash
python tryon_example.py
# Copy task_id from the JSON, then:
python tryon_poll_example.py "YOUR_TASK_ID"
```

### Try-on image paths (submit script only)

By default, `tryon_example.py` looks for `person.png`, `top_garment.png`, and `bottom_garment.png` in **`../tests/fixtures/`** relative to this folder (same files used in SDK tests). You can add overrides to **`examples/.env`**:

```bash
BITMESH_TRYON_PERSON_IMAGE=/path/to/person.png
BITMESH_TRYON_TOP_IMAGE=/path/to/top.png
BITMESH_TRYON_BOTTOM_IMAGE=/path/to/bottom.png
```

Or set the same variables in your shell.

### Try-on poll script (`tryon_poll_example.py`)

Optional **environment variables**:

| Variable | Meaning |
|----------|--------|
| `BITMESH_TRYON_POLL_SECONDS` | Total time to keep polling (default **`60`** — one minute) |
| `BITMESH_TRYON_POLL_INTERVAL` | Seconds between polls (default `3`) |
| `BITMESH_TRYON_OUTPUT` | Filesystem path to write the result image (from `get_tools_result` when `image_url` is present) |

Polling stops when the poll JSON has ``task_status`` **2** (top-level or under ``data``), or on failure-like ``status`` values, or when the poll window ends.

See `../doc/api-reference.md` for every endpoint on `BitmeshClient`.
