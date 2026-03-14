"""AI image generation via Replicate."""

import io
import time

import httpx
import replicate
from PIL import Image

MODEL = "black-forest-labs/flux-dev"

EXERCISES: dict[str, list[str]] = {
    "jumping-jacks": [
        "standing still with both arms straight down at sides, legs closed together",
        "jumping in the air, both arms stretched fully above head, legs wide apart in a V shape",
    ],
    "squats": [
        "standing fully upright with straight legs, arms relaxed at sides",
        "in a deep low squat with butt near the ground, knees fully bent, both arms stretched straight out in front at shoulder height, thighs horizontal",
    ],
    "push-ups": [
        "in a high plank position with arms fully locked straight, body horizontal, side view",
        "at the bottom of a push-up with chest touching the floor, arms fully bent, side view",
    ],
    "lunges": [
        "standing tall with both feet together, hands on hips",
        "in a deep forward lunge, front knee bent 90 degrees, back knee almost touching floor",
    ],
    "burpees": [
        "standing fully upright with arms relaxed at sides",
        "crouching low with both hands flat on the floor, knees tucked to chest",
        "jumping high in the air with both arms stretched above head, feet off the ground",
    ],
}

DEFAULT_BACKGROUND = (
    "plain deep navy blue background with subtle paper grain texture, "
    "uniform and simple, no scenery or objects"
)

DEFAULT_STYLE = (
    "An athletic man with a goofy dopey dog head, tongue hanging out, silly wide eyes, "
    "human muscular body, "
    "wearing a bright neon fitness outfit with headband and sneakers, "
    "facing the viewer, front view, looking straight at camera, "
    "colorful cartoon style, bold outlines, fun and energetic, full body visible, "
    "same character in every frame, consistent outfit and proportions, "
    f"exaggerated dynamic pose, comic book illustration, {DEFAULT_BACKGROUND}"
)


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


def generate_image(
    prompt: str, style: str, width: int, height: int, seed: int
) -> Image.Image:
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
