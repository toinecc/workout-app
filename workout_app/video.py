"""Workout video assembly — concatenate exercise GIFs into an MP4."""

import subprocess

from pathlib import Path

from PIL import Image, ImageDraw

from workout_app.gif import _get_font, add_label, load_gif_frames


def _make_rest_frame(
    width: int, height: int, seconds_left: int
) -> Image.Image:
    """Create a single rest screen frame with countdown."""
    # Deep navy blue matching the exercise background
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    title_font = _get_font(72)
    countdown_font = _get_font(120)
    draw.text(
        (width // 2, height // 2 - 80),
        "REST",
        fill=(255, 220, 80),
        anchor="mm",
        font=title_font,
    )
    draw.text(
        (width // 2, height // 2 + 60),
        str(seconds_left),
        fill=(255, 255, 255),
        anchor="mm",
        font=countdown_font,
    )
    return img


def _make_title_frame(
    width: int, height: int, title: str, total_duration: int
) -> Image.Image:
    """Create a title card frame with workout name and total duration."""
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    title_font = _get_font(90)
    sub_font = _get_font(48)

    minutes, secs = divmod(total_duration, 60)
    if minutes:
        duration_text = f"{minutes}min {secs}s"
    else:
        duration_text = f"{secs}s"

    draw.text(
        (width // 2, height // 2 - 60),
        title.upper(),
        fill=(255, 220, 80),
        anchor="mm",
        font=title_font,
    )
    draw.text(
        (width // 2, height // 2 + 60),
        duration_text,
        fill=(255, 255, 255),
        anchor="mm",
        font=sub_font,
    )
    return img


def _add_countdown(img: Image.Image, seconds_left: int) -> Image.Image:
    """Overlay a countdown timer in the top-right corner of a frame."""
    img = img.copy()
    draw = ImageDraw.Draw(img)
    font = _get_font(52)
    text = str(seconds_left)
    padding = 20
    # Draw a semi-transparent black rounded box behind the text
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = img.width - tw - padding * 3
    y = padding
    draw.rectangle(
        [x, y, x + tw + padding * 2, y + th + padding],
        fill=(0, 0, 0),
    )
    draw.text(
        (x + padding, y + padding // 2),
        text,
        fill=(255, 255, 255),
        font=font,
    )
    return img


BACKGROUND_COLOR = (10, 15, 44)


def _fit_to_canvas(frame: Image.Image, width: int, height: int) -> Image.Image:
    """Fit a frame into a canvas, preserving aspect ratio with navy blue bars."""
    if frame.size == (width, height):
        return frame
    # Scale to fit within the target dimensions
    scale = min(width / frame.width, height / frame.height)
    new_w = int(frame.width * scale)
    new_h = int(frame.height * scale)
    scaled = frame.resize((new_w, new_h), Image.LANCZOS)
    # Center on a navy blue canvas
    canvas = Image.new("RGB", (width, height), BACKGROUND_COLOR)
    x = (width - new_w) // 2
    y = (height - new_h) // 2
    canvas.paste(scaled, (x, y))
    return canvas


def _frames_to_raw(frames: list[Image.Image], width: int, height: int) -> bytes:
    """Convert PIL frames to raw RGB bytes, fitting to canvas if needed."""
    raw = bytearray()
    for frame in frames:
        raw.extend(_fit_to_canvas(frame, width, height).tobytes())
    return bytes(raw)


def build_workout(
    exercises: list[dict],
    rest_duration: int,
    output: Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 4,
    music: Path | None = None,
    title: str | None = None,
    title_duration: int = 20,
) -> None:
    """Build a workout MP4 from exercise GIFs.

    Args:
        exercises: list of {"gif": Path, "duration": int (seconds), "name": str}
        rest_duration: seconds of rest between exercises
        output: output MP4 path
        width: video width
        height: video height
        fps: frames per second (should match GIF frame rate)
        music: optional MP3 file to use as background music (trimmed to video length)
        title: optional workout name shown on a title card at the start
        title_duration: how long the title card is shown in seconds (default 20)
    """
    all_frames: list[Image.Image] = []

    # Title card at the beginning
    if title:
        total_workout_time = (
            sum(e["duration"] for e in exercises)
            + rest_duration * max(0, len(exercises) - 1)
        )
        title_frame = _make_title_frame(width, height, title, total_workout_time)
        for _ in range(title_duration * fps):
            all_frames.append(title_frame)

    for i, ex in enumerate(exercises):
        gif_path = Path(ex["gif"])
        duration_secs = ex["duration"]
        name = ex.get("name", gif_path.stem)

        # Load and label the GIF frames
        frames, frame_duration_ms = load_gif_frames(gif_path)
        labeled = [add_label(f.copy(), name.upper(), position="bottom") for f in frames]

        # Expand GIF frames to match video fps, preserving original playback speed
        # Each GIF frame is repeated for (frame_duration_ms / 1000 * fps) video frames
        video_frames_per_gif_frame = max(1, round(frame_duration_ms / 1000 * fps))
        one_cycle: list[Image.Image] = []
        for lf in labeled:
            one_cycle.extend([lf] * video_frames_per_gif_frame)

        # Loop the cycle to fill the exercise duration, with countdown
        total_frames_needed = duration_secs * fps
        for j in range(total_frames_needed):
            seconds_left = duration_secs - (j // fps)
            frame = _add_countdown(one_cycle[j % len(one_cycle)], seconds_left)
            all_frames.append(frame)

        # Add rest screens between exercises (not after the last one)
        if i < len(exercises) - 1 and rest_duration > 0:
            for sec in range(rest_duration, 0, -1):
                rest_frame = _make_rest_frame(width, height, sec)
                # Show each countdown number for 1 second (fps frames)
                for _ in range(fps):
                    all_frames.append(rest_frame)

    # Pipe raw frames into ffmpeg
    raw_data = _frames_to_raw(all_frames, width, height)
    video_duration = len(all_frames) / fps

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
    ]

    if music:
        cmd += ["-i", str(music), "-t", str(video_duration), "-c:a", "aac", "-shortest"]

    cmd += [
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output),
    ]

    proc = subprocess.run(cmd, input=raw_data, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{proc.stderr.decode()}")
