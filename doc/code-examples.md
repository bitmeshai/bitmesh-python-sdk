# Code Examples

Examples for `bitmesh_ai.BitmeshClient`. The client always calls **`https://api.bitmesh.ai`**. Each method mirrors the HTTP API: you pass **payload dicts** (or file paths) that match the server contract. See [api-reference.md](api-reference.md) for behavior and errors.

```python
from bitmesh_ai import BitmeshClient

consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"

# Third argument: timeout in seconds (default 30)
client = BitmeshClient(consumer_key, consumer_secret, timeout_seconds=120)
```

---

## Chat

Send a JSON body as documented for `POST /chat`:

```python
response = client.chat(
    {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Reply with exactly: ok"},
        ],
        "max_tokens": 32,
        "temperature": 0,
    }
)

content = response["choices"][0]["message"]["content"]
print(content)
```

If your key uses a **fixed default model**, omit `model` so the server does not reject the request:

```python
response = client.chat(
    {
        "messages": [
            {"role": "user", "content": "Hello"},
        ],
    }
)
```

Vision-style content is expressed in the payload as the API expects (nested `content` lists with `image_url`, etc.):

```python
response = client.chat(
    {
        "model": "google/gemma-3n-e4b-it",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://placecats.com/600/400"},
                    },
                ],
            },
        ],
        "max_tokens": 256,
    }
)
```

---

## Image

```python
response = client.image(
    {
        "prompt": "A red bicycle by a canal",
        "model": "wan-ai/wan2.6-image",
        "reference_images": [
            "https://placecats.com/800/600",
        ],
    }
)

job_or_data = response  # shape depends on provider; often includes `id`
```

---

## Video

```python
response = client.video(
    {
        "prompt": "Short cinematic scene",
        "model": "bytedance/seedance-1.0-lite",
        "frame_images": [
            {
                "input_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200",
                "frame": 0,
            },
        ],
    }
)

job_id = response.get("id")
```

Poll job status (`GET /video/{id}`) using the returned `id`:

```python
video_id = str(response.get("id") or "")
if video_id:
    status = client.get_video(
        video_id,
        {
            # optional query params if supported (e.g. test)
        },
    )
    print(status.get("status"))
```

---

## Transcription (upload + poll)

Submit a local file (`POST /transcribe-recorded`):

```python
response = client.transcribe_file(
    "/path/to/recording.mp3",
    {"speech_models": ["universal-2"]},
)

transcript_id = response.get("id")
```

Poll status or result (`GET /transcribe-recorded/{id}`):

```python
status = client.get_transcribe_recorded(
    str(transcript_id),
    {
        # optional query params, e.g. test flags if supported
    },
)

print(status.get("status", "unknown"))
```

---

## Tools – background removal + download result

```python
result = client.tools_general_background_removal(
    {"return_form": "mask"},
    "/path/to/input.png",
)

image_url = (result.get("data") or {}).get("image_url")

from urllib.parse import urlparse

path = urlparse(str(image_url)).path or ""
prefix = "/tools-result/"
relative = path.split(prefix, 1)[1].lstrip("/") if prefix in path else ""

bytes_out = client.get_tools_result(relative)
with open("/tmp/mask.png", "wb") as fh:
    fh.write(bytes_out)
```

---

## Tools – try-on (async) + query task

Async try-on returns a ``task_id``. **Poll** with ``tools_query_async_task_result(task_id)`` until ``status``
indicates completion (or an image URL appears). A single call is often not enough while the job is still running.

```python
try_on = client.tools_portrait_try_on_clothes(
    {
        "task_type": "async",
        "resolution": "-1",
        "restore_face": "true",
    },
    {
        "person_image": "/path/to/person.png",
        "top_garment": "/path/to/top.png",
        "bottom_garment": "/path/to/bottom.png",
    },
)

task_id = str(try_on.get("task_id") or "")

import time

while True:
    query = client.tools_query_async_task_result(task_id)
    status = str(query.get("status", "")).lower()
    if status in ("success", "failed", "error", "completed"):
        break
    if isinstance(query.get("data"), dict) and (query["data"].get("image_url")):
        break
    time.sleep(3)

print(query)
```

If the result includes ``data["image_url"]`` pointing at ``/tools-result/...``, download the bytes with
``get_tools_result()`` (see **Tools – background removal** above for stripping the path). Run
``examples/tryon_example.py`` to submit, then ``examples/tryon_poll_example.py <task_id>`` to poll (and
optionally set ``BITMESH_TRYON_OUTPUT`` for the saved image).

---

## Error handling

```python
from bitmesh_ai import BitmeshClient, BitmeshError

client = BitmeshClient("key", "secret")

try:
    out = client.chat({"messages": [{"role": "user", "content": "Hi"}]})
except BitmeshError as exc:
    print(exc)
```
