# Bitmesh Python SDK — examples

Small scripts that load credentials from the environment and call `BitmeshClient`. They mirror the PHP demo concepts: **payload dicts** match the HTTP API.

## Setup

From this directory (with the repo root on `PYTHONPATH` or after `pip install` of the package):

```bash
pip install -e ..
export BITMESH_CONSUMER_KEY="your-key"
export BITMESH_CONSUMER_SECRET="your-secret"
python chat_example.py
```

You can also copy `example.env` to `.env` and use a loader of your choice; the scripts below expect plain environment variables.

## Scripts

- `chat_example.py` — `POST /chat`
- `image_example.py` — `POST /image`

See `../doc/api-reference.md` for every endpoint on `BitmeshClient`.
