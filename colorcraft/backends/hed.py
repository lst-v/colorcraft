import cv2
import numpy as np

from .base import EdgeDetectionBackend
from ..models.downloader import ensure_model, model_path

_crop_layer_registered = False


class CropLayer:
    """Custom crop layer required by HED's prototxt."""

    def __init__(self, params, blobs):
        self.x_start = 0
        self.x_end = 0
        self.y_start = 0
        self.y_end = 0

    def getMemoryShapes(self, inputs):
        input_shape, target_shape = inputs[0], inputs[1]
        batch, channels = input_shape[0], input_shape[1]
        h, w = target_shape[2], target_shape[3]

        self.y_start = (input_shape[2] - target_shape[2]) // 2
        self.x_start = (input_shape[3] - target_shape[3]) // 2
        self.y_end = self.y_start + h
        self.x_end = self.x_start + w

        return [[batch, channels, h, w]]

    def forward(self, inputs):
        return [inputs[0][:, :, self.y_start : self.y_end, self.x_start : self.x_end]]


def _register_crop_layer():
    global _crop_layer_registered
    if not _crop_layer_registered:
        cv2.dnn_registerLayer("Crop", CropLayer)
        _crop_layer_registered = True


class HEDBackend(EdgeDetectionBackend):
    MAX_INFERENCE_DIM = 1024

    def __init__(self, edge_threshold: int = 128):
        self.edge_threshold = edge_threshold
        self._net = None

    def _load_net(self):
        if self._net is not None:
            return
        _register_crop_layer()
        prototxt = str(ensure_model("hed", "prototxt"))
        caffemodel = str(ensure_model("hed", "caffemodel"))
        self._net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)

    def detect_edges(self, image: np.ndarray) -> np.ndarray:
        self._load_net()

        h, w = image.shape[:2]
        scale = 1.0
        if max(h, w) > self.MAX_INFERENCE_DIM:
            scale = self.MAX_INFERENCE_DIM / max(h, w)
            inp = cv2.resize(image, (int(w * scale), int(h * scale)))
        else:
            inp = image

        inp_h, inp_w = inp.shape[:2]
        blob = cv2.dnn.blobFromImage(
            inp,
            scalefactor=1.0,
            size=(inp_w, inp_h),
            mean=(104.00698793, 116.66876762, 122.67891434),
            swapRB=False,
            crop=False,
        )
        self._net.setInput(blob)
        out = self._net.forward()

        # out shape: (1, 1, H, W) — sigmoid probabilities
        edge_map = out[0, 0]
        edge_map = (edge_map * 255).clip(0, 255).astype(np.uint8)

        # Upscale back to original size if we downscaled
        if scale != 1.0:
            edge_map = cv2.resize(edge_map, (w, h))

        # Threshold to binary
        _, binary = cv2.threshold(edge_map, self.edge_threshold, 255, cv2.THRESH_BINARY)
        return binary

    def is_available(self) -> bool:
        prototxt = model_path("hed", "prototxt")
        caffemodel = model_path("hed", "caffemodel")
        return prototxt.exists() and caffemodel.exists()
