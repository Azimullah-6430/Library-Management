import os
import re
import json
import base64
from typing import Dict, Any

from PIL import Image


# ============================================================
# BOOK SCANNER
# ============================================================

BOOK_FIELDS = [
    "title",
    "author",
    "subtitle",
    "isbn",
    "category",
    "publisher",
    "year",
    "edition",
    "price",
]


def empty_book_data() -> Dict[str, str]:
    return {
        field: ""
        for field in BOOK_FIELDS
    }


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, (list, tuple)):
        value = " ".join(
            str(item) for item in value
        )

    return str(value).strip()


def clean_isbn(value: Any) -> str:
    value = clean_text(value)

    value = re.sub(
        r"(?i)^isbn[\s:\-]*",
        "",
        value
    )

    value = re.sub(
        r"[^0-9Xx]",
        "",
        value
    )

    if len(value) in (10, 13):
        return value.upper()

    return ""


def clean_year(value: Any) -> str:
    value = clean_text(value)

    match = re.search(
        r"\b(?:19|20)\d{2}\b",
        value
    )

    if match:
        return match.group(0)

    return ""


def clean_price(value: Any) -> str:
    value = clean_text(value)

    if not value:
        return ""

    match = re.search(
        r"(?:₹|Rs\.?|INR)?\s*[\d,]+(?:\.\d{1,2})?",
        value,
        re.IGNORECASE
    )

    if match:
        return match.group(0).strip()

    return value


def normalize_result(data: Dict[str, Any]) -> Dict[str, str]:
    result = empty_book_data()

    if not isinstance(data, dict):
        return result

    aliases = {
        "title": [
            "title",
            "book_title",
            "book title",
            "name",
        ],
        "author": [
            "author",
            "authors",
            "writer",
        ],
        "subtitle": [
            "subtitle",
            "sub_title",
            "sub title",
        ],
        "isbn": [
            "isbn",
            "isbn10",
            "isbn13",
            "isbn_10",
            "isbn_13",
        ],
        "category": [
            "category",
            "subject",
            "genre",
        ],
        "publisher": [
            "publisher",
            "publishing_company",
            "publishing company",
            "publisher_name",
        ],
        "year": [
            "year",
            "publication_year",
            "publication year",
            "published_year",
        ],
        "edition": [
            "edition",
        ],
        "price": [
            "price",
            "mrp",
            "maximum_retail_price",
            "maximum retail price",
        ],
    }

    normalized_keys = {
        re.sub(
            r"[^a-z0-9]",
            "",
            str(key).lower()
        ): value
        for key, value in data.items()
    }

    for field, possible_keys in aliases.items():

        for key in possible_keys:

            normalized_key = re.sub(
                r"[^a-z0-9]",
                "",
                key.lower()
            )

            if normalized_key in normalized_keys:

                value = normalized_keys[
                    normalized_key
                ]

                result[field] = clean_text(value)

                break

    result["isbn"] = clean_isbn(
        result["isbn"]
    )

    result["year"] = clean_year(
        result["year"]
    )

    result["price"] = clean_price(
        result["price"]
    )

    return result


# ============================================================
# OCR SUPPORT
# ============================================================

def run_local_ocr(image_path: str) -> str:
    """
    Optional local OCR.

    Uses pytesseract when it is installed.
    The application continues to work if it is unavailable.
    """

    try:
        import pytesseract
    except ImportError:
        return ""

    if not image_path or not os.path.exists(image_path):
        return ""

    try:

        image = Image.open(image_path)

        image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image
        )

        return text.strip()

    except Exception:
        return ""


# ============================================================
# ISBN DETECTION
# ============================================================

def detect_isbn(text: str) -> str:
    if not text:
        return ""

    text = re.sub(
        r"(?i)isbn[\s:\-]*",
        " ",
        text
    )

    candidates = re.findall(
        r"(?:97[89][\-\s]?)?"
        r"\d(?:[\d\-\s]{8,16})[\dXx]",
        text
    )

    for candidate in candidates:

        isbn = re.sub(
            r"[^0-9Xx]",
            "",
            candidate
        )

        if len(isbn) == 13:
            return isbn

        if len(isbn) == 10:
            return isbn.upper()

    return ""


# ============================================================
# BASIC METADATA FALLBACK
# ============================================================

