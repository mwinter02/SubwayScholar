from pathlib import Path
import shutil
from typing import Optional

from modules.tts_module import TTSModule


def run_tts_module_test(script_path: str, output_dir: Optional[Path] = None) -> dict:
    input_path = Path(script_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Script file not found: {script_path}")

    target_dir = output_dir or Path("tests/tts")
    target_dir.mkdir(parents=True, exist_ok=True)

    script = input_path.read_text(encoding="utf-8")
    module = TTSModule()
    audio_path = module.synthesize(script)

    output_audio_path = target_dir / "output.wav"
    shutil.copy2(audio_path, output_audio_path)

    return {
        "audio_path": str(output_audio_path),
    }
