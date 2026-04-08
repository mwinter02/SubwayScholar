from pathlib import Path
from typing import List

import fitz


class PDFModule:
    TEMP_IMAGES_DIR = Path("temp/images")

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

        images_output_dir = self.TEMP_IMAGES_DIR
        images_output_dir.mkdir(parents=True, exist_ok=True)

        text_parts: List[str] = []
        saved_images: List[str] = []
        image_index = 1

        with fitz.open(str(pdf_file)) as doc:
            for page_number in range(len(doc)):
                page = doc.load_page(page_number)

                page_text = self._extract_page_text(page)
                if page_text:
                    text_parts.append(page_text)

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

        full_text = "\n\n".join(text_parts)

        return {
            "text": full_text,
            "images": saved_images,
        }

    def _extract_page_text(self, page: fitz.Page) -> str:
        words = page.get_text("words", sort=True)
        if not words:
            return (page.get_text("text") or "").strip()

        lines: List[str] = []
        current_key = None
        current_words: List[str] = []

        for word_entry in words:
            text = str(word_entry[4]).strip()
            if not text:
                continue

            key = (int(word_entry[5]), int(word_entry[6]))
            if current_key is None:
                current_key = key

            if key != current_key:
                if current_words:
                    lines.append(" ".join(current_words))
                current_words = [text]
                current_key = key
            else:
                current_words.append(text)

        if current_words:
            lines.append(" ".join(current_words))

        return "\n".join(lines).strip()
