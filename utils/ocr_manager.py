# utils/ocr_manager.py

import re

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except Exception:
    pytesseract = None
    TESSERACT_AVAILABLE = False

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class OCRManager:
    def __init__(self):
        self.tesseract_available = TESSERACT_AVAILABLE

    def preprocess_image(self, image_path):
        image = Image.open(image_path)

        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        width, height = image.size

        if width < 1800:
            scale = 1800 / width
            image = image.resize(
                (int(width * scale), int(height * scale)),
                Image.Resampling.LANCZOS
            )

        gray = ImageOps.grayscale(image)

        gray = ImageEnhance.Contrast(gray).enhance(1.8)
        gray = ImageEnhance.Sharpness(gray).enhance(1.5)
        gray = gray.filter(ImageFilter.SHARPEN)

        return gray

    def extract_text(self, image_path):
        if not self.tesseract_available:
            return ""

        try:
            processed = self.preprocess_image(image_path)

            texts = []

            for psm in (6, 11, 12):
                try:
                    text = pytesseract.image_to_string(
                        processed,
                        config=f"--psm {psm}"
                    )

                    if text and text.strip():
                        texts.append(text.strip())
                except Exception:
                    continue

            return "\n".join(texts)

        except Exception:
            return ""

    def extract_isbn(self, text):
        if not text:
            return ""

        normalized = text.upper()

        patterns = [
            r"ISBN(?:-1[03])?\s*[:\-]?\s*([0-9X][0-9X\-\s]{8,20}[0-9X])",
            r"\b(97[89][\-\s]?[0-9][0-9\-\s]{8,17}[0-9X])\b",
            r"\b([0-9][0-9\-\s]{8,15}[0-9X])\b",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, normalized)

            for match in matches:
                isbn = re.sub(r"[^0-9X]", "", match)

                if self.validate_isbn(isbn):
                    return isbn

        return ""

    def validate_isbn(self, isbn):
        isbn = re.sub(r"[^0-9Xx]", "", str(isbn))

        if len(isbn) == 10:
            digits = isbn.upper()

            total = 0

            for index, character in enumerate(digits):
                value = 10 if character == "X" else int(character)
                total += value * (10 - index)

            return total % 11 == 0

        if len(isbn) == 13 and isbn.isdigit():
            total = 0

            for index, digit in enumerate(isbn[:12]):
                weight = 1 if index % 2 == 0 else 3
                total += int(digit) * weight

            check_digit = (10 - (total % 10)) % 10

            return check_digit == int(isbn[12])

        return False

    def extract_year(self, text):
        if not text:
            return ""

        years = re.findall(
            r"\b(1[5-9]\d{2}|20\d{2}|21\d{2})\b",
            text
        )

        if not years:
            return ""

        # Prefer the latest plausible publication year.
        return max(years, key=int)

    def scan_images(self, front_path, back_path):
        front_text = self.extract_text(front_path)
        back_text = self.extract_text(back_path)

        combined_text = "\n".join(
            part for part in [
                front_text,
                back_text
            ]
            if part
        )

        return {
            "front_text": front_text,
            "back_text": back_text,
            "combined_text": combined_text,
            "isbn": self.extract_isbn(combined_text),
            "year": self.extract_year(combined_text),
        }


ocr_manager = OCRManager()
