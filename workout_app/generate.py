"""AI image generation via Replicate."""

import io
import time

import httpx
import replicate
from PIL import Image

MODEL = "black-forest-labs/flux-dev"

_last_call_time: float = 0


def _rate_limit() -> None:
    """Wait if needed to stay under Replicate's rate limit."""
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if _last_call_time and elapsed < 12:
        time.sleep(12 - elapsed)
    _last_call_time = time.time()


def _download_image(url: str, width: int, height: int) -> Image.Image:
    """Download an image from a URL and resize it."""
    response = httpx.get(url)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content)).convert("RGB")
    return img.resize((width, height))


def generate_image(prompt: str, style: str, width: int, height: int, seed: int) -> Image.Image:
    """Generate an image via txt2img with a fixed seed for character consistency."""
    _rate_limit()
    full_prompt = f"{style} — {prompt}"
    output = replicate.run(
        MODEL,
        input={
            "prompt": full_prompt,
            "seed": seed,
            "num_outputs": 1,
            "aspect_ratio": "16:9",
            "output_format": "png",
        },
    )
    return _download_image(str(output[0]), width, height)
