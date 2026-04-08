from pathlib import Path

from modules.video_module import VideoModule


def run_video_module_test(audio_path: str, output_video_path: str, image_paths: list[str]) -> dict:
    if not image_paths:
        raise ValueError("At least one image path is required")

    if not Path(audio_path).exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    for image_path in image_paths:
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

    module = VideoModule()
    video_path = module.create_video(audio_path=audio_path, images=image_paths, output_path=output_video_path)

    return {
        "video_path": video_path,
    }
