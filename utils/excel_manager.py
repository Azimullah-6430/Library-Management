import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

EXCEL_FILE = os.path.join(
    DATA_DIR,
    "library_books.xlsx"
)


HEADERS = [
    "Book ID",
    "Book Title",
    "Author",
    "Subtitle",
    "ISBN",
    "Category",
    "Publisher",
    "Publication Year",
    "Edition",
    "Price",
    "Total Copies",
    "Available Copies",
    "Borrowed Copies",
    "Shelf Number",
    "Front Image",
    "Back Image",
    "Date Added",
    "Scan Status",
]


# ============================================================
# EXCEL MANAGER
# ============================================================

class ExcelManager:

    def __init__(
        self,
        file_path: str = EXCEL_FILE
    ):
        self.file_path = file_path

        os.makedirs(
            os.path.dirname(
                self.file_path
            ),
            exist_ok=True
        )

        self.ensure_file()

    # ========================================================
    # CREATE / INITIALIZE FILE
    # ========================================================

    def ensure_file(self) -> None:

        if not os.path.exists(
            self.file_path
        ):

            self._create_workbook()

            return

        try:

            workbook = load_workbook(
                self.file_path
            )

            if "Books" not in workbook.sheetnames:

                worksheet = workbook.create_sheet(
                    "Books"
                )

                self._setup_worksheet(
                    worksheet
                )

                workbook.save(
                    self.file_path
                )

            else:

                worksheet = workbook["Books"]

                self._repair_headers(
                    worksheet
                )

                workbook.save(
                    self.file_path
                )

        except Exception:

            # If the existing workbook is corrupted,
            # create a fresh workbook.
            self._create_workbook()

    # ========================================================
    # CREATE WORKBOOK
    # ========================================================

    def _create_workbook(self) -> None:

        workbook = Workbook()

        worksheet = workbook.active

        worksheet.title = "Books"

        self._setup_worksheet(
            worksheet
        )

        workbook.save(
            self.file_path
        )

    # ========================================================
    # SETUP WORKSHEET
    # ========================================================

    def _setup_worksheet(
        self,
        worksheet
    ) -> None:

        for column_index, header in enumerate(
            HEADERS,
            start=1
        ):

            cell = worksheet.cell(
                row=1,
                column=column_index,
                value=header
            )

            cell.font = Font(
                bold=True
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

            cell.fill = PatternFill(
                fill_type="solid",
                fgColor="17324D"
            )

            # Make header text readable.
            cell.font = Font(
                bold=True,
                color="FFFFFF"
            )

        worksheet.freeze_panes = "A2"

        worksheet.auto_filter.ref = (
            f"A1:{get_column_letter(len(HEADERS))}1"
        )

        self._set_column_widths(
            worksheet
        )

    # ========================================================
    # REPAIR HEADERS
    # ========================================================

    def _repair_headers(
        self,
        worksheet
    ) -> None:

        existing_headers = [
            worksheet.cell(
                row=1,
                column=index
            ).value
            for index in range(
                1,
                len(HEADERS) + 1
            )
        ]

        if existing_headers != HEADERS:

            for index, header in enumerate(
                HEADERS,
                start=1
            ):

                worksheet.cell(
                    row=1,
                    column=index,
                    value=header
                )

        for index, header in enumerate(
            HEADERS,
            start=1
        ):

            cell = worksheet.cell(
                row=1,
                column=index
            )

            cell.font = Font(
                bold=True,
                color="FFFFFF"
            )

            cell.fill = PatternFill(
                fill_type="solid",
                fgColor="17324D"
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        worksheet.freeze_panes = "A2"

        worksheet.auto_filter.ref = (
            f"A1:{get_column_letter(len(HEADERS))}1"
        )

        self._set_column_widths(
            worksheet
        )

    # ========================================================
    # COLUMN WIDTHS
    # ========================================================

    def _set_column_widths(
        self,
        worksheet
    ) -> None:

        widths = {
            "A": 15,
            "B": 35,
            "C": 28,
            "D": 30,
            "E": 18,
            "F": 22,
            "G": 28,
            "H": 18,
            "I": 16,
            "J": 15,
            "K": 15,
            "L": 18,
            "M": 18,
            "N": 18,
            "O": 35,
            "P": 35,
            "Q": 22,
            "R": 18,
        }

        for column, width in widths.items():

            worksheet.column_dimensions[
                column
            ].width = width

    # ========================================================
    # LOAD WORKBOOK
    # ========================================================

    def _load(self):

        self.ensure_file()

        return load_workbook(
            self.file_path
        )

    # ========================================================
    # SAVE WORKBOOK
    # ========================================================

    def _save(
        self,
        workbook
    ) -> None:

        workbook.save(
            self.file_path
        )

    # ========================================================
    # ROW TO DICTIONARY
    # ========================================================

    def _row_to_dict(
        self,
        row
    ) -> Dict[str, Any]:

        book = {}

        for index, header in enumerate(
            HEADERS
        ):

            value = row[index]

            if value is None:
                value = ""

            book[header] = value

        return book

    # ========================================================
    # DICTIONARY TO APPLICATION FORMAT
    # ========================================================

    def normalize_book(
        self,
        book: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {
            "id": book.get(
                "Book ID",
                ""
            ),
            "title": book.get(
                "Book Title",
                ""
            ),
            "author": book.get(
                "Author",
                ""
            ),
            "subtitle": book.get(
                "Subtitle",
                ""
            ),
            "isbn": book.get(
                "ISBN",
                ""
            ),
            "category": book.get(
                "Category",
                ""
            ),
            "publisher": book.get(
                "Publisher",
                ""
            ),
            "year": book.get(
                "Publication Year",
                ""
            ),
            "edition": book.get(
                "Edition",
                ""
            ),
            "price": book.get(
                "Price",
                ""
            ),
            "copies": book.get(
                "Total Copies",
                1
            ),
            "available": book.get(
                "Available Copies",
                1
            ),
            "borrowed": book.get(
                "Borrowed Copies",
                0
            ),
            "shelf": book.get(
                "Shelf Number",
                ""
            ),
            "front_image": book.get(
                "Front Image",
                ""
            ),
            "back_image": book.get(
                "Back Image",
                ""
            ),
            "date_added": book.get(
                "Date Added",
                ""
            ),
            "scan_status": book.get(
                "Scan Status",
                ""
            ),
        }

    # ========================================================
    # GET ALL BOOKS
    # ========================================================

    def get_all_books(
        self
    ) -> List[Dict[str, Any]]:

        workbook = self._load()

        worksheet = workbook["Books"]

        books = []

        for row in worksheet.iter_rows(
            min_row=2,
            values_only=True
        ):

            if not any(
                value is not None
                and str(value).strip()
                for value in row
            ):
                continue

            raw_book = self._row_to_dict(
                row
            )

            books.append(
                self.normalize_book(
                    raw_book
                )
            )

        workbook.close()

        return books

    # ========================================================
    # GET BOOK BY ID
    # ========================================================

    def get_book_by_id(
        self,
        book_id: str
    ) -> Optional[Dict[str, Any]]:

        if not book_id:
            return None

        books = self.get_all_books()

        for book in books:

            if str(
                book.get("id", "")
            ).strip().lower() == str(
                book_id
            ).strip().lower():

                return book

        return None

    # ========================================================
    # GET BOOK BY ISBN
    # ========================================================

    def get_book_by_isbn(
        self,
        isbn: str
    ) -> Optional[Dict[str, Any]]:

        if not isbn:
            return None

        cleaned_isbn = (
            str(isbn)
            .replace("-", "")
            .replace(" ", "")
            .strip()
            .upper()
        )

        books = self.get_all_books()

        for book in books:

            existing_isbn = (
                str(
                    book.get(
                        "isbn",
                        ""
                    )
                )
                .replace("-", "")
                .replace(" ", "")
                .strip()
                .upper()
            )

            if (
                existing_isbn
                and existing_isbn == cleaned_isbn
            ):
                return book

        return None

    # ========================================================
    # ADD BOOK
    # ========================================================

    def add_book(
        self,
        book: Dict[str, Any]
    ) -> bool:

        workbook = self._load()

        worksheet = workbook["Books"]

        values = {
            "Book ID": book.get(
                "id",
                ""
            ),
            "Book Title": book.get(
                "title",
                "Not detected"
            ),
            "Author": book.get(
                "author",
                "Not detected"
            ),
            "Subtitle": book.get(
                "subtitle",
                "Not detected"
            ),
            "ISBN": book.get(
                "isbn",
                "Not detected"
            ),
            "Category": book.get(
                "category",
                "Not detected"
            ),
            "Publisher": book.get(
                "publisher",
                "Not detected"
            ),
            "Publication Year": book.get(
                "year",
                "Not detected"
            ),
            "Edition": book.get(
                "edition",
                "Not detected"
            ),
            "Price": book.get(
                "price",
                "Not detected"
            ),
            "Total Copies": self._number(
                book.get(
                    "copies",
                    1
                ),
                1
            ),
            "Available Copies": self._number(
                book.get(
                    "available",
                    1
                ),
                1
            ),
            "Borrowed Copies": self._number(
                book.get(
                    "borrowed",
                    0
                ),
                0
            ),
            "Shelf Number": book.get(
                "shelf",
                ""
            ),
            "Front Image": book.get(
                "front_image",
                ""
            ),
            "Back Image": book.get(
                "back_image",
                ""
            ),
            "Date Added": book.get(
                "date_added",
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
            "Scan Status": book.get(
                "scan_status",
                "AI Scanned"
            ),
        }

        row_values = [
            values[header]
            for header in HEADERS
        ]

        worksheet.append(
            row_values
        )

        self._format_data_row(
            worksheet,
            worksheet.max_row
        )

        self._save(
            workbook
        )

        workbook.close()

        return True

    # ========================================================
    # UPDATE BOOK
    # ========================================================

    def update_book(
        self,
        book_id: str,
        book: Dict[str, Any]
    ) -> bool:

        workbook = self._load()

        worksheet = workbook["Books"]

        target_row = None

        for row_number in range(
            2,
            worksheet.max_row + 1
        ):

            current_id = worksheet.cell(
                row=row_number,
                column=1
            ).value

            if str(
                current_id
            ).strip().lower() == str(
                book_id
            ).strip().lower():

                target_row = row_number

                break

        if target_row is None:

            workbook.close()

            return False

        values = {
            "Book ID": book.get(
                "id",
                book_id
            ),
            "Book Title": book.get(
                "title",
                "Not detected"
            ),
            "Author": book.get(
                "author",
                "Not detected"
            ),
            "Subtitle": book.get(
                "subtitle",
                "Not detected"
            ),
            "ISBN": book.get(
                "isbn",
                "Not detected"
            ),
            "Category": book.get(
                "category",
                "Not detected"
            ),
            "Publisher": book.get(
                "publisher",
                "Not detected"
            ),
            "Publication Year": book.get(
                "year",
                "Not detected"
            ),
            "Edition": book.get(
                "edition",
                "Not detected"
            ),
            "Price": book.get(
                "price",
                "Not detected"
            ),
            "Total Copies": self._number(
                book.get(
                    "copies",
                    1
                ),
                1
            ),
            "Available Copies": self._number(
                book.get(
                    "available",
                    1
                ),
                1
            ),
            "Borrowed Copies": self._number(
                book.get(
                    "borrowed",
                    0
                ),
                0
            ),
            "Shelf Number": book.get(
                "shelf",
                ""
            ),
            "Front Image": book.get(
                "front_image",
                ""
            ),
            "Back Image": book.get(
                "back_image",
                ""
            ),
            "Date Added": book.get(
                "date_added",
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ),
            "Scan Status": book.get(
                "scan_status",
                "AI Scanned"
            ),
        }

        for column_index, header in enumerate(
            HEADERS,
            start=1
        ):

            worksheet.cell(
                row=target_row,
                column=column_index,
                value=values[header]
            )

        self._format_data_row(
            worksheet,
            target_row
        )

        self._save(
            workbook
        )

        workbook.close()

        return True

    # ========================================================
    # DELETE BOOK
    # ========================================================

    def delete_book(
        self,
        book_id: str
    ) -> bool:

        workbook = self._load()

        worksheet = workbook["Books"]

        target_row = None

        for row_number in range(
            2,
            worksheet.max_row + 1
        ):

            current_id = worksheet.cell(
                row=row_number,
                column=1
            ).value

            if str(
                current_id
            ).strip().lower() == str(
                book_id
            ).strip().lower():

                target_row = row_number

                break

        if target_row is None:

            workbook.close()

            return False

        worksheet.delete_rows(
            target_row,
            1
        )

        self._save(
            workbook
        )

        workbook.close()

        return True

    # ========================================================
    # SEARCH BOOKS
    # ========================================================

    def search_books(
        self,
        query: str
    ) -> List[Dict[str, Any]]:

        query = str(
            query or ""
        ).strip().lower()

        if not query:
            return self.get_all_books()

        books = self.get_all_books()

        results = []

        searchable_fields = [
            "id",
            "title",
            "author",
            "isbn",
            "category",
            "publisher",
            "year",
            "edition",
        ]

        for book in books:

            for field in searchable_fields:

                value = str(
                    book.get(
                        field,
                        ""
                    )
                ).lower()

                if query in value:

                    results.append(
                        book
                    )

                    break

        return results

    # ========================================================
    # CATEGORY FILTER
    # ========================================================

    def get_by_category(
        self,
        category: str
    ) -> List[Dict[str, Any]]:

        category = str(
            category or ""
        ).strip().lower()

        books = self.get_all_books()

        if not category:
            return books

        return [
            book
            for book in books
            if str(
                book.get(
                    "category",
                    ""
                )
            ).strip().lower()
            == category
        ]

    # ========================================================
    # AVAILABLE BOOKS
    # ========================================================

    def get_available_books(
        self
    ) -> List[Dict[str, Any]]:

        books = self.get_all_books()

        return [
            book
            for book in books
            if self._number(
                book.get(
                    "available",
                    0
                ),
                0
            ) > 0
        ]

    # ========================================================
    # BORROWED BOOKS
    # ========================================================

    def get_borrowed_books(
        self
    ) -> List[Dict[str, Any]]:

        books = self.get_all_books()

        return [
            book
            for book in books
            if self._number(
                book.get(
                    "borrowed",
                    0
                ),
                0
            ) > 0
        ]

    # ========================================================
    # STATISTICS
    # ========================================================

    def get_statistics(
        self
    ) -> Dict[str, Any]:

        books = self.get_all_books()

        total_titles = len(
            books
        )

        total_copies = sum(
            self._number(
                book.get(
                    "copies",
                    0
                ),
                0
            )
            for book in books
        )

        available_copies = sum(
            self._number(
                book.get(
                    "available",
                    0
                ),
                0
            )
            for book in books
        )

        borrowed_copies = sum(
            self._number(
                book.get(
                    "borrowed",
                    0
                ),
                0
            )
            for book in books
        )

        categories = set()

        for book in books:

            category = str(
                book.get(
                    "category",
                    ""
                )
            ).strip()

            if category:
                categories.add(
                    category
                )

        return {
            "total_titles": total_titles,
            "total_books": total_titles,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "borrowed_copies": borrowed_copies,
            "categories": len(
                categories
            ),
        }

    # ========================================================
    # FORMAT ROW
    # ========================================================

    def _format_data_row(
        self,
        worksheet,
        row_number: int
    ) -> None:

        for column_number in range(
            1,
            len(HEADERS) + 1
        ):

            cell = worksheet.cell(
                row=row_number,
                column=column_number
            )

            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

    # ========================================================
    # SAFE NUMBER
    # ========================================================

    def _number(
        self,
        value: Any,
        default: int = 0
    ) -> int:

        try:

            if value is None:
                return default

            if isinstance(
                value,
                str
            ):

                value = value.strip()

                if not value:
                    return default

                value = value.replace(
                    ",",
                    ""
                )

            return int(
                float(value)
            )

        except (
            TypeError,
            ValueError
        ):

            return default


# ============================================================
# GLOBAL INSTANCE
# ============================================================

excel_manager = ExcelManager()


# ============================================================
# COMPATIBILITY FUNCTIONS
# ============================================================

def get_all_books():
    return excel_manager.get_all_books()


def get_book_by_id(book_id):
    return excel_manager.get_book_by_id(
        book_id
    )


def get_book_by_isbn(isbn):
    return excel_manager.get_book_by_isbn(
        isbn
    )


def add_book(book):
    return excel_manager.add_book(
        book
    )


def update_book(book_id, book):
    return excel_manager.update_book(
        book_id,
        book
    )


def delete_book(book_id):
    return excel_manager.delete_book(
        book_id
    )


def search_books(query):
    return excel_manager.search_books(
        query
    )


def get_available_books():
    return excel_manager.get_available_books()


def get_borrowed_books():
    return excel_manager.get_borrowed_books()


def get_statistics():
    return excel_manager.get_statistics()
