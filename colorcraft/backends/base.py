from abc import ABC, abstractmethod

import numpy as np


class EdgeDetectionBackend(ABC):
    skip_postprocess: bool = False

    @abstractmethod
    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        """Take a BGR image and return a single-channel edge map (white edges on black)."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this backend is ready to use."""
