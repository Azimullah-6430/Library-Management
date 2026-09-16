# utils/book_manager.py

import re
from datetime import datetime

from .excel_manager import excel_manager


class BookManager:
    def __init__(self):
        self.excel = excel_manager

    def _clean(self, value):
        if value is None:
            return "Not detected"

        value = str(value).strip()

        if not value or value.lower() in {
            "none",
            "null",
            "unknown",
            "not found",
            "not detected",
            "n/a",
        }:
            return "Not detected"

        return value

    def _normalize_isbn(self, isbn):
        if not isbn:
            return ""

        isbn = str(isbn).strip()
        digits = re.sub(r"[^0-9Xx]", "", isbn)

        if len(digits) == 13:
            return digits

        if len(digits) == 10:
            return digits.upper()

        return isbn

    def _normalize_year(self, year):
        if not year:
            return "Not detected"

        match = re.search(r"\b(1[5-9]\d{2}|20\d{2}|21\d{2})\b", str(year))

        if match:
            return match.group(1)

        return "Not detected"

    def _normalize_price(self, price):
        if not price:
            return "Not detected"

        value = str(price).strip()

        match = re.search(
            r"(?:₹|Rs\.?|INR|\$|€|£)?\s*[\d,]+(?:\.\d{1,2})?",
            value,
            re.IGNORECASE,
        )

        return match.group(0).strip() if match else self._clean(price)

    def normalize_book_data(self, data):
        data = data or {}

        title = self._clean(
            data.get("title")
            or data.get("book_title")
            or data.get("Book Title")
        )

        author = self._clean(
            data.get("author")
            or data.get("authors")
            or data.get("Author")
        )

        subtitle = self._clean(
            data.get("subtitle")
            or data.get("Subtitle")
        )

        isbn = self._normalize_isbn(
            data.get("isbn")
            or data.get("ISBN")
        )

        category = self._clean(
            data.get("category")
            or data.get("Category")
        )

        publisher = self._clean(
            data.get("publisher")
            or data.get("Publisher")
        )

        year = self._normalize_year(
            data.get("year")
            or data.get("publication_year")
            or data.get("Publication Year")
        )

        edition = self._clean(
            data.get("edition")
            or data.get("Edition")
        )

        price = self._normalize_price(
            data.get("price")
            or data.get("Price")
        )

        return {
            "title": title,
            "author": author,
            "subtitle": subtitle,
            "isbn": isbn,
            "category": category,
            "publisher": publisher,
            "year": year,
            "edition": edition,
            "price": price,
        }

    def _isbn_exists(self, isbn):
        if not isbn or isbn == "Not detected":
            return False

        books = self.excel.get_all_books()

        normalized = self._normalize_isbn(isbn)

        for book in books:
            existing = self._normalize_isbn(book.get("ISBN", ""))

            if existing and existing == normalized:
                return True

        return False

    def generate_book_id(self):
        books = self.excel.get_all_books()

        highest = 0

        for book in books:
            book_id = str(book.get("Book ID", ""))

            match = re.search(r"LIB-(\d+)", book_id)

            if match:
                highest = max(highest, int(match.group(1)))

        return f"LIB-{highest + 1:05d}"

    def add_scanned_book(
        self,
        scanned_data,
        front_image="",
        back_image="",
    ):
        book = self.normalize_book_data(scanned_data)

        if book["title"] == "Not detected":
            raise ValueError(
                "Book title could not be detected from the uploaded images."
            )

        if book["isbn"] != "Not detected" and self._isbn_exists(book["isbn"]):
            raise ValueError(
                f"A book with ISBN {book['isbn']} already exists."
            )

        book_id = self.generate_book_id()

        book_record = {
            "Book ID": book_id,
            "Book Title": book["title"],
            "Author": book["author"],
            "Subtitle": book["subtitle"],
            "ISBN": book["isbn"],
            "Category": book["category"],
            "Publisher": book["publisher"],
            "Publication Year": book["year"],
            "Edition": book["edition"],
            "Price": book["price"],
            "Total Copies": 1,
            "Available Copies": 1,
            "Borrowed Copies": 0,
            "Shelf Number": "",
            "Front Image": front_image,
            "Back Image": back_image,
            "Date Added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Scan Status": "AI Scanned",
        }

        self.excel.add_book(book_record)

        return book_record

    def get_all_books(self):
        return self.excel.get_all_books()

    def get_book(self, book_id):
        return self.excel.get_book(book_id)

    def update_book(self, book_id, data):
        return self.excel.update_book(book_id, data)

    def delete_book(self, book_id):
        return self.excel.delete_book(book_id)

    def search_books(self, query):
        return self.excel.search_books(query)

    def get_categories(self):
        return self.excel.get_categories()

    def get_available_books(self):
        return self.excel.get_available_books()

    def get_borrowed_books(self):
        return self.excel.get_borrowed_books()

    def get_statistics(self):
        return self.excel.get_statistics()


book_manager = BookManager()