def fallback_metadata(
    front_text: str,
    back_text: str
) -> Dict[str, str]:

    result = empty_book_data()

    combined_text = (
        f"{front_text}\n{back_text}"
    ).strip()

    result["isbn"] = detect_isbn(
        combined_text
    )

    year_match = re.search(
        r"\b(?:19|20)\d{2}\b",
        combined_text
    )

    if year_match:
        result["year"] = year_match.group(0)

    return result


# ============================================================
# OPTIONAL GEMINI EXTRACTION
# ============================================================

def extract_with_gemini(
    front_path: str,
    back_path: str,
    front_text: str,
    back_text: str
) -> Dict[str, str]:

    api_key = os.environ.get(
        "GEMINI_API_KEY"
    )

    if not api_key:
        return {}

    try:
        from google import genai
    except ImportError:
        return {}

    try:

        client = genai.Client(
            api_key=api_key
        )

        front_file = client.files.upload(
            file=front_path
        )

        back_file = client.files.upload(
            file=back_path
        )

        prompt = """
You are a professional library cataloguing assistant.

Analyze the FRONT and BACK images of the same physical book.

Extract ONLY information that is actually visible or strongly supported
by the images/OCR.

Do NOT invent, guess, hallucinate, or complete missing information.

Return ONLY valid JSON using exactly these fields:

{
  "title": "",
  "author": "",
  "subtitle": "",
  "isbn": "",
  "category": "",
  "publisher": "",
  "year": "",
  "edition": "",
  "price": ""
}

Rules:

1. Title must come primarily from the front cover.
2. Author must come from visible book information.
3. ISBN should preferably come from the back cover or barcode area.
4. Publisher should come from the copyright/publisher information.
5. Publication year must be a visible publication/copyright year.
6. Edition must only be returned when visible.
7. Price must only be returned when visible.
8. Category should describe the academic/book subject only when it can
   reasonably be determined from the book.
9. Do not confuse a price, page number, phone number, or other number
   with an ISBN.
10. Do not fabricate missing values.
11. Return an empty string for information that cannot be determined.
12. Preserve the actual spelling of the title and author.
"""

        response = client.models.generate_content(
            model=os.environ.get(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            ),
            contents=[
                prompt,
                front_file,
                back_file,
            ],
        )

        text = getattr(
            response,
            "text",
            ""
        )

        if not text:
            return {}

        text = text.strip()

        if text.startswith("```"):
            text = re.sub(
                r"^```(?:json)?",
                "",
                text,
                flags=re.IGNORECASE
            )

            text = re.sub(
                r"```$",
                "",
                text
            ).strip()

        parsed = json.loads(text)

        return normalize_result(
            parsed
        )

    except Exception:
        return {}


# ============================================================
# MAIN SCANNER
# ============================================================

def scan_book_images(
    front_path: str,
    back_path: str
) -> Dict[str, str]:

    result = empty_book_data()

    if not os.path.exists(front_path):
        raise FileNotFoundError(
            "Front book image was not found."
        )

    if not os.path.exists(back_path):
        raise FileNotFoundError(
            "Back book image was not found."
        )

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    front_text = run_local_ocr(
        front_path
    )

    back_text = run_local_ocr(
        back_path
    )

    # --------------------------------------------------------
    # Basic fallback extraction
    # --------------------------------------------------------

    result.update(
        fallback_metadata(
            front_text,
            back_text
        )
    )

    # --------------------------------------------------------
    # AI extraction
    # --------------------------------------------------------

    ai_result = extract_with_gemini(
        front_path,
        back_path,
        front_text,
        back_text
    )

    if ai_result:

        for field in BOOK_FIELDS:

            value = ai_result.get(
                field,
                ""
            )

            if value:
                result[field] = value

    # --------------------------------------------------------
    # Final ISBN validation
    # --------------------------------------------------------

    if not result.get("isbn"):

        result["isbn"] = detect_isbn(
            f"{front_text}\n{back_text}"
        )

    result["isbn"] = clean_isbn(
        result.get("isbn", "")
    )

    # --------------------------------------------------------
    # Final year validation
    # --------------------------------------------------------

    if result.get("year"):

        result["year"] = clean_year(
            result["year"]
        )

    # --------------------------------------------------------
    # Final price normalization
    # --------------------------------------------------------

    if result.get("price"):

        result["price"] = clean_price(
            result["price"]
        )

    return result


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

scan_book = scan_book_images
extract_book_details = scan_book_images
