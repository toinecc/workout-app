"""Predefined exercise pose sequences."""

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
