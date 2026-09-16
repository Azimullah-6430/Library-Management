import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils.excel_manager import excel_manager


# ============================================================
# BOOK MANAGER
# ============================================================

class BookManager:

    def __init__(self):
        self.excel = excel_manager

    # ========================================================
    # GENERATE BOOK ID
    # ========================================================

    def generate_book_id(
        self
    ) -> str:

        books = self.get_all_books()

        highest_number = 0

        for book in books:

            book_id = str(
                book.get(
                    "id",
                    ""
                )
            ).strip().upper()

            match = re.search(
                r"(\d+)$",
                book_id
            )

            if match:

                number = int(
                    match.group(1)
                )

                highest_number = max(
                    highest_number,
                    number
                )

        return (
            f"LIB-{highest_number + 1:05d}"
        )

    # ========================================================
    # GET ALL BOOKS
    # ========================================================

    def get_all_books(
        self
    ) -> List[Dict[str, Any]]:

        return self.excel.get_all_books()

    # ========================================================
    # GET BOOK
    # ========================================================

    def get_book(
        self,
        book_id: str
    ) -> Optional[Dict[str, Any]]:

        return self.excel.get_book_by_id(
            book_id
        )

    # ========================================================
    # GET BOOK BY ISBN
    # ========================================================

    def get_book_by_isbn(
        self,
        isbn: str
    ) -> Optional[Dict[str, Any]]:

        return self.excel.get_book_by_isbn(
            self.clean_isbn(isbn)
        )

    # ========================================================
    # CLEAN ISBN
    # ========================================================

    def clean_isbn(
        self,
        isbn: Any
    ) -> str:

        if isbn is None:
            return ""

        return re.sub(
            r"[^0-9Xx]",
            "",
            str(isbn)
        ).upper()

    # ========================================================
    # CLEAN VALUE
    # ========================================================

    def clean_value(
        self,
        value: Any,
        default: str = ""
    ) -> str:

        if value is None:
            return default

        value = str(
            value
        ).strip()

        if not value:
            return default

        return value

    # ========================================================
    # NORMALIZE SCANNED DATA
    # ========================================================

    def normalize_scanned_data(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:

        if not isinstance(
            data,
            dict
        ):
            data = {}

        return {
            "title": self.clean_value(
                data.get("title"),
                "Not detected"
            ),
            "author": self.clean_value(
                data.get("author"),
                "Not detected"
            ),
            "subtitle": self.clean_value(
                data.get("subtitle"),
                "Not detected"
            ),
            "isbn": self.clean_isbn(
                data.get("isbn")
            ) or "Not detected",
            "category": self.clean_value(
                data.get("category"),
                "Not detected"
            ),
            "publisher": self.clean_value(
                data.get("publisher"),
                "Not detected"
            ),
            "year": self.clean_value(
                data.get("year"),
                "Not detected"
            ),
            "edition": self.clean_value(
                data.get("edition"),
                "Not detected"
            ),
            "price": self.clean_value(
                data.get("price"),
                "Not detected"
            ),
        }

    # ========================================================
    # CHECK REQUIRED SCAN
    # ========================================================

    def validate_scanned_data(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:

        normalized = self.normalize_scanned_data(
            data
        )

        # At least the title should be detected.
        # The application should not silently create
        # completely empty book records.
        title = normalized.get(
            "title",
            ""
        )

        if (
            not title
            or title.lower() == "not detected"
        ):

            return {
                "valid": False,
                "data": normalized,
                "error": (
                    "Book title could not be "
                    "detected from the uploaded images."
                ),
            }

        return {
            "valid": True,
            "data": normalized,
            "error": "",
        }

    # ========================================================
    # DUPLICATE ISBN CHECK
    # ========================================================

    def is_duplicate_isbn(
        self,
        isbn: str,
        exclude_book_id: str = ""
    ) -> bool:

        isbn = self.clean_isbn(
            isbn
        )

        if not isbn:
            return False

        existing = self.get_book_by_isbn(
            isbn
        )

        if not existing:
            return False

        existing_id = str(
            existing.get(
                "id",
                ""
            )
        ).strip().lower()

        excluded_id = str(
            exclude_book_id or ""
        ).strip().lower()

        if (
            excluded_id
            and existing_id == excluded_id
        ):
            return False

        return True

    # ========================================================
    # ADD SCANNED BOOK
    # ========================================================

    def add_scanned_book(
        self,
        scanned_data: Dict[str, Any],
        front_image: str,
        back_image: str
    ) -> Dict[str, Any]:

        validation = self.validate_scanned_data(
            scanned_data
        )

        if not validation["valid"]:

            return {
                "success": False,
                "error": validation["error"],
            }

        data = validation["data"]

        isbn = self.clean_isbn(
            data.get(
                "isbn",
                ""
            )
        )

        if isbn and isbn != "NOT DETECTED":

            if self.is_duplicate_isbn(
                isbn
            ):

                existing = self.get_book_by_isbn(
                    isbn
                )

                return {
                    "success": False,
                    "error": (
                        "A book with this ISBN "
                        "already exists in the library."
                    ),
                    "duplicate": True,
                    "existing_book": existing,
                }

        book_id = self.generate_book_id()

        book = {
            "id": book_id,
            "title": data.get(
                "title",
                "Not detected"
            ),
            "author": data.get(
                "author",
                "Not detected"
            ),
            "subtitle": data.get(
                "subtitle",
                "Not detected"
            ),
            "isbn": (
                isbn
                if isbn
                else "Not detected"
            ),
            "category": data.get(
                "category",
                "Not detected"
            ),
            "publisher": data.get(
                "publisher",
                "Not detected"
            ),
            "year": data.get(
                "year",
                "Not detected"
            ),
            "edition": data.get(
                "edition",
                "Not detected"
            ),
            "price": data.get(
                "price",
                "Not detected"
            ),
            "copies": 1,
            "available": 1,
            "borrowed": 0,
            "shelf": "",
            "front_image": front_image or "",
            "back_image": back_image or "",
            "date_added": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "scan_status": "AI Scanned",
        }

        try:

            saved = self.excel.add_book(
                book
            )

            if not saved:

                return {
                    "success": False,
                    "error": (
                        "The book could not be "
                        "saved to the library."
                    ),
                }

            return {
                "success": True,
                "book": book,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

    # ========================================================
    # UPDATE BOOK
    # ========================================================

    def update_book(
        self,
        book_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:

        existing = self.get_book(
            book_id
        )

        if not existing:

            return {
                "success": False,
                "error": "Book not found.",
            }

        normalized = self.normalize_scanned_data(
            data
        )

        isbn = self.clean_isbn(
            normalized.get(
                "isbn",
                ""
            )
        )

        if isbn and isbn != "NOT DETECTED":

            if self.is_duplicate_isbn(
                isbn,
                exclude_book_id=book_id
            ):

                return {
                    "success": False,
                    "error": (
                        "Another book with this "
                        "ISBN already exists."
                    ),
                }

        updated = {
            "id": book_id,
            "title": normalized.get(
                "title",
                existing.get(
                    "title",
                    "Not detected"
                )
            ),
            "author": normalized.get(
                "author",
                existing.get(
                    "author",
                    "Not detected"
                )
            ),
            "subtitle": normalized.get(
                "subtitle",
                existing.get(
                    "subtitle",
                    "Not detected"
                )
            ),
            "isbn": (
                isbn
                if isbn
                else existing.get(
                    "isbn",
                    "Not detected"
                )
            ),
            "category": normalized.get(
                "category",
                existing.get(
                    "category",
                    "Not detected"
                )
            ),
            "publisher": normalized.get(
                "publisher",
                existing.get(
                    "publisher",
                    "Not detected"
                )
            ),
            "year": normalized.get(
                "year",
                existing.get(
                    "year",
                    "Not detected"
                )
            ),
            "edition": normalized.get(
                "edition",
                existing.get(
                    "edition",
                    "Not detected"
                )
            ),
            "price": normalized.get(
                "price",
                existing.get(
                    "price",
                    "Not detected"
                )
            ),
            "copies": existing.get(
                "copies",
                1
            ),
            "available": existing.get(
                "available",
                1
            ),
            "borrowed": existing.get(
                "borrowed",
                0
            ),
            "shelf": existing.get(
                "shelf",
                ""
            ),
            "front_image": existing.get(
                "front_image",
                ""
            ),
            "back_image": existing.get(
                "back_image",
                ""
            ),
            "date_added": existing.get(
                "date_added",
                ""
            ),
            "scan_status": "AI Scanned",
        }

        try:

            updated_successfully = (
                self.excel.update_book(
                    book_id,
                    updated
                )
            )

            if not updated_successfully:

                return {
                    "success": False,
                    "error": (
                        "Book could not be updated."
                    ),
                }

            return {
                "success": True,
                "book": updated,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

    # ========================================================
    # DELETE BOOK
    # ========================================================

    def delete_book(
        self,
        book_id: str
    ) -> Dict[str, Any]:

        existing = self.get_book(
            book_id
        )

        if not existing:

            return {
                "success": False,
                "error": "Book not found.",
            }

        try:

            deleted = self.excel.delete_book(
                book_id
            )

            if not deleted:

                return {
                    "success": False,
                    "error": (
                        "Book could not be deleted."
                    ),
                }

            return {
                "success": True,
                "book": existing,
            }

        except Exception as error:

            return {
                "success": False,
                "error": str(error),
            }

    # ========================================================
    # SEARCH
    # ========================================================

    def search(
        self,
        query: str
    ) -> List[Dict[str, Any]]:

        return self.excel.search_books(
            query
        )

    # ========================================================
    # CATEGORY
    # ========================================================

    def category(
        self,
        category: str
    ) -> List[Dict[str, Any]]:

        return self.excel.get_by_category(
            category
        )

    # ========================================================
    # AVAILABLE
    # ========================================================

    def available(
        self
    ) -> List[Dict[str, Any]]:

        return self.excel.get_available_books()

    # ========================================================
    # BORROWED
    # ========================================================

    def borrowed(
        self
    ) -> List[Dict[str, Any]]:

        return self.excel.get_borrowed_books()

    # ========================================================
    # STATISTICS
    # ========================================================

    def statistics(
        self
    ) -> Dict[str, Any]:

        return self.excel.get_statistics()


# ============================================================
# GLOBAL INSTANCE
# ============================================================

book_manager = BookManager()


# ============================================================
# COMPATIBILITY FUNCTIONS
# ============================================================

def get_all_books():
    return book_manager.get_all_books()


def get_book(
    book_id
):
    return book_manager.get_book(
        book_id
    )


def get_book_by_id(
    book_id
):
    return book_manager.get_book(
        book_id
    )


def get_book_by_isbn(
    isbn
):
    return book_manager.get_book_by_isbn(
        isbn
    )


def generate_book_id():
    return book_manager.generate_book_id()


def add_scanned_book(
    scanned_data,
    front_image,
    back_image
):
    return book_manager.add_scanned_book(
        scanned_data,
        front_image,
        back_image
    )


def update_book(
    book_id,
    data
):
    return book_manager.update_book(
        book_id,
        data
    )


def delete_book(
    book_id
):
    return book_manager.delete_book(
        book_id
    )


def search_books(
    query
):
    return book_manager.search(
        query
    )


def get_statistics():
    return book_manager.statistics()
