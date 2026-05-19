# Bitmesh Python SDK

Python SDK for calling the Bitmesh AI API (chat, image, video, transcription, and tools) with the same OAuth signing model as the official PHP client. Browse [all available models](https://bitmesh.ai/models) on Bitmesh.ai.

**Package names:** the installable distribution is **`bitmesh-python-sdk`** (what you `pip install`). The Python import module is **`bitmesh_ai`** (`from bitmesh_ai import BitmeshClient`).

---

## Using this SDK in your project

If you know Composer for PHP, the usual Python flow is: **virtual environment → declare dependency → `pip install` → import in code** (there is no separate autoload step).

| PHP (Composer) | Python (pip) |
|----------------|--------------|
| `composer require bitmeshai/bitmesh-php-sdk` | `pip install bitmesh-python-sdk` (from PyPI, when published) |
| `composer install` from `composer.lock` | `pip install -r requirements.txt` or install from your app’s `pyproject.toml` |
| `use BitmeshAI\BitmeshClient` | `from bitmesh_ai import BitmeshClient` |

**1. Virtual environment (recommended)**

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
```

**2. Install the SDK**

- **From PyPI** (once this package is published):

  ```bash
  pip install bitmesh-python-sdk
  ```

  In **`requirements.txt`**:

  ```text
  bitmesh-python-sdk>=0.1.0
  ```

  In a **`pyproject.toml`** dependencies list (PEP 621 / Poetry / Hatch, etc.):

  ```toml
  dependencies = [
    "bitmesh-python-sdk>=0.1.0",
  ]
  ```

- **From Git** (no PyPI release yet, or you need a specific revision):

  ```bash
  pip install "git+https://github.com/bitmeshai/bitmesh-python-sdk.git"
  ```

  Pin a tag or commit by appending `@v0.1.0` or `@abc1234` to the URL.

- **From a local clone** (development or monorepo):

  ```bash
  pip install /path/to/bitmesh-python-sdk
  pip install -e /path/to/bitmesh-python-sdk   # editable install
  ```

**3. Use in code**

Pass OAuth consumer key and secret from your config or environment (do not hardcode secrets in the repo).

```python
from bitmesh_ai import BitmeshClient

client = BitmeshClient(key, secret, timeout_seconds=120)
response = client.chat({...})
```

**4. Credentials**

Use environment variables, a secrets manager, or your framework’s settings—not committed files. Example:

```bash
export BITMESH_CONSUMER_KEY="your-oauth-consumer-key"
export BITMESH_CONSUMER_SECRET="your-oauth-consumer-secret"
```

---

## Requirements

- Python **3.10+**
- Runtime dependency: **`requests`** (installed automatically with this package).

---

## Installation (from this repository)

When developing the SDK itself, install from the repo root:

```bash
pip install .
# or editable with dev tools (pytest, etc.)
pip install -e ".[dev]"
```

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
