# Workout App

Generate animated exercise GIFs using AI and assemble them into full workout videos with countdowns, rest screens, title cards, and background music.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- A [Replicate](https://replicate.com/) API token (for AI image generation)
- [ffmpeg](https://ffmpeg.org/) (for video assembly)

## Installation

```bash
uv sync
```

## Project Structure

```
workout_app/
  exercises.py   # Exercise pose definitions and style prompts
  generate.py    # AI image generation via Replicate
  gif.py         # GIF tooling: labeling, loading, saving
  video.py       # Workout video assembly (MP4 with ffmpeg)
  cli.py         # CLI commands (generate, workout)
```

## CLI Commands

### `generate-workout` — Assemble a workout video

Combine exercise GIFs into a full workout MP4 video with countdown timers, rest screens, an optional title card, and background music.

```bash
uv run generate-exercise-gif generate-workout [options]
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `-e, --exercise` | *(required)* | Exercise in format `name:duration_seconds` (repeatable) |
| `-r, --rest` | `10` | Rest duration in seconds between exercises |
| `-o, --output` | `data/workout.mp4` | Output MP4 file path |
| `-w, --width` | `1920` | Video width in pixels |
| `-h, --height` | `1080` | Video height in pixels |
| `--fps` | `4` | Frames per second |
| `-m, --music` | None | MP3 file for background music (trimmed to video length) |
| `-t, --title` | None | Workout name shown on a title card at the start |
| `--title-duration` | `20` | Title card duration in seconds |

**Examples:**

```bash
# Simple workout
uv run generate-exercise-gif generate-workout \
  -e squats:30 \
  -e push-ups:30 \
  -e high-knees:30 \
  --rest 10

# Full workout with title and music
uv run generate-exercise-gif generate-workout \
  -e push-ups:35 \
  -e high-knees:35 \
  -e biceps-curl:35 \
  -e mountain-climbers:35 \
  -e alternative-sit-up:35 \
  --rest 10 \
  -t "Morning Circuit" \
  -m music.mp3 \
  -o data/morning_circuit.mp4
```

The exercise name in `-e` must match a GIF filename in `data/gifs/` (without the `.gif` extension). Generate the GIFs first with the `generate` command.

### `generate-gif` — Generate an exercise GIF

Generate an animated GIF for a single exercise using AI-generated frames.

```bash
uv run generate-exercise-gif generate <exercise-name> [options]
```

Built-in exercises: `jumping-jacks`, `squats`, `push-ups`, `lunges`, `burpees`. You can also pass any custom exercise name and the app will generate poses automatically.

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `-o, --output` | `data/gifs/<name>.gif` | Output GIF file path |
| `-s, --style` | Built-in style | Art style prompt for visuals |
| `-w, --width` | `1280` | Image width in pixels |
| `-h, --height` | `720` | Image height in pixels |
| `-d, --duration` | `400` | Duration per frame in milliseconds |
| `-f, --frames` | `4` | Number of frames (custom exercises only) |
| `--seed` | Random | Fixed seed for character consistency |
| `--label/--no-label` | `--label` | Add exercise name label on each frame |

**Examples:**

```bash
# Generate a built-in exercise
uv run generate-exercise-gif generate-gif squats

# Custom exercise with a fixed seed
uv run generate-exercise-gif generate-gif  "kettlebell-swings" --seed 42

# Higher resolution, no label
uv run generate-exercise-gif generate-gif push-ups -w 1920 -h 1080 --no-label
```


## Claude Code Skills

### `/create-workout`

A Claude Code skill that acts as a fitness coach to design balanced workout routines. It:

1. Scans available exercise GIFs in `data/gifs/`
2. Categorizes them by muscle group (upper push/pull, core, lower body, cardio)
3. Selects 6-8 exercises with balanced muscle group coverage
4. Orders them to alternate muscle groups (never two consecutive exercises targeting the same area)
5. Designs a 30-40 minute circuit with multiple rounds
6. Presents the plan for approval, then runs the `workout` CLI command

## GIF Sources

- https://giphy.com/danielflefil/exercises
- https://giphy.com/hockeytraining
