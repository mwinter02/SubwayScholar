from pathlib import Path
from typing import List

import fitz
import pdfplumber


class PDFModule:
    def extract(self, pdf_path: str) -> dict:
        """
        Returns:
        {
            "text": str,
            "images": List[str]  # file paths
        }
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        images_output_dir = Path("outputs/images")
        images_output_dir.mkdir(parents=True, exist_ok=True)

        text_parts = []
        with pdfplumber.open(str(pdf_file)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n".join(text_parts)

        saved_images: List[str] = []
        image_index = 1

        with fitz.open(str(pdf_file)) as doc:
            for page_number in range(len(doc)):
                page = doc.load_page(page_number)
                for image_info in page.get_images(full=True):
                    xref = image_info[0]
                    image_path = images_output_dir / f"image_{image_index}.png"

                    try:
                        pixmap = fitz.Pixmap(doc, xref)
                        if pixmap.n - pixmap.alpha > 3:
                            rgb_pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
                            pixmap = None
                            rgb_pixmap.save(str(image_path))
                            rgb_pixmap = None
                        else:
                            pixmap.save(str(image_path))
                            pixmap = None
                    except Exception:
                        image_data = doc.extract_image(xref)
                        image_bytes = image_data.get("image") if image_data else None
                        if not image_bytes:
                            continue
                        with open(image_path, "wb") as image_file:
                            image_file.write(image_bytes)

                    saved_images.append(str(image_path))
                    image_index += 1

        return {
            "text": full_text,
            "images": saved_images,
        }
