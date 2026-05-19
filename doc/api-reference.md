# Bitmesh Python SDK — API Reference

Reference for `bitmesh_ai.BitmeshClient`. All requests use the fixed host **`https://api.bitmesh.ai`** unless you pass a different `base_url` to the constructor (primarily for tests).

- **Module**: `bitmesh_ai`
- **Class**: `BitmeshClient`
- **Requirements**: Python 3.10+, dependency on `requests`.
- **Authentication (signed requests)**: OAuth 1.0 one-legged (`Authorization: OAuth ...`, HMAC-SHA1). JSON and GET bodies use **`X-Payload-Signature`**: SHA-256 of `body + consumerKey + oauthSignature` (empty string body for GET). Multipart requests sign a canonical JSON encoding of **non-file** fields only (top-level keys sorted, same as the PHP SDK), same header name.
- **Unsigned**: `get_tools_result()` calls `GET .../tools-result/...` without OAuth (public asset fetch).

On failure the client raises **`BitmeshError`** (`RuntimeError` subclass): HTTP status and body text, transport errors, missing files, invalid JSON, or validation errors such as empty id/path.

---

## Constructor

### `BitmeshClient(key, secret, timeout_seconds=30, base_url=None)`

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | `str` | OAuth consumer key |
| `secret` | `str` | OAuth consumer secret |
| `timeout_seconds` | `int` | Request timeout in seconds (default `30`) |
| `base_url` | `str \| None` | Override API origin for testing (default `https://api.bitmesh.ai`) |

---

## `chat(payload) -> dict`

- **HTTP**: `POST /chat` with `Content-Type: application/json`
- **Description**: Chat completions. Pass the **exact JSON body** the API expects (e.g. `model`, `messages`, `max_tokens`, `temperature`, …). If your API key is bound to a fixed model, omit `model` in the payload (the server may reject a conflicting `model` field).
- **Returns**: Parsed JSON **object** (`dict`).

---

## `image(payload) -> dict`

- **HTTP**: `POST /image` (`application/json`)
- **Description**: Image generation. Payload fields depend on the provider (e.g. `prompt`, `model`, `reference_images`, dimensions, …).

---

## `video(payload) -> dict`

- **HTTP**: `POST /video` (`application/json`)
- **Description**: Video generation. Typical keys include `prompt`, `model`, `frame_images`, etc. The response shape is provider-specific (often includes `id` for a job to poll).

---

## `get_video(id, query=None) -> dict`

- **HTTP**: `GET /video/{id}` (`id` is URL-encoded; optional `query` merged into the query string)
- **Description**: Poll video generation job status or retrieve result metadata. Empty or whitespace-only `id` raises **`BitmeshError`**.

---

## `transcribe_file(audio_file_path, fields=None) -> dict`

- **HTTP**: `POST /transcribe-recorded` (`multipart/form-data`)
- **Description**: Upload a local audio file. The file is sent as the **`audio`** part. `fields` are non-file form fields (e.g. `speech_models` as nested lists are flattened for multipart and included in the payload signature). The file must exist and be readable.
- **Returns**: JSON response (e.g. often includes `id` for the transcript job).

---

## `get_transcribe_recorded(id, query=None) -> dict`

- **HTTP**: `GET /transcribe-recorded/{id}` (`id` is URL-encoded; optional `query` merged into the query string)
- **Description**: Poll transcription job status or fetch result. Empty or whitespace-only `id` raises **`BitmeshError`**.

---

## `tools_general_background_removal(fields, image_path) -> dict`

- **HTTP**: `POST /tools/general/background-removal` (multipart)
- **Description**: Background removal. **`image`** is taken from `image_path`. Other tool options go in `fields` (e.g. `return_form` = `mask` \| `whiteBK` \| `crop`). File must exist and be readable.

---

## `tools_portrait_try_on_clothes(fields, files) -> dict`

- **HTTP**: `POST /tools/portrait/try-on-clothes` (multipart)
- **Description**: Virtual try-on. `files` maps **field name → path** (e.g. `person_image`, `top_garment`, `bottom_garment`). `fields` may include `task_type`, `resolution`, `restore_face`, etc. Every path must be a readable file.

---

## `tools_query_async_task_result(task_id) -> dict`

- **HTTP**: `POST /tools/query-async-task-result` (`application/json` body `{"task_id":"..."}`)
- **Description**: Poll an async tools task. Empty `task_id` raises **`BitmeshError`**.

---

## `get_tools_result(path) -> bytes`

- **HTTP**: `GET /tools-result/{path}` (path segments after `tools-result/`)
- **Description**: Download raw bytes for a proxied tool result (often an image). **No** OAuth or payload signature. Pass the path relative to `tools-result/` (leading slashes are normalized). Empty path raises **`BitmeshError`**. Returns **`bytes`**.

---

## Notes

- **Success criteria**: HTTP status must be 2xx; JSON endpoints must decode to a JSON **object** (`dict`), not a bare list/string/number at the top level.
- **Rate limits**: The API may throttle; the client does not retry automatically.

For runnable snippets, see [code-examples.md](code-examples.md).
