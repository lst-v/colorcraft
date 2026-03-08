from __future__ import annotations

import base64
import json
import os
import urllib.request
from uuid import uuid4

import cv2
import numpy as np

from .base import EdgeDetectionBackend

DEFAULT_PROMPT = (
    "Convert this image into a simple coloring book page for young children. "
    "Keep the main subject and its overall shape, but drastically simplify the details — "
    "remove small features, textures, repetitive patterns, and background clutter. "
    "Use only bold, clean black outlines on a pure white background. "
    "Leave large empty white areas inside shapes so they are easy to color in. "
    "No shading, no gradients, no gray tones, no filled areas, no solid black regions. "
    "Do NOT add, remove, or reposition the main objects — keep the composition, just simplify the lines. "
    "Think of a coloring page for a 4-year-old: fewer lines, bigger shapes, lots of white space."
)


class OpenAIBackend(EdgeDetectionBackend):
    skip_postprocess = True

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-image-1.5",
        prompt: str | None = None,
        quality: str = "high",
        size: str = "auto",
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Pass api_key= or set OPENAI_API_KEY env var."
            )
        self.model = model
        self.prompt = prompt or DEFAULT_PROMPT
        self.quality = quality
        self.size = size

    def is_available(self) -> bool:
        return bool(self.api_key)

    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        success, png_buf = cv2.imencode(".png", image)
        if not success:
            raise RuntimeError("Failed to encode image to PNG")
        png_bytes = png_buf.tobytes()

        boundary = uuid4().hex
        body = _build_multipart(
            boundary,
            fields={
                "model": self.model,
                "prompt": self.prompt,
                "quality": self.quality,
                "size": self.size,
            },
            file_field="image[]",
            file_name="input.png",
            file_bytes=png_bytes,
            file_content_type="image/png",
        )

        url = "https://api.openai.com/v1/images/edits"
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "colorcraft/0.3.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                resp_body = resp.read()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(error_body)
            except json.JSONDecodeError:
                detail = error_body
            raise RuntimeError(
                f"OpenAI API error {e.code}: {detail}"
            ) from e

        data = json.loads(resp_body)
        b64_image = data["data"][0]["b64_json"]
        image_bytes = base64.b64decode(b64_image)

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError("Failed to decode OpenAI API response as image")
        return img


def _build_multipart(
    boundary: str,
    fields: dict[str, str],
    file_field: str,
    file_name: str,
    file_bytes: bytes,
    file_content_type: str,
) -> bytes:
    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n".encode()
        )
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_name}"\r\n'
        f"Content-Type: {file_content_type}\r\n\r\n".encode()
        + file_bytes
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts)
