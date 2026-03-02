from .canny import CannyBackend
from .hed import HEDBackend
from .openai import OpenAIBackend
from .stability import StabilityBackend

BACKENDS = {
    "canny": CannyBackend,
    "hed": HEDBackend,
    "openai": OpenAIBackend,
    "stability": StabilityBackend,
}


def get_backend(name: str, **kwargs):
    """Create a backend instance by name."""
    if name not in BACKENDS:
        raise ValueError(f"Unknown backend: {name!r}. Available: {list(BACKENDS)}")
    return BACKENDS[name](**kwargs)
