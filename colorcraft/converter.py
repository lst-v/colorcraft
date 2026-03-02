import cv2
import numpy as np

from .backends import get_backend


class ColoringPageConverter:
    def __init__(
        self,
        method: str = "stability",
        line_thickness: int = 2,
        **backend_kwargs,
    ):
        self.backend = get_backend(method, **backend_kwargs)
        self.line_thickness = line_thickness

    def convert(self, input_path: str) -> np.ndarray:
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not load image: {input_path}")

        edges = self.backend.detect_edges(img)

        if self.backend.skip_postprocess:
            # Force pure black and white — no gray tones
            _, bw = cv2.threshold(edges, 200, 255, cv2.THRESH_BINARY)
            return bw

        # Dilate to thicken lines (kid-friendly)
        if self.line_thickness > 1:
            kernel = np.ones((self.line_thickness, self.line_thickness), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)

        # Morphological closing to connect nearby lines
        closing_kernel = np.ones((3, 3), np.uint8)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, closing_kernel)

        # Invert: white background, black lines
        coloring_page = cv2.bitwise_not(closed)

        return coloring_page

    def save(self, image: np.ndarray, output_path: str) -> None:
        cv2.imwrite(output_path, image)
