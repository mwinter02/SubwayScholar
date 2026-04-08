from pathlib import Path
import shutil

from modules.pdf_module import PDFModule


def run_pdf_module_test(pdf_path: str, output_dir: Path | None = None) -> dict:
    target_dir = output_dir or Path("tests/pdf")
    target_dir.mkdir(parents=True, exist_ok=True)

    module = PDFModule()
    result = module.extract(pdf_path)

    text_output = target_dir / "extracted_text.txt"
    text_output.write_text(result.get("text", ""), encoding="utf-8")

    copied_images = []
    for index, image_path in enumerate(result.get("images", []), start=1):
        source = Path(image_path)
        destination = target_dir / f"image_{index}.png"
        if source.exists():
            shutil.copy2(source, destination)
            copied_images.append(str(destination))

    return {
        "text_path": str(text_output),
        "images": copied_images,
    }
