# Bitmesh Python SDK

Python SDK for calling the Bitmesh AI API (chat, image, video, transcription, and tools) with built-in OAuth signing for `https://api.bitmesh.ai`. Browse [all available models](https://bitmesh.ai/models) on Bitmesh.ai.

**Names:** install the distribution **`bitmesh-python-sdk`** with pip. Import the package **`bitmesh_ai`** in code (`from bitmesh_ai import BitmeshClient`).

---

## Install the package

**1. Virtual environment (recommended)**

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

**2. Add the dependency**

- **From PyPI** (once published):

  ```bash
  pip install bitmesh-python-sdk
  ```

  **`requirements.txt`:**

  ```text
  bitmesh-python-sdk>=0.1.0
  ```

  **`pyproject.toml`** dependencies (PEP 621 / Poetry / Hatch, etc.):

  ```toml
  dependencies = [
    "bitmesh-python-sdk>=0.1.0",
  ]
  ```

- **From Git** (specific revision or before PyPI):

  ```bash
  pip install "git+https://github.com/bitmeshai/bitmesh-python-sdk.git"
  ```

  Pin with `@v0.1.0` or `@commit` on the URL.

- **From a local path** (your clone or monorepo):

  ```bash
  pip install /path/to/bitmesh-python-sdk
  pip install -e /path/to/bitmesh-python-sdk   # editable
  ```

**3. Use in code**

Load OAuth consumer key and secret from environment or your app config—do not commit secrets.

```python
from bitmesh_ai import BitmeshClient

client = BitmeshClient(key, secret, timeout_seconds=120)
response = client.chat({...})
```

**4. Credentials (example)**

```bash
export BITMESH_CONSUMER_KEY="your-oauth-consumer-key"
export BITMESH_CONSUMER_SECRET="your-oauth-consumer-secret"
```

---

## Requirements

- Python **3.10+**
- **`requests`** (pulled in automatically as a dependency of this package).

---

## Usage

```python
from bitmesh_ai import BitmeshClient

client = BitmeshClient("YOUR_CONSUMER_KEY", "YOUR_CONSUMER_SECRET", timeout_seconds=120)
response = client.chat(
    {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 32,
        "temperature": 0,
    }
)
print(response)
```

See `doc/code-examples.md` for full snippets and `doc/api-reference.md` for method-level behavior.

---

## Clone this repository (SDK development)

From the repo root:

```bash
pip install .
pip install -e ".[dev]"   # editable + pytest, etc.
```

---

## Development and tests

```bash
pip install -e ".[dev]"
pytest
```

By default, pytest **skips** HTTP integration cases when credentials are unset, runs **local** tests (validation, OAuth parity, mocked HTTP), and **excludes** the `expensive` marker (video generation).

To run integration tests against `https://api.bitmesh.ai`, provide credentials in either of these ways:

**Option A — `.env.test` file (recommended)**

Copy the example file and add your keys (this file is gitignored):

```bash
cp .env.test.example .env.test
# edit .env.test — set BITMESH_TEST_CONSUMER_KEY and BITMESH_TEST_CONSUMER_SECRET
pytest
```

Variables already set in your shell or CI take precedence (the loader does not override them).

**Option B — environment variables**

```bash
export BITMESH_TEST_CONSUMER_KEY="your-oauth-consumer-key"
export BITMESH_TEST_CONSUMER_SECRET="your-oauth-consumer-secret"
pytest
```

To also run video tests (higher cost):

```bash
pytest -m expensive
```

Integration tests use files under `tests/fixtures/` (images and a sample MP3 for transcription).

---

## Examples

See the `examples/` directory for small runnable scripts (`examples/README.md`).

---

## License

MIT. See `LICENSE`.
