import argparse

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run module-level tests.")
    parser.add_argument("-pdf", dest="pdf_path", help="Path to input PDF for PDF module test")
    parser.add_argument("-llm", dest="llm_text_path", help="Path to input TXT for LLM module test")
    parser.add_argument("-tts", dest="tts_text_path", help="Path to input TXT script for TTS module test")
    parser.add_argument(
        "-video",
        dest="video_args",
        nargs="+",
        help=(
            "Run video module test: -video <audio_path> <output_video_path> "
            "<image1> [image2 ...]"
        ),
    )

    args = parser.parse_args()

    if args.pdf_path:
        from tests.pdf.test_pdf_module import run_pdf_module_test

        result = run_pdf_module_test(args.pdf_path)
        print(f"PDF test complete. Text output: {result['text_path']}")
        print(f"Extracted images: {len(result['images'])}")

    if args.llm_text_path:
        from tests.llm.test_llm_module import run_llm_module_test

        result = run_llm_module_test(args.llm_text_path)
        print(f"LLM test complete. Script output: {result['script_path']}")

    if args.tts_text_path:
        from tests.tts.test_tts_module import run_tts_module_test

        result = run_tts_module_test(args.tts_text_path)
        print(f"TTS test complete. Audio output: {result['audio_path']}")

    if args.video_args:
        if len(args.video_args) < 3:
            parser.error("-video requires: <audio_path> <output_video_path> <image1> [image2 ...]")

        from tests.video.test_video_module import run_video_module_test

        audio_path = args.video_args[0]
        output_video_path = args.video_args[1]
        image_paths = args.video_args[2:]

        result = run_video_module_test(
            audio_path=audio_path,
            output_video_path=output_video_path,
            image_paths=image_paths,
        )
        print(f"Video test complete. Video output: {result['video_path']}")

    if not any([args.pdf_path, args.llm_text_path, args.tts_text_path, args.video_args]):
        parser.print_help()


if __name__ == "__main__":
    main()
