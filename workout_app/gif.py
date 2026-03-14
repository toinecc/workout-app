"""GIF tooling: labeling, loading, and saving."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LABEL_HEIGHT = 80
FONT_SIZE = 48


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a bold TrueType font, falling back to the default font."""
    for path in (
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def add_label(img: Image.Image, label: str, position: str = "top") -> Image.Image:
    """Add an exercise name label banner at the top or bottom."""
    draw = ImageDraw.Draw(img)
    font = _get_font(FONT_SIZE)
    if position == "bottom":
        y0 = img.height - LABEL_HEIGHT
        y1 = img.height
        text_y = img.height - LABEL_HEIGHT // 2
    else:
        y0 = 0
        y1 = LABEL_HEIGHT
        text_y = LABEL_HEIGHT // 2
    draw.rectangle([0, y0, img.width, y1], fill=(0, 0, 0))
    draw.text(
        (img.width // 2, text_y), label, fill=(255, 220, 80), anchor="mm", font=font
    )
    return img


def save_gif(images: list[Image.Image], output: str, duration: int) -> None:
    """Save a list of images as an animated GIF."""
    images[0].save(
        output,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
    )


def load_gif_frames(gif_path: Path) -> tuple[list[Image.Image], int]:
    """Load all frames from a GIF. Returns (frames, duration_ms)."""
    src = Image.open(gif_path)
    frames: list[Image.Image] = []
    duration = src.info.get("duration", 400)
    try:
        while True:
            frames.append(src.copy().convert("RGB"))
            src.seek(src.tell() + 1)
    except EOFError:
        pass
    return frames, duration
