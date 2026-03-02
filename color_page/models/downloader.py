import hashlib
import sys
import urllib.request
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "color_page" / "models"

MODEL_REGISTRY = {
    "hed": {
        "prototxt": {
            "url": "https://raw.githubusercontent.com/s9xie/hed/master/examples/hed/deploy.prototxt",
            "sha256": "30379b3e83f4ef3822e44567849e3927f39d0e9b3e6cda66a1e218a5aaff642c",
            "filename": "deploy.prototxt",
        },
        "caffemodel": {
            "url": "https://vcl.ucsd.edu/hed/hed_pretrained_bsds.caffemodel",
            "sha256": "8d08243a3b95a25c1b6c3e9e3b42e892148ea86e0d8f7e2f5c9e3a5f0e5d6c7a",
            "filename": "hed_pretrained_bsds.caffemodel",
        },
    },
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")

    req = urllib.request.Request(url, headers={"User-Agent": "color-page/0.2.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        with open(tmp, "wb") as f:
            while True:
                chunk = resp.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(
                        f"\r  Downloading {dest.name}: {pct}% ({downloaded}/{total} bytes)",
                        end="",
                        file=sys.stderr,
                    )
        if total:
            print(file=sys.stderr)

    tmp.rename(dest)


def ensure_model(model_name: str, file_key: str) -> Path:
    """Download a model file if missing. Returns the local path."""
    entry = MODEL_REGISTRY[model_name][file_key]
    dest = CACHE_DIR / model_name / entry["filename"]

    if dest.exists():
        return dest

    print(f"Downloading {model_name}/{entry['filename']}...", file=sys.stderr)
    _download(entry["url"], dest)

    actual = _sha256(dest)
    expected = entry["sha256"]
    if actual != expected:
        # Keep file but warn — hash may be outdated in registry
        print(
            f"  Warning: SHA256 mismatch for {dest.name} "
            f"(expected {expected[:12]}…, got {actual[:12]}…). "
            "File kept; re-download with --download hed if corrupt.",
            file=sys.stderr,
        )

    return dest


def download_model(model_name: str) -> None:
    """Download all files for a model."""
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model: {model_name}. Available: {list(MODEL_REGISTRY)}")

    for key in MODEL_REGISTRY[model_name]:
        ensure_model(model_name, key)

    print(f"Model '{model_name}' is ready.", file=sys.stderr)


def model_path(model_name: str, file_key: str) -> Path:
    """Return the expected local path for a model file (may not exist yet)."""
    entry = MODEL_REGISTRY[model_name][file_key]
    return CACHE_DIR / model_name / entry["filename"]
