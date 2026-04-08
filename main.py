import argparse
from pathlib import Path

from dotenv import load_dotenv

from modules.pdf_module import PDFModule
from modules.llm_module import LLMModule
from modules.tts_module import TTSModule
from modules.video_module import VideoModule


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full PDF-to-video pipeline.")
    parser.add_argument(
        "--voice-model",
        default=TTSModule.DEFAULT_MODEL_NAME,
        help=(
            "Piper voice model name (.onnx optional). "
            "Default: en_US-lessac-medium.onnx"
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

    pdf_path = "input.pdf"  # TODO: Replace with CLI argument or config value
    output_path = "outputs/video/final.mp4"

    # Ensure project output/model/temp directories exist before pipeline runs.
    Path("outputs/audio").mkdir(parents=True, exist_ok=True)
    Path("outputs/images").mkdir(parents=True, exist_ok=True)
    Path("outputs/video").mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(parents=True, exist_ok=True)
    Path("temp").mkdir(parents=True, exist_ok=True)

    print("[1/4] Extracting text and images from PDF...")
    pdf_module = PDFModule()
    pdf_data = pdf_module.extract(pdf_path)
    print(
        f"       Extracted {len(pdf_data.get('text', ''))} text characters and "
        f"{len(pdf_data.get('images', []))} images."
    )

    print("[2/4] Generating narration script with OpenAI...")
    llm_module = LLMModule()
    script = llm_module.generate_script(pdf_data["text"])
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
        output_path,
        background_video=args.background_video,
    )
    print(f"       Video saved to: {final_video_path}")

    print(f"Done. Final video path: {final_video_path}")


if __name__ == "__main__":
    main()
