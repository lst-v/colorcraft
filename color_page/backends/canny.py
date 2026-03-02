import cv2
import numpy as np

from .base import EdgeDetectionBackend


class CannyBackend(EdgeDetectionBackend):
    def __init__(
        self,
        threshold_low: int = 50,
        threshold_high: int = 150,
        blur_kernel: int = 5,
    ):
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.blur_kernel = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1

    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bilateral = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        blurred = cv2.GaussianBlur(
            bilateral, (self.blur_kernel, self.blur_kernel), 0
        )
        edges = cv2.Canny(blurred, self.threshold_low, self.threshold_high)
        return edges

    def is_available(self) -> bool:
        return True
