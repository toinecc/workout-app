"""CLI to generate animated exercise GIFs and workout videos."""

import random
from pathlib import Path
from typing import Annotated

import typer

from workout_app.exercises import DEFAULT_STYLE, EXERCISES
from workout_app.generate import generate_image
from workout_app.gif import add_label, save_gif
from workout_app.video import build_workout

app = typer.Typer(help="CLI to create fun workouts!")


@app.command()
def generate_gif(
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


@app.command()
def workout(
    exercise: Annotated[
        list[str],
        typer.Option(
            "--exercise", "-e",
            help="Exercise in format 'name:duration_seconds' (e.g. 'squats:30'). Repeatable.",
        ),
    ],
    rest: Annotated[
        int,
        typer.Option("--rest", "-r", help="Rest duration in seconds between exercises."),
    ] = 10,
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output MP4 file path."),
    ] = Path("data/workout.mp4"),
    width: Annotated[
        int,
        typer.Option("--width", "-w", help="Video width in pixels."),
    ] = 1920,
    height: Annotated[
        int,
        typer.Option("--height", "-h", help="Video height in pixels."),
    ] = 1080,
    fps: Annotated[
        int,
        typer.Option("--fps", help="Frames per second."),
    ] = 4,
    music: Annotated[
        Path,
        typer.Option("--music", "-m", help="MP3 file to use as background music (trimmed to video length)."),
    ] = None,
    title: Annotated[
        str,
        typer.Option("--title", "-t", help="Workout name shown on a title card at the start."),
    ] = None,
    title_duration: Annotated[
        int,
        typer.Option("--title-duration", help="How long the title card is shown in seconds."),
    ] = 20,
):
    """Assemble exercise GIFs into a full workout MP4 video."""
    parsed: list[dict] = []
    gif_dir = Path("data/gifs")

    for entry in exercise:
        if ":" not in entry:
            typer.echo(f"Error: '{entry}' must be in format 'name:duration' (e.g. 'squats:30').", err=True)
            raise typer.Exit(1)
        name, dur = entry.rsplit(":", 1)
        gif_path = gif_dir / f"{name}.gif"
        if not gif_path.exists():
            typer.echo(f"Error: GIF not found at {gif_path}. Generate it first.", err=True)
            raise typer.Exit(1)
        parsed.append({"gif": gif_path, "duration": int(dur), "name": name.replace("-", " ")})

    output.parent.mkdir(parents=True, exist_ok=True)

    total_exercise = sum(e["duration"] for e in parsed)
    total_rest = rest * (len(parsed) - 1) if len(parsed) > 1 else 0
    total = total_exercise + total_rest

    typer.echo(f"Building workout video ({len(parsed)} exercises, {total}s total):")
    for e in parsed:
        typer.echo(f"  - {e['name'].upper()}: {e['duration']}s")
    if total_rest:
        typer.echo(f"  - REST between exercises: {rest}s")
    typer.echo("")

    if music and not music.exists():
        typer.echo(f"Error: Music file {music} not found.", err=True)
        raise typer.Exit(1)

    build_workout(parsed, rest, output, width, height, fps, music, title, title_duration)
    typer.echo(f"Saved {output} ({width}x{height}px, {total}s)")
    if music:
        typer.echo(f"Music: {music}")


if __name__ == "__main__":
    app()
