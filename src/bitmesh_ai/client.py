"""Minimal Bitmesh AI API client matching the PHP ``BitmeshAI\\BitmeshClient`` behavior."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qsl, quote, urlparse, urlencode

import requests

from bitmesh_ai.errors import BitmeshError

BASE_URL = "https://api.bitmesh.ai"


def _file_is_readable(path: Path) -> bool:
    """Readable check compatible with Python 3.10 (``Path.is_readable`` is 3.11+)."""
    return path.is_file() and os.access(path, os.R_OK)


def _php_style_parse_query(query: str) -> dict[str, str]:
    """Merge query keys like PHP ``parse_str`` (last duplicate wins)."""
    merged: dict[str, str] = {}
    if not query:
        return merged
    for key, value in parse_qsl(query, keep_blank_values=True):
        merged[key] = value
    return merged


def flatten_multipart_fields(fields: Any, prefix: str = "") -> dict[str, Any]:
    """Flatten nested dict/list structures into PHP-style bracket field names."""
    flattened: dict[str, Any] = {}
    if isinstance(fields, dict):
        items = fields.items()
    elif isinstance(fields, list):
        items = enumerate(fields)
    else:
        raise TypeError("multipart fields must be a dict or list at the root")

    for key, value in items:
        field_name = str(key) if prefix == "" else f"{prefix}[{key}]"
        if isinstance(value, (dict, list)):
            flattened.update(flatten_multipart_fields(value, field_name))
        else:
            flattened[field_name] = value
    return flattened


def generate_oauth_signature(method: str, url: str, params: dict[str, str], consumer_secret: str) -> str:
    """OAuth 1.0 HMAC-SHA1 signature (same construction as the PHP client)."""
    parsed = urlparse(url)
    if not parsed.hostname:
        raise BitmeshError("Invalid URL for OAuth signature generation.")

    scheme = parsed.scheme or "http"
    host = parsed.hostname
    port = parsed.port
    path = parsed.path.lstrip("/") if parsed.path else ""

    normalized_url = f"{scheme}://{host}"
    if (scheme == "http" and port is not None and port != 80) or (
        scheme == "https" and port is not None and port != 443
    ):
        normalized_url += f":{port}"
    normalized_url += f"/{path}"

    query_params: dict[str, str] = {}
    if parsed.query:
        query_params = _php_style_parse_query(parsed.query)

    all_params = {**params, **query_params}
    all_params.pop("oauth_signature", None)

    normalized_pairs: list[str] = []
    for key in sorted(all_params.keys()):
        raw_key = str(key)
        raw_value = str(all_params[key])
        normalized_pairs.append(f"{quote(raw_key, safe='')}={quote(raw_value, safe='')}")

    signature_base_string = "&".join(
        [
            quote(method.upper(), safe=""),
            quote(normalized_url, safe=""),
            quote("&".join(normalized_pairs), safe=""),
        ]
    )

    signing_key = f"{quote(str(consumer_secret), safe='')}&"
    digest = hmac.new(
        signing_key.encode("utf-8"),
        signature_base_string.encode("utf-8"),
        hashlib.sha1,
    ).digest()
    return base64.b64encode(digest).decode("ascii")


class BitmeshClient:
    """Bitmesh API client: OAuth 1.0 signing, JSON, GET, and multipart endpoints."""

    def __init__(
        self,
        key: str,
        secret: str,
        timeout_seconds: int = 30,
        base_url: str | None = None,
    ) -> None:
        self._key = key
        self._secret = secret
        self._timeout = float(timeout_seconds)
        self._base_url = (base_url or BASE_URL).rstrip("/")

    def chat(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._send_signed_json_request("POST", "/chat", dict(payload))

    def image(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._send_signed_json_request("POST", "/image", dict(payload))

    def video(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._send_signed_json_request("POST", "/video", dict(payload))

    def get_video(self, job_id: str, query: Mapping[str, Any] | None = None) -> dict[str, Any]:
        job_id = job_id.strip()
        if job_id == "":
            raise BitmeshError("Video job id is required.")
        return self._send_signed_get_request(f"video/{quote(job_id, safe='')}", dict(query or {}))

    def transcribe_file(self, audio_file_path: str | Path, fields: Mapping[str, Any] | None = None) -> dict[str, Any]:
        path = Path(audio_file_path)
        if not _file_is_readable(path):
            raise BitmeshError(f"Audio file does not exist or is not readable: {audio_file_path}")
        return self._send_signed_multipart_request("POST", "/transcribe-recorded", path, dict(fields or {}))

    def get_transcribe_recorded(self, job_id: str, query: Mapping[str, Any] | None = None) -> dict[str, Any]:
        job_id = job_id.strip()
        if job_id == "":
            raise BitmeshError("Transcription job id is required.")
        return self._send_signed_get_request(
            f"transcribe-recorded/{quote(job_id, safe='')}", dict(query or {})
        )

    def tools_general_background_removal(self, fields: Mapping[str, Any], image_path: str | Path) -> dict[str, Any]:
        return self._send_signed_tool_multipart_request(
            "/tools/general/background-removal",
            dict(fields),
            {"image": str(image_path)},
        )

    def tools_portrait_try_on_clothes(
        self,
        fields: Mapping[str, Any],
        files: Mapping[str, str | Path],
    ) -> dict[str, Any]:
        as_paths = {k: str(v) for k, v in files.items()}
        return self._send_signed_tool_multipart_request("/tools/portrait/try-on-clothes", dict(fields), as_paths)

    def tools_query_async_task_result(self, task_id: str) -> dict[str, Any]:
        task_id = task_id.strip()
        if task_id == "":
            raise BitmeshError("Task id is required.")
        return self._send_signed_json_request(
            "POST",
            "/tools/query-async-task-result",
            {"task_id": task_id},
        )

    def get_tools_result(self, path: str) -> bytes:
        rel = path.lstrip("/")
        if rel == "":
            raise BitmeshError("Tools result path is required.")
        return self._send_unsigned_get_request(f"tools-result/{rel}")

    # --- internals ---

    def _build_url(self, path: str) -> str:
        return f"{self._base_url}/{path.lstrip('/')}"

    def _encode_json(self, payload: dict[str, Any]) -> str:
        try:
            return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise BitmeshError("Failed to encode request payload to JSON.") from exc

    def _decode_json_response(self, body: str) -> dict[str, Any]:
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise BitmeshError("Bitmesh API returned a non-JSON or invalid JSON response.") from exc
        if not isinstance(data, dict):
            raise BitmeshError("Bitmesh API returned a non-JSON or invalid JSON response.")
        return data

    def _generate_oauth_params(self, method: str, url: str) -> dict[str, str]:
        params: dict[str, str] = {
            "oauth_consumer_key": self._key,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_nonce": secrets.token_hex(16),
            "oauth_version": "1.0",
        }
        params["oauth_signature"] = generate_oauth_signature(method, url, params, self._secret)
        return params

    def _authorization_header(self, oauth_params: dict[str, str]) -> str:
        parts: list[str] = []
        for key, value in oauth_params.items():
            if key.startswith("oauth_"):
                parts.append(f'{quote(str(key), safe="")}="{quote(str(value), safe="")}"')
        return f"OAuth {', '.join(parts)}"

    def _payload_signature(self, request_body: str, oauth_signature: str) -> str:
        digest = hashlib.sha256(
            (request_body + self._key + oauth_signature).encode("utf-8")
        ).hexdigest()
        return digest

    def _multipart_payload_signature(self, non_file_fields: dict[str, Any], oauth_signature: str) -> str:
        sorted_keys = sorted(non_file_fields.keys())
        sorted_fields = {k: non_file_fields[k] for k in sorted_keys}
        try:
            canonical = json.dumps(sorted_fields, ensure_ascii=False, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise BitmeshError("Failed to encode multipart fields for payload signature.") from exc
        return hashlib.sha256((canonical + self._key + oauth_signature).encode("utf-8")).hexdigest()

    def _raise_for_status(self, response: requests.Response) -> None:
        if 200 <= response.status_code < 300:
            return
        text = response.text if response.text is not None else ""
        raise BitmeshError(
            f"Bitmesh API request failed with status {response.status_code}: {text}"
        )

    def _send_signed_json_request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self._build_url(path)
        json_body = self._encode_json(payload)
        oauth_params = self._generate_oauth_params(method, url)
        oauth_signature = oauth_params.get("oauth_signature", "")

        headers = {
            "Authorization": self._authorization_header(oauth_params),
            "X-Payload-Signature": self._payload_signature(json_body, oauth_signature),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.request(
                method.upper(),
                url,
                data=json_body.encode("utf-8"),
                headers=headers,
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise BitmeshError(f"Bitmesh request failed: {exc}") from exc

        self._raise_for_status(resp)
        return self._decode_json_response(resp.text)

    def _send_signed_get_request(self, path: str, query: dict[str, Any]) -> dict[str, Any]:
        path = path.lstrip("/")
        suffix = "" if not query else "?" + urlencode(query, quote_via=quote, doseq=True)
        url = self._build_url(path + suffix)

        oauth_params = self._generate_oauth_params("GET", url)
        oauth_signature = oauth_params.get("oauth_signature", "")

        headers = {
            "Authorization": self._authorization_header(oauth_params),
            "X-Payload-Signature": self._payload_signature("", oauth_signature),
            "Accept": "application/json",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=self._timeout)
        except requests.RequestException as exc:
            raise BitmeshError(f"Bitmesh request failed: {exc}") from exc

        self._raise_for_status(resp)
        return self._decode_json_response(resp.text)

    def _send_unsigned_get_request(self, path: str) -> bytes:
        url = self._build_url(path)
        try:
            resp = requests.get(url, timeout=self._timeout)
        except requests.RequestException as exc:
            raise BitmeshError(f"Bitmesh request failed: {exc}") from exc

        self._raise_for_status(resp)
        return resp.content

    def _validate_tool_files(self, files: dict[str, str]) -> None:
        for field_name, file_path in files.items():
            path = Path(file_path)
            if not _file_is_readable(path):
                raise BitmeshError(
                    f'File does not exist or is not readable for field "{field_name}": {file_path}'
                )

    def _send_signed_tool_multipart_request(
        self,
        path: str,
        fields: dict[str, Any],
        files: dict[str, str],
    ) -> dict[str, Any]:
        self._validate_tool_files(files)
        url = self._build_url(path)
        oauth_params = self._generate_oauth_params("POST", url)
        oauth_signature = oauth_params.get("oauth_signature", "")

        headers = {
            "Authorization": self._authorization_header(oauth_params),
            "X-Payload-Signature": self._multipart_payload_signature(fields, oauth_signature),
            "Accept": "application/json",
        }

        data = flatten_multipart_fields(fields)
        open_files: list[tuple[Any, Any]] = []
        try:
            multipart_files: list[tuple[str, tuple[str, Any]]] = []
            for field_name, file_path in files.items():
                fh = open(file_path, "rb")
                open_files.append((field_name, fh))
                multipart_files.append((field_name, (Path(file_path).name, fh)))

            try:
                resp = requests.post(
                    url,
                    headers=headers,
                    data=data,
                    files=multipart_files,
                    timeout=self._timeout,
                )
            finally:
                for _, fh in open_files:
                    fh.close()
        except OSError as exc:
            raise BitmeshError(f"Bitmesh request failed: {exc}") from exc
        except requests.RequestException as exc:
            raise BitmeshError(f"Bitmesh request failed: {exc}") from exc

        self._raise_for_status(resp)
        return self._decode_json_response(resp.text)

    def _send_signed_multipart_request(
        self,
        method: str,
        path: str,
        audio_path: Path,
        fields: dict[str, Any],
    ) -> dict[str, Any]:
        url = self._build_url(path)
        oauth_params = self._generate_oauth_params(method, url)
        oauth_signature = oauth_params.get("oauth_signature", "")

        headers = {
            "Authorization": self._authorization_header(oauth_params),
            "X-Payload-Signature": self._multipart_payload_signature(fields, oauth_signature),
            "Accept": "application/json",
        }

        data = flatten_multipart_fields(fields)
        try:
            with open(audio_path, "rb") as audio_fh:
                files = {"audio": (audio_path.name, audio_fh)}
                try:
                    resp = requests.request(
                        method.upper(),
                        url,
                        headers=headers,
                        data=data,
                        files=files,
                        timeout=self._timeout,
                    )
                except requests.RequestException as exc:
                    raise BitmeshError(f"Bitmesh request failed: {exc}") from exc
        except OSError as exc:
            raise BitmeshError(f"Bitmesh request failed: {exc}") from exc

        self._raise_for_status(resp)
        return self._decode_json_response(resp.text)
