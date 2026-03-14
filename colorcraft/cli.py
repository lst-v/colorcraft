import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from .converter import ColoringPageConverter
from .backends import BACKENDS

SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}


def _age_to_tier(age: int) -> str:
    if age <= 3:
        return "toddler"
    elif age <= 5:
        return "preschool"
    else:
        return "school"


def main():
    parser = argparse.ArgumentParser(
        description="Convert images to printable coloring pages for kids."
    )
    parser.add_argument("input", nargs="?", help="Input image file (PNG, JPG, JPEG, BMP, TIFF)")
    parser.add_argument(
        "-o", "--output", help="Output file path (default: <input>_coloring.png)"
    )
    parser.add_argument(
        "-m",
        "--method",
        choices=list(BACKENDS),
        default="openai",
        help="Edge detection method (default: openai)",
    )
    parser.add_argument(
        "--download",
        metavar="METHOD",
        help="Download model files for METHOD and exit (e.g. --download hed)",
    )
    parser.add_argument(
        "--edge-threshold",
        type=int,
        default=128,
        help="HED edge threshold 0-255 (default: 128)",
    )
    parser.add_argument(
        "-t",
        "--threshold-low",
        type=int,
        default=50,
        help="Canny low threshold (default: 50)",
    )
    parser.add_argument(
        "-T",
        "--threshold-high",
        type=int,
        default=150,
        help="Canny high threshold (default: 150)",
    )
    parser.add_argument(
        "-b", "--blur", type=int, default=5, help="Gaussian blur kernel size (default: 5)"
    )
    parser.add_argument(
        "-l",
        "--line-thickness",
        type=int,
        default=2,
        help="Line thickness 1-5 (default: 2)",
    )
    parser.add_argument(
        "--api-key",
        help="API key (for stability: STABILITY_API_KEY, for openai: OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--control-strength",
        type=float,
        default=0.7,
        help="Stability control strength 0.0-1.0 (default: 0.7)",
    )
    parser.add_argument(
        "--age",
        type=int,
        metavar="YEARS",
        help="Child's age — adjusts complexity (2-3: toddler, 4-5: preschool, 6+: school-age)",
    )
    parser.add_argument(
        "--prompt",
        help="Custom prompt for AI generation (overrides --age)",
    )
    parser.add_argument(
        "--openai-model",
        default="gpt-image-1.5",
        help="OpenAI image model (default: gpt-image-1.5)",
    )

    args = parser.parse_args()

    # Handle --download
    if args.download:
        from .models.downloader import download_model

        try:
            download_model(args.download)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        sys.exit(0)

    # input is required for conversion
    if not args.input:
        parser.error("the following arguments are required: input")

    # Validate input file — fall back to input/ directory
    input_path = Path(args.input)
    if not input_path.exists():
        input_fallback = Path(__file__).resolve().parent.parent / "input" / args.input
        if input_fallback.exists():
            input_path = input_fallback
        else:
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

    if input_path.suffix.lower() not in SUPPORTED_FORMATS:
        print(
            f"Error: Unsupported format. Supported: {', '.join(SUPPORTED_FORMATS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Generate output path if not specified
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    if args.output:
        output_path = args.output
    else:
        output_path = str(output_dir / f"{input_path.stem}_coloring.png")

    # Build backend kwargs based on method
    backend_kwargs = {}
    if args.method == "canny":
        backend_kwargs = {
            "threshold_low": args.threshold_low,
            "threshold_high": args.threshold_high,
            "blur_kernel": args.blur,
        }
    elif args.method == "hed":
        backend_kwargs = {"edge_threshold": args.edge_threshold}
    elif args.method == "stability":
        from .backends.stability import AGE_PROMPTS as STABILITY_AGE_PROMPTS

        backend_kwargs = {
            "control_strength": args.control_strength,
        }
        if args.api_key:
            backend_kwargs["api_key"] = args.api_key
        if args.prompt:
            backend_kwargs["prompt"] = args.prompt
        elif args.age is not None:
            backend_kwargs["prompt"] = STABILITY_AGE_PROMPTS[_age_to_tier(args.age)]
    elif args.method == "openai":
        from .backends.openai import AGE_PROMPTS as OPENAI_AGE_PROMPTS

        backend_kwargs = {"model": args.openai_model}
        if args.api_key:
            backend_kwargs["api_key"] = args.api_key
        if args.prompt:
            backend_kwargs["prompt"] = args.prompt
        elif args.age is not None:
            backend_kwargs["prompt"] = OPENAI_AGE_PROMPTS[_age_to_tier(args.age)]

    # Convert
    converter = ColoringPageConverter(
        method=args.method,
        line_thickness=args.line_thickness,
        **backend_kwargs,
    )

    try:
        print(f"Converting {args.input} (method: {args.method})...")
        result = converter.convert(str(input_path))
        converter.save(result, output_path)
        print(f"Saved coloring page to: {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
