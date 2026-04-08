import argparse
import shutil
from pathlib import Path

from dotenv import load_dotenv

from modules.pdf_module import PDFModule
from modules.llm_module import LLMModule
from modules.tts_module import TTSModule
from modules.video_module import VideoModule


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full PDF-to-video pipeline.")
    parser.add_argument(
        "pdf_path",
        help="Path to input PDF file",
    )
    parser.add_argument(
        "--use-openai-api",
        action="store_true",
        help=(
            "Use OpenAI API for script generation. "
            "Default mode is manual clipboard + paste flow."
        ),
    )
    parser.add_argument(
        "--voice-model",
        default=TTSModule.DEFAULT_MODEL_NAME,
        help=(
            "Piper voice model name (.onnx optional). "
            f"Default: {TTSModule.DEFAULT_MODEL_NAME}"
        ),
    )
    parser.add_argument(
        "--background-video",
        default="assets/background.mp4",
        help="Path to background video file. Default: assets/background.mp4",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    pdf_path = args.pdf_path
    output_file = Path("outputs") / f"{Path(pdf_path).stem}.mp4"

    # Ensure required runtime directories exist before pipeline runs.
    Path("outputs").mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(parents=True, exist_ok=True)
    Path("temp").mkdir(parents=True, exist_ok=True)
    _reset_temp_media_dirs()

    print("[1/4] Extracting text and images from PDF...")
    pdf_module = PDFModule()
    pdf_data = pdf_module.extract(pdf_path)
    print(
        f"       Extracted {len(pdf_data.get('text', ''))} text characters and "
        f"{len(pdf_data.get('images', []))} images."
    )

    if args.use_openai_api:
        print("[2/4] Generating narration script with OpenAI...")
    else:
        print("[2/4] Generating narration script in manual LLM mode...")
    llm_module = LLMModule()
    script = llm_module.generate_script(pdf_data["text"], use_api=args.use_openai_api)
    print(f"       Generated script with {len(script.split())} words.")

    print("[3/4] Converting script to speech...")
    tts_module = TTSModule()
    audio_path = tts_module.synthesize(script, model=args.voice_model)
    print(f"       Audio saved to: {audio_path}")

    print("[4/4] Creating final video...")
    video_module = VideoModule()
    final_video_path = video_module.create_video(
        audio_path,
        pdf_data["images"],
        str(output_file),
        background_video=args.background_video,
    )
    print(f"       Video saved to: {final_video_path}")

    _cleanup_temp_media_dirs()
    print("       Cleaned temporary audio/image files.")
    print(f"Done. Final video path: {final_video_path}")


def _reset_temp_media_dirs() -> None:
    for temp_dir in [Path("temp/images"), Path("temp/audio")]:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        temp_dir.mkdir(parents=True, exist_ok=True)


def _cleanup_temp_media_dirs() -> None:
    for temp_dir in [Path("temp/images"), Path("temp/audio")]:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
