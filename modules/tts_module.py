from pathlib import Path
import wave

import requests


class TTSModule:
    MODEL_DIR = Path("models")
    MODEL_NAME = "en_US-lessac-medium.onnx"
    MODEL_CONFIG_NAME = "en_US-lessac-medium.onnx.json"

    MODEL_URL = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
        "en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    )
    MODEL_CONFIG_URL = (
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/"
        "en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    )

    OUTPUT_AUDIO_PATH = Path("outputs/audio/output.wav")

    def synthesize(self, script: str) -> str:
        """
        Converts script text into speech using Piper.

        Returns:
            Path to generated WAV audio file
        """
        self.OUTPUT_AUDIO_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)

        model_path, config_path = self._ensure_model_files()

        cleaned_script = (script or "").strip()
        if not cleaned_script:
            raise ValueError("Script is empty")

        try:
            from piper import PiperVoice, SynthesisConfig
        except ImportError as exc:
            raise RuntimeError(
                "piper-tts is not installed. Run: pip install piper-tts"
            ) from exc

        try:
            voice = PiperVoice.load(model_path=model_path, config_path=config_path, use_cuda=False)
            syn_config = SynthesisConfig()

            with wave.open(str(self.OUTPUT_AUDIO_PATH), "wb") as wav_file:
                wrote_audio = False
                for audio_chunk in voice.synthesize(cleaned_script, syn_config=syn_config):
                    if not wrote_audio:
                        wav_file.setframerate(audio_chunk.sample_rate)
                        wav_file.setsampwidth(audio_chunk.sample_width)
                        wav_file.setnchannels(audio_chunk.sample_channels)
                        wrote_audio = True

                    wav_file.writeframes(audio_chunk.audio_int16_bytes)

            if not wrote_audio:
                raise RuntimeError("Piper TTS synthesis failed")

            return str(self.OUTPUT_AUDIO_PATH)
        except RuntimeError as exc:
            if str(exc) == "Piper TTS synthesis failed":
                raise
            raise RuntimeError("Piper TTS synthesis failed") from exc
        except Exception as exc:
            raise RuntimeError("Piper TTS synthesis failed") from exc

    def _ensure_model_files(self) -> tuple[Path, Path]:
        model_path = self.MODEL_DIR / self.MODEL_NAME
        config_path = self.MODEL_DIR / self.MODEL_CONFIG_NAME

        if not model_path.exists():
            self._download_file(self.MODEL_URL, model_path)

        if not config_path.exists():
            self._download_file(self.MODEL_CONFIG_URL, config_path)

        return model_path, config_path

    def _download_file(self, url: str, destination: Path) -> None:
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            with open(destination, "wb") as file_obj:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file_obj.write(chunk)
        except Exception as exc:
            try:
                if destination.exists():
                    destination.unlink()
            except Exception:
                pass
            raise RuntimeError("Failed to download Piper voice model") from exc
