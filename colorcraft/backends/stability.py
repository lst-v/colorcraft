from __future__ import annotations

import json
import os
import urllib.request
from uuid import uuid4

import cv2
import numpy as np

from .base import EdgeDetectionBackend

AGE_PROMPTS = {
    "toddler": (
        "Extremely simple coloring book page for toddlers ages 2-3, "
        "only very thick bold black outlines on pure white background, "
        "minimal detail, huge chunky shapes, no small features, "
        "no shading, no gradients, no gray tones, no filled areas, no solid black regions, "
        "pure black and white only, maximum white space"
    ),
    "preschool": (
        "Coloring book page for children, only black outlines on pure white background, "
        "no shading, no gradients, no gray tones, no filled areas, no solid black regions, "
        "every shape must be empty with clean black outlines only, "
        "pure black and white only, no off-white, no gray, "
        "high contrast line art, simple and clear"
    ),
    "school": (
        "Detailed coloring book page for school-age children ages 6 and up, "
        "clean black outlines on pure white background with moderate detail, "
        "preserve interesting features and smaller shapes, "
        "no shading, no gradients, no gray tones, no filled areas, no solid black regions, "
        "pure black and white only, high contrast line art"
    ),
}

DEFAULT_PROMPT = AGE_PROMPTS["preschool"]


class StabilityBackend(EdgeDetectionBackend):
    skip_postprocess = True

    def __init__(
        self,
        api_key: str | None = None,
        control_strength: float = 0.7,
        prompt: str | None = None,
    ):
        self.api_key = api_key or os.environ.get("STABILITY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Stability API key required. Pass api_key= or set STABILITY_API_KEY env var."
            )
        self.control_strength = control_strength
        self.prompt = prompt or DEFAULT_PROMPT

    def is_available(self) -> bool:
        return bool(self.api_key)

    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        # Encode input image to PNG bytes
        success, png_buf = cv2.imencode(".png", image)
        if not success:
            raise RuntimeError("Failed to encode image to PNG")
        png_bytes = png_buf.tobytes()

        # Build multipart/form-data request
        boundary = uuid4().hex
        body = _build_multipart(
            boundary,
            fields={
                "prompt": self.prompt,
                "control_strength": str(self.control_strength),
                "style_preset": "line-art",
                "output_format": "png",
            },
            file_field="image",
            file_name="input.png",
            file_bytes=png_bytes,
            file_content_type="image/png",
        )

        url = "https://api.stability.ai/v2beta/stable-image/control/sketch"
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "User-Agent": "colorcraft/0.3.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                resp_bytes = resp.read()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(error_body)
            except json.JSONDecodeError:
                detail = error_body
            raise RuntimeError(
                f"Stability API error {e.code}: {detail}"
            ) from e

        # Decode response PNG to grayscale numpy array
        arr = np.frombuffer(resp_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise RuntimeError("Failed to decode Stability API response as image")
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
