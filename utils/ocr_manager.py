import os
import re
from typing import List, Dict, Any

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


# ============================================================
# OCR MANAGER
# ============================================================

class OCRManager:
    """
    Handles image preprocessing and OCR extraction.

    Tesseract is used when available.
    The module is designed so the rest of the application
    does not crash if OCR is temporarily unavailable.
    """

    def __init__(self):
        self.tesseract_available = False
        self.pytesseract = None

        try:
            import pytesseract

            self.pytesseract = pytesseract

            # Optional custom Tesseract executable path.
            custom_path = os.environ.get(
                "TESSERACT_CMD"
            )

            if custom_path:
                self.pytesseract.pytesseract.tesseract_cmd = (
                    custom_path
                )

            self.pytesseract.get_tesseract_version()

            self.tesseract_available = True

        except Exception:
            self.tesseract_available = False

    # ========================================================
    # IMAGE PREPROCESSING
    # ========================================================

    def preprocess_image(
        self,
        image_path: str
    ) -> Image.Image:

        if not image_path:
            raise ValueError(
                "Image path is required."
            )

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(
            image_path
        )

        image = ImageOps.exif_transpose(
            image
        )

        image = image.convert(
            "RGB"
        )

        # Keep very large images manageable.
        max_dimension = 2400

        width, height = image.size

        if max(width, height) > max_dimension:

            scale = (
                max_dimension /
                max(width, height)
            )

            image = image.resize(
                (
                    int(width * scale),
                    int(height * scale)
                ),
                Image.Resampling.LANCZOS
            )

        # Upscale smaller book-cover images.
        width, height = image.size

        if max(width, height) < 1600:

            scale = 1600 / max(
                width,
                height
            )

            image = image.resize(
                (
                    int(width * scale),
                    int(height * scale)
                ),
                Image.Resampling.LANCZOS
            )

        # Improve contrast.
        image = ImageEnhance.Contrast(
            image
        ).enhance(1.5)

        # Improve sharpness.
        image = ImageEnhance.Sharpness(
            image
        ).enhance(1.8)

        return image

    # ========================================================
    # GRAYSCALE IMAGE
    # ========================================================

    def create_grayscale(
        self,
        image: Image.Image
    ) -> Image.Image:

        gray = ImageOps.grayscale(
            image
        )

        gray = ImageEnhance.Contrast(
            gray
        ).enhance(1.8)

        gray = gray.filter(
            ImageFilter.SHARPEN
        )

        return gray

    # ========================================================
    # OCR SINGLE IMAGE
    # ========================================================

    def extract_text(
        self,
        image_path: str
    ) -> str:

        if not self.tesseract_available:
            return ""

        try:

            image = self.preprocess_image(
                image_path
            )

            gray = self.create_grayscale(
                image
            )

            text_results = []

            # Multiple OCR configurations improve
            # recognition of covers and back covers.
            configurations = [
                "--psm 6",
                "--psm 11",
                "--psm 12",
            ]

            for config in configurations:

                try:

                    text = self.pytesseract.image_to_string(
                        gray,
                        config=config,
                        lang="eng"
                    )

                    if text:
                        text_results.append(
                            text
                        )

                except Exception:
                    continue

            return self._merge_ocr_results(
                text_results
            )

        except Exception:
            return ""

    # ========================================================
    # OCR WITH DATA
    # ========================================================

    def extract_data(
        self,
        image_path: str
    ) -> List[Dict[str, Any]]:

        if not self.tesseract_available:
            return []

        try:

            image = self.preprocess_image(
                image_path
            )

            gray = self.create_grayscale(
                image
            )

            data = self.pytesseract.image_to_data(
                gray,
                config="--psm 11",
                lang="eng",
                output_type=self.pytesseract.Output.DICT
            )

            results = []

            total = len(
                data.get("text", [])
            )

            for index in range(total):

                text = str(
                    data["text"][index]
                ).strip()

                if not text:
                    continue

                try:
                    confidence = float(
                        data["conf"][index]
                    )
                except Exception:
                    confidence = 0.0

                results.append(
                    {
                        "text": text,
                        "confidence": confidence,
                        "left": data["left"][index],
                        "top": data["top"][index],
                        "width": data["width"][index],
                        "height": data["height"][index],
                        "block": data["block_num"][index],
                        "line": data["line_num"][index],
                    }
                )

            return results

        except Exception:
            return []

    # ========================================================
    # FRONT + BACK OCR
    # ========================================================

    def scan_images(
        self,
        front_path: str,
        back_path: str
    ) -> Dict[str, str]:

        front_text = self.extract_text(
            front_path
        )

        back_text = self.extract_text(
            back_path
        )

        return {
            "front_text": front_text,
            "back_text": back_text,
            "combined_text": (
                f"{front_text}\n{back_text}"
            ).strip()
        }

    # ========================================================
    # ISBN EXTRACTION
    # ========================================================

    def extract_isbn(
        self,
        text: str
    ) -> str:

        if not text:
            return ""

        text = text.replace(
            "\n",
            " "
        )

        # First search for explicitly labelled ISBNs.
        labelled_patterns = [
            r"ISBN(?:-10|-13)?\s*[:\-]?\s*"
            r"([0-9Xx][0-9Xx\-\s]{8,20}[0-9Xx])",

            r"ISBN(?:-10|-13)?\s*"
            r"([0-9]{9}[0-9Xx])",

            r"ISBN(?:-10|-13)?\s*"
            r"(97[89][0-9]{10})",
        ]

        for pattern in labelled_patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                isbn = self._clean_isbn(
                    match
                )

                if self.validate_isbn(
                    isbn
                ):
                    return isbn

        # General ISBN-13 candidates.
        candidates = re.findall(
            r"(97[89][\-\s]?[0-9\-\s]{10,17})",
            text
        )

        for candidate in candidates:

            isbn = self._clean_isbn(
                candidate
            )

            if self.validate_isbn(
                isbn
            ):
                return isbn

        # General ISBN-10 candidates.
        candidates = re.findall(
            r"\b[0-9]{9}[0-9Xx]\b",
            text
        )

        for candidate in candidates:

            isbn = self._clean_isbn(
                candidate
            )

            if self.validate_isbn(
                isbn
            ):
                return isbn

        return ""

    # ========================================================
    # ISBN VALIDATION
    # ========================================================

    def validate_isbn(
        self,
        isbn: str
    ) -> bool:

        isbn = self._clean_isbn(
            isbn
        )

        # ISBN-10
        if len(isbn) == 10:

            total = 0

            for index, character in enumerate(
                isbn
            ):

                if character.upper() == "X":

                    if index != 9:
                        return False

                    value = 10

                elif character.isdigit():

                    value = int(
                        character
                    )

                else:
                    return False

                total += (
                    (10 - index) * value
                )

            return total % 11 == 0

        # ISBN-13
        if len(isbn) == 13:

            if not isbn.isdigit():
                return False

            if not isbn.startswith(
                ("978", "979")
            ):
                return False

            total = 0

            for index, character in enumerate(
                isbn[:12]
            ):

                value = int(
                    character
                )

                if index % 2 == 0:
                    total += value

                else:
                    total += value * 3

            check_digit = (
                10 - (total % 10)
            ) % 10

            return check_digit == int(
                isbn[12]
            )

        return False

    # ========================================================
    # CLEAN ISBN
    # ========================================================

    def _clean_isbn(
        self,
        value: str
    ) -> str:

        if not value:
            return ""

        value = re.sub(
            r"[^0-9Xx]",
            "",
            str(value)
        )

        return value.upper()

    # ========================================================
    # MERGE OCR RESULTS
    # ========================================================

    def _merge_ocr_results(
        self,
        results: List[str]
    ) -> str:

        if not results:
            return ""

        lines = []

        seen = set()

        for result in results:

            for line in result.splitlines():

                line = re.sub(
                    r"\s+",
                    " ",
                    line
                ).strip()

                if not line:
                    continue

                key = line.lower()

                if key in seen:
                    continue

                seen.add(key)

                lines.append(
                    line
                )

        return "\n".join(
            lines
        )

    # ========================================================
    # CLEAN OCR TEXT
    # ========================================================

    def clean_text(
        self,
        text: str
    ) -> str:

        if not text:
            return ""

        text = text.replace(
            "\r",
            "\n"
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()


# ============================================================
# SINGLETON
# ============================================================

ocr_manager = OCRManager()


# ============================================================
# SIMPLE FUNCTION API
# ============================================================

def extract_text_from_image(
    image_path: str
) -> str:

    return ocr_manager.extract_text(
        image_path
    )


def extract_ocr_data(
    image_path: str
) -> List[Dict[str, Any]]:

    return ocr_manager.extract_data(
        image_path
    )


def extract_isbn_from_text(
    text: str
) -> str:

    return ocr_manager.extract_isbn(
        text
    )


def validate_isbn(
    isbn: str
) -> bool:

    return ocr_manager.validate_isbn(
        isbn
    )


def scan_book_images_ocr(
    front_path: str,
    back_path: str
) -> Dict[str, str]:

    return ocr_manager.scan_images(
        front_path,
        back_path
    )
