import math
from pathlib import Path
from typing import Any


class VideoModule:
    BACKGROUND_VIDEO_PATH = Path("assets/background.mp4")

    def create_video(self, audio_path: str, images: list, output_path: str) -> str:
        """Returns final video path"""
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not self.BACKGROUND_VIDEO_PATH.exists():
            raise FileNotFoundError(
                f"Background video not found: {self.BACKGROUND_VIDEO_PATH}"
            )

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            from moviepy import (
                AudioFileClip,
                CompositeVideoClip,
                ImageClip,
                VideoFileClip,
                concatenate_videoclips,
            )
        except ImportError:
            from moviepy.editor import (  # type: ignore
                AudioFileClip,
                CompositeVideoClip,
                ImageClip,
                VideoFileClip,
                concatenate_videoclips,
            )

        closable_clips = []

        try:
            audio_clip = AudioFileClip(str(audio_file))
            closable_clips.append(audio_clip)

            audio_duration = float(getattr(audio_clip, "duration", 0) or 0)
            if audio_duration <= 0:
                raise ValueError("Audio duration must be greater than zero")

            background_clips = [VideoFileClip(str(self.BACKGROUND_VIDEO_PATH))]
            closable_clips.extend(background_clips)

            background_duration = float(
                getattr(background_clips[0], "duration", 0) or 0
            )
            if background_duration <= 0:
                raise ValueError("Background video duration must be greater than zero")

            repeats = max(1, math.ceil(audio_duration / background_duration))
            for _ in range(repeats - 1):
                clip = VideoFileClip(str(self.BACKGROUND_VIDEO_PATH))
                background_clips.append(clip)
                closable_clips.append(clip)

            looped_background = concatenate_videoclips(background_clips, method="compose")
            closable_clips.append(looped_background)
            looped_background = self._trim(looped_background, 0, audio_duration)

            image_overlays = []
            if images:
                image_duration = audio_duration / max(len(images), 1)
                for index, image_path in enumerate(images):
                    image_file = Path(image_path)
                    if not image_file.exists():
                        raise FileNotFoundError(f"Image file not found: {image_path}")

                    image_clip = ImageClip(str(image_file))
                    image_clip = self._set_start(image_clip, index * image_duration)
                    image_clip = self._set_duration(image_clip, image_duration)
                    image_clip = self._set_position(image_clip, ("center", "center"))
                    image_overlays.append(image_clip)
                    closable_clips.append(image_clip)

            layers = [looped_background] + image_overlays
            final_clip = CompositeVideoClip(layers, size=looped_background.size)
            closable_clips.append(final_clip)
            final_clip = self._set_duration(final_clip, audio_duration)
            final_clip = self._set_audio(final_clip, audio_clip)

            fps = int(getattr(background_clips[0], "fps", 24) or 24)
            final_clip.write_videofile(
                str(output_file),
                codec="libx264",
                audio_codec="aac",
                fps=fps,
                logger=None,
            )

            return str(output_file)
        finally:
            for clip in reversed(closable_clips):
                close_method = getattr(clip, "close", None)
                if callable(close_method):
                    close_method()

    def _trim(self, clip: Any, start: float, end: float) -> Any:
        if hasattr(clip, "subclipped"):
            return clip.subclipped(start, end)
        return clip.subclip(start, end)

    def _set_start(self, clip: Any, start: float) -> Any:
        if hasattr(clip, "with_start"):
            return clip.with_start(start)
        return clip.set_start(start)

    def _set_duration(self, clip: Any, duration: float) -> Any:
        if hasattr(clip, "with_duration"):
            return clip.with_duration(duration)
        return clip.set_duration(duration)

    def _set_position(self, clip: Any, position: Any) -> Any:
        if hasattr(clip, "with_position"):
            return clip.with_position(position)
        return clip.set_position(position)

    def _set_audio(self, clip: Any, audio_clip: Any) -> Any:
        if hasattr(clip, "with_audio"):
            return clip.with_audio(audio_clip)
        return clip.set_audio(audio_clip)
