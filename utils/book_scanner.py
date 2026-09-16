# utils/book_scanner.py

import json
import os
import re

from .ocr_manager import ocr_manager


def _clean_value(value):
    if value is None:
        return "Not detected"

    value = str(value).strip()

    if not value or value.lower() in {
        "none",
        "null",
        "unknown",
        "not found",
        "not available",
        "n/a",
    }:
        return "Not detected"

    return value


def _normalize_isbn(value):
    if not value:
        return "Not detected"

    isbn = re.sub(r"[^0-9Xx]", "", str(value))

    if len(isbn) in (10, 13):
        return isbn.upper()

    return _clean_value(value)


def _extract_json(text):
    if not text:
        return None

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None

    return None


def _fallback_from_ocr(ocr_data):
    combined = ocr_data.get("combined_text", "")

    isbn = ocr_data.get("isbn") or "Not detected"
    year = ocr_data.get("year") or "Not detected"

    lines = [
        line.strip()
        for line in combined.splitlines()
        if line.strip()
    ]

    title = "Not detected"
    author = "Not detected"
    publisher = "Not detected"
    category = "Not detected"
    edition = "Not detected"
    price = "Not detected"
    subtitle = "Not detected"

    for line in lines:
        lower = line.lower()

        if title == "Not detected" and len(line) > 3:
            if not any(
                keyword in lower
                for keyword in [
                    "isbn",
                    "publisher",
                    "edition",
                    "price",
                    "www.",
                    "http",
                    "copyright",
                ]
            ):
                title = line

        if author == "Not detected" and any(
            keyword in lower
            for keyword in [
                "author",
                "written by",
                "by ",
            ]
        ):
            value = re.sub(
                r"^(author|written by|by)\s*[:\-]?\s*",
                "",
                line,
                flags=re.IGNORECASE
            ).strip()

            if value:
                author = value

        if publisher == "Not detected" and "publisher" in lower:
            value = re.sub(
                r"^.*?publisher\s*[:\-]?\s*",
                "",
                line,
                flags=re.IGNORECASE
            ).strip()

            if value:
                publisher = value

        if edition == "Not detected" and "edition" in lower:
            match = re.search(
                r"([\w\-]+\s*edition)",
                line,
                re.IGNORECASE
            )

            if match:
                edition = match.group(1)

        if price == "Not detected":
            match = re.search(
                r"(?:₹|rs\.?|inr|\$|€|£)\s*[\d,]+(?:\.\d{1,2})?",
                line,
                re.IGNORECASE
            )

            if match:
                price = match.group(0)

    return {
        "title": title,
        "author": author,
        "subtitle": subtitle,
        "isbn": _normalize_isbn(isbn),
        "category": category,
        "publisher": publisher,
        "year": year,
        "edition": edition,
        "price": price,
    }


def _gemini_scan(ocr_data):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

        prompt = f"""
You are an expert library cataloguing system.

Extract book metadata from the OCR text below.

The OCR may contain errors. Use context to identify the correct
book information. Do not invent information.

Return ONLY valid JSON with exactly these keys:

title
author
subtitle
isbn
category
publisher
year
edition
price

Rules:
- title = actual book title.
- author = author name or names.
- subtitle = subtitle if clearly present.
- isbn = valid ISBN-10 or ISBN-13 if detected.
- category = academic/general subject category if identifiable.
- publisher = publisher name.
- year = publication year.
- edition = edition if explicitly detected.
- price = printed/list price if explicitly detected.
- If a field cannot be reliably detected, return "Not detected".
- Do not guess.
- Do not return explanations.
- Do not use markdown.

FRONT IMAGE OCR:
{ocr_data.get("front_text", "")}

BACK IMAGE OCR:
{ocr_data.get("back_text", "")}

COMBINED OCR:
{ocr_data.get("combined_text", "")}
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        result = _extract_json(
            getattr(response, "text", "")
        )

        if not isinstance(result, dict):
            return None

        return {
            "title": _clean_value(result.get("title")),
            "author": _clean_value(result.get("author")),
            "subtitle": _clean_value(result.get("subtitle")),
            "isbn": _normalize_isbn(result.get("isbn")),
            "category": _clean_value(result.get("category")),
            "publisher": _clean_value(result.get("publisher")),
            "year": _clean_value(result.get("year")),
            "edition": _clean_value(result.get("edition")),
            "price": _clean_value(result.get("price")),
        }

    except Exception:
        return None


def scan_book_images(front_path, back_path):
    if not os.path.exists(front_path):
        raise FileNotFoundError("Front book image not found.")

    if not os.path.exists(back_path):
        raise FileNotFoundError("Back book image not found.")

    ocr_data = ocr_manager.scan_images(
        front_path,
        back_path
    )

    fallback_data = _fallback_from_ocr(ocr_data)

    ai_data = _gemini_scan(ocr_data)

    if ai_data:
        result = ai_data.copy()

        for key in fallback_data:
            if (
                result.get(key) in
                (None, "", "Not detected")
                and fallback_data.get(key) not in
                (None, "", "Not detected")
            ):
                result[key] = fallback_data[key]
    else:
        result = fallback_data

    result["isbn"] = _normalize_isbn(
        result.get("isbn")
        or ocr_data.get("isbn")
    )

    if (
        result.get("year") in
        (None, "", "Not detected")
        and ocr_data.get("year")
    ):
        result["year"] = ocr_data["year"]

    return result


def scan_book(front_path, back_path):
    return scan_book_images(
        front_path,
        back_path
    )


extract_book_details = scan_book_images
