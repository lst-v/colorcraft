# color-page

Convert images into printable coloring pages for kids.

Supports multiple backends — from local edge detection (Canny, HED) to AI-powered generation (OpenAI, Stability AI).

## Installation

```bash
pip install -e .
```

For API-based backends, install the optional HTTP dependency:

```bash
pip install -e ".[stability]"
```

## Usage

```bash
color-page <input-image> [options]
```

### Basic examples

```bash
# Using OpenAI (default requires OPENAI_API_KEY)
color-page photo.jpg -m openai

# Using Stability AI (requires STABILITY_API_KEY)
color-page photo.jpg -m stability

# Using local Canny edge detection (no API key needed)
color-page photo.jpg -m canny

# Using HED edge detection (downloads model on first run)
color-page photo.jpg -m hed
```

Output is saved to the `output/` directory by default. Use `-o` to specify a custom path:

```bash
color-page photo.jpg -m openai -o my_coloring_page.png
```

### Options

| Flag | Description | Default |
|---|---|---|
| `-m`, `--method` | Backend: `canny`, `hed`, `openai`, `stability` | `stability` |
| `-o`, `--output` | Output file path | `output/<name>_coloring.png` |
| `-l`, `--line-thickness` | Line thickness 1-5 | `2` |
| `--api-key` | API key (alternative to env var) | — |
| `--prompt` | Custom prompt for AI backends | — |
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

Uses OpenAI's `gpt-image-1.5` model to generate coloring pages via the image editing API. Produces clean line art that closely follows the source image.

### Stability AI (`-m stability`)

Uses Stability AI's sketch control endpoint for image-to-coloring conversion with controllable strength.

### Canny (`-m canny`)

Local edge detection using OpenCV's Canny algorithm. Fast, free, no API key needed. Best for images with clear edges.

### HED (`-m hed`)

Holistically-Nested Edge Detection using a deep learning model. Produces smoother edges than Canny. Requires a one-time model download:

```bash
color-page --download hed
```

## Supported formats

PNG, JPG, JPEG, BMP, TIFF

## License

[MIT](LICENSE)
