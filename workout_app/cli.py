"""CLI to generate animated exercise GIFs using AI-generated images."""

import random
from pathlib import Path
from typing import Annotated

import typer

from workout_app.exercises import DEFAULT_STYLE, EXERCISES
from workout_app.image import add_label, generate_image, save_gif

app = typer.Typer(help="Generate fun exercise GIFs using AI.")


@app.command()
def generate(
    exercise: Annotated[
        str,
        typer.Argument(help=f"Exercise name. Built-in: {', '.join(EXERCISES.keys())}"),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output GIF file path."),
    ] = None,
    style: Annotated[
        str,
        typer.Option("--style", "-s", help="Art style prompt prefix for consistent visuals."),
    ] = DEFAULT_STYLE,
    width: Annotated[
        int,
        typer.Option("--width", "-w", help="Image width in pixels."),
    ] = 1280,
    height: Annotated[
        int,
        typer.Option("--height", "-h", help="Image height in pixels."),
    ] = 720,
    duration: Annotated[
        int,
        typer.Option("--duration", "-d", help="Duration per frame in milliseconds."),
    ] = 400,
    frames: Annotated[
        int,
        typer.Option("--frames", "-f", help="Number of frames (only for custom exercises)."),
    ] = 4,
    seed: Annotated[
        int,
        typer.Option("--seed", help="Fixed seed for character consistency. Same seed = same character look."),
    ] = None,
    label: Annotated[
        bool,
        typer.Option("--label/--no-label", help="Add exercise name label on each frame."),
    ] = True,
):
    """Generate an animated GIF for a single exercise."""
    exercise_key = exercise.lower().strip()

    if exercise_key in EXERCISES:
        poses = EXERCISES[exercise_key]
        display_name = exercise_key.replace("-", " ").upper()
    else:
        display_name = exercise.upper()
        poses = [
            f"person doing {exercise}, starting position",
            f"person doing {exercise}, mid-movement",
            f"person doing {exercise}, peak of the movement",
            f"person doing {exercise}, returning to start",
        ][:frames]

    gif_dir = Path("data/gifs")
    frames_dir = Path("data/frames")
    gif_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    if output is None:
        output = gif_dir / f"{exercise_key}.gif"

    if seed is None:
        seed = random.randint(0, 2**31)

    typer.echo(f"Generating {len(poses)} frames for {display_name} (seed={seed})...")
    typer.echo(f"Frames saved to: {frames_dir}/\n")

    images = []
    for i, pose in enumerate(poses, 1):
        typer.echo(f"  [{i}/{len(poses)}] {pose[:70]}...")
        img = generate_image(pose, style, width, height, seed)
        frame_path = frames_dir / f"{exercise_key}_frame{i:02d}.png"
        img.save(str(frame_path))
        typer.echo(f"         -> {frame_path}")
        images.append(img)

    # Apply labels after all frames are generated
    if label:
        images = [add_label(img, display_name) for img in images]

    save_gif(images, str(output), duration)

    typer.echo(f"\nSaved {output} ({len(images)} frames, {width}x{height}px)")
    typer.echo(f"Individual frames in: {frames_dir}/")
    typer.echo(f"Re-run with --seed {seed} to get the same character style.")


if __name__ == "__main__":
    app()
