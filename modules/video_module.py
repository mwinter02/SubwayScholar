import math
from pathlib import Path
from typing import Any


class VideoModule:
    BACKGROUND_VIDEO_PATH = Path("assets/background.mp4")

    def create_video(
        self,
        audio_path: str,
        images: list,
        output_path: str,
        background_video: str = "assets/background.mp4",
    ) -> str:
        """Returns final video path"""
        audio_file = Path(audio_path)
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        background_video_path = Path(background_video)
        if not background_video_path.exists():
            raise FileNotFoundError(
                f"Background video not found: {background_video_path}"
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

            background_clips = [VideoFileClip(str(background_video_path))]
            closable_clips.extend(background_clips)

            background_duration = float(
                getattr(background_clips[0], "duration", 0) or 0
            )
            if background_duration <= 0:
                raise ValueError("Background video duration must be greater than zero")

            video_width, video_height = background_clips[0].size
            safe_area_width = float(video_width) * 0.5
            safe_area_height = float(video_height) * 0.5

            repeats = max(1, math.ceil(audio_duration / background_duration))
            for _ in range(repeats - 1):
                clip = VideoFileClip(str(background_video_path))
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
                    image_clip = self._fit_image_to_safe_area(
                        image_clip=image_clip,
                        max_width=safe_area_width,
                        max_height=safe_area_height,
                    )
                    image_clip = self._set_start(image_clip, index * image_duration)
                    image_clip = self._set_duration(image_clip, image_duration)
                    y_position = self._compute_safe_y_position(
                        image_clip=image_clip,
                        video_height=float(video_height),
                        target_center_ratio=0.35,
                    )
                    image_clip = self._set_position(image_clip, ("center", y_position))
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

    def _fit_image_to_safe_area(
        self, image_clip: Any, max_width: float, max_height: float
    ) -> Any:
        image_size = getattr(image_clip, "size", None)
        if not image_size or image_size[0] <= 0 or image_size[1] <= 0:
            return image_clip

        image_width, image_height = float(image_size[0]), float(image_size[1])
        scale = min(max_width / image_width, max_height / image_height, 1.0)

        resized_width = max(1, int(round(image_width * scale)))
        resized_height = max(1, int(round(image_height * scale)))
        return self._resize(image_clip, resized_width, resized_height)

    def _resize(self, clip: Any, width: int, height: int) -> Any:
        if hasattr(clip, "resized"):
            return clip.resized(new_size=(width, height))
        return clip.resize(newsize=(width, height))

    def _compute_safe_y_position(
        self, image_clip: Any, video_height: float, target_center_ratio: float
    ) -> float:
        image_size = getattr(image_clip, "size", None)
        if not image_size or image_size[1] <= 0:
            return max(0.0, video_height * target_center_ratio)

        image_height = float(image_size[1])
        target_center_y = video_height * target_center_ratio
        top_y = target_center_y - (image_height / 2.0)

        # Clamp to visible bounds so the image never overflows the frame.
        max_top_y = max(0.0, video_height - image_height)
        return max(0.0, min(top_y, max_top_y))
