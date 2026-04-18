# colorcraft

Convert images into printable coloring pages for kids.

Supports multiple backends — from local edge detection (Canny, HED) to AI-powered generation (OpenAI, Stability AI).

## Installation

Requires [uv](https://docs.astral.sh/uv/):

```bash
uv sync --extra stability
```

Or use the `run.sh` wrapper, which handles installation automatically:

```bash
./run.sh photo.jpg -m canny
```

> **Note:** Always use `./run.sh` instead of calling `colorcraft` directly. The bare `colorcraft` command may point to a stale system-level install that lacks the required dependencies.

## Usage

```bash
./run.sh <input-image> [options]
```

### Basic examples

```bash
# Using OpenAI (default requires OPENAI_API_KEY)
./run.sh photo.jpg -m openai

# Adjust complexity for a toddler (ages 2-3: very simple, chunky outlines)
./run.sh photo.jpg -m openai --age 2

# For a school-age child (ages 6+: more detail)
./run.sh photo.jpg -m openai --age 7

# HEIC/HEIF photos (e.g. straight from iPhone) are supported natively
./run.sh photo.HEIC -m openai --age 6

# Using Stability AI (requires STABILITY_API_KEY)
./run.sh photo.jpg -m stability

# Using local Canny edge detection (no API key needed)
./run.sh photo.jpg -m canny

# Using HED edge detection (downloads model on first run)
./run.sh photo.jpg -m hed
```

Output is saved to the `output/` directory by default. Use `-o` to specify a custom path:

```bash
./run.sh photo.jpg -m openai -o my_coloring_page.png
```

### Options

| Flag | Description | Default |
|---|---|---|
| `-m`, `--method` | Backend: `canny`, `hed`, `openai`, `stability` | `stability` |
| `-o`, `--output` | Output file path | `output/<name>_coloring.png` |
| `-l`, `--line-thickness` | Line thickness 1-5 | `2` |
| `--age` | Child's age in years — adjusts complexity (2-3: toddler, 4-5: preschool, 6+: school-age) | — |
| `--api-key` | API key (alternative to env var) | — |
| `--prompt` | Custom prompt for AI backends (overrides `--age`) | — |
| `--openai-model` | OpenAI image model | `gpt-image-1.5` |
| `--control-strength` | Stability control strength 0.0-1.0 | `0.7` |
| `-t`, `--threshold-low` | Canny low threshold | `50` |
| `-T`, `--threshold-high` | Canny high threshold | `150` |
| `-b`, `--blur` | Gaussian blur kernel size | `5` |
| `--edge-threshold` | HED edge threshold 0-255 | `128` |
| `--download METHOD` | Download model files (e.g. `hed`) and exit | — |

### Environment variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=sk-...
```

## Backends

### OpenAI (`-m openai`)

Uses OpenAI's image editing API to generate coloring pages. Defaults to `gpt-image-1.5` which produces the most faithful line art. Use `--openai-model` to pick a different model:

```bash
# Default (best quality)
./run.sh photo.jpg -m openai

# Use gpt-image-1 (cheaper)
./run.sh photo.jpg -m openai --openai-model gpt-image-1

# Use the mini variant (fastest, cheapest)
./run.sh photo.jpg -m openai --openai-model gpt-image-1-mini
```

Available models: `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`.

### Stability AI (`-m stability`)

Uses Stability AI's sketch control endpoint for image-to-coloring conversion with controllable strength.

### Canny (`-m canny`)

Local edge detection using OpenCV's Canny algorithm. Fast, free, no API key needed. Best for images with clear edges.

### HED (`-m hed`)

Holistically-Nested Edge Detection using a deep learning model. Produces smoother edges than Canny. Requires a one-time model download:

```bash
./run.sh --download hed
```

## Supported formats

PNG, JPG, JPEG, BMP, TIFF, HEIC, HEIF, AVIF

HEIC/HEIF files (e.g. photos taken on iPhone) are converted automatically — no manual pre-conversion needed.

## License

[MIT](LICENSE)
