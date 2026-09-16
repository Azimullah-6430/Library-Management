# utils/excel_manager.py

import os
from openpyxl import Workbook, load_workbook


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


class ExcelManager:
    def __init__(self, file_path="data/library_books.xlsx"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        directory = os.path.dirname(self.file_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.file_path):
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "Books"

            for column, header in enumerate(HEADERS, start=1):
                worksheet.cell(
                    row=1,
                    column=column,
                    value=header
                )

            worksheet.freeze_panes = "A2"
            workbook.save(self.file_path)

    def _load(self):
        return load_workbook(self.file_path)

    def _row_to_dict(self, worksheet, row):
        return {
            worksheet.cell(1, column).value:
            worksheet.cell(row, column).value
            for column in range(1, worksheet.max_column + 1)
        }

    def get_all_books(self):
        workbook = self._load()
        worksheet = workbook["Books"]

        books = []

        for row in range(2, worksheet.max_row + 1):
            values = [
                worksheet.cell(row, column).value
                for column in range(1, worksheet.max_column + 1)
            ]

            if any(value not in (None, "") for value in values):
                books.append(self._row_to_dict(worksheet, row))

        workbook.close()

        return books

    def get_book(self, book_id):
        workbook = self._load()
        worksheet = workbook["Books"]

        for row in range(2, worksheet.max_row + 1):
            value = worksheet.cell(row, 1).value

            if str(value).strip() == str(book_id).strip():
                book = self._row_to_dict(worksheet, row)
                workbook.close()
                return book

        workbook.close()
        return None

    def add_book(self, book):
        workbook = self._load()
        worksheet = workbook["Books"]

        row = worksheet.max_row + 1

        for column, header in enumerate(HEADERS, start=1):
            worksheet.cell(
                row=row,
                column=column,
                value=book.get(header, "")
            )

        workbook.save(self.file_path)
        workbook.close()

        return True

    def update_book(self, book_id, data):
        workbook = self._load()
        worksheet = workbook["Books"]

        for row in range(2, worksheet.max_row + 1):
            current_id = worksheet.cell(row, 1).value

            if str(current_id).strip() == str(book_id).strip():

                for column, header in enumerate(HEADERS, start=1):
                    if header in data:
                        worksheet.cell(
                            row=row,
                            column=column,
                            value=data[header]
                        )

                workbook.save(self.file_path)
                workbook.close()

                return True

        workbook.close()
        return False

    def delete_book(self, book_id):
        workbook = self._load()
        worksheet = workbook["Books"]

        for row in range(2, worksheet.max_row + 1):
            current_id = worksheet.cell(row, 1).value

            if str(current_id).strip() == str(book_id).strip():
                worksheet.delete_rows(row, 1)

                workbook.save(self.file_path)
                workbook.close()

                return True

        workbook.close()
        return False

    def search_books(self, query):
        query = str(query or "").strip().lower()

        if not query:
            return self.get_all_books()

        books = self.get_all_books()
        results = []

        searchable_fields = [
            "Book ID",
            "Book Title",
            "Author",
            "ISBN",
            "Category",
            "Publisher",
            "Edition",
            "Shelf Number",
        ]

        for book in books:
            for field in searchable_fields:
                value = str(book.get(field, "") or "").lower()

                if query in value:
                    results.append(book)
                    break

        return results

    def get_categories(self):
        categories = set()

        for book in self.get_all_books():
            category = str(
                book.get("Category", "") or ""
            ).strip()

            if category and category.lower() != "not detected":
                categories.add(category)

        return sorted(categories)

    def get_available_books(self):
        books = self.get_all_books()

        return [
            book for book in books
            if self._to_number(book.get("Available Copies", 0)) > 0
        ]

    def get_borrowed_books(self):
        books = self.get_all_books()

        return [
            book for book in books
            if self._to_number(book.get("Borrowed Copies", 0)) > 0
        ]

    def _to_number(self, value):
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            try:
                return float(value or 0)
            except (TypeError, ValueError):
                return 0

    def get_statistics(self):
        books = self.get_all_books()

        total_titles = len(books)

        total_copies = sum(
            self._to_number(book.get("Total Copies"))
            for book in books
        )

        available_copies = sum(
            self._to_number(book.get("Available Copies"))
            for book in books
        )

        borrowed_copies = sum(
            self._to_number(book.get("Borrowed Copies"))
            for book in books
        )

        categories = set()

        for book in books:
            category = str(
                book.get("Category", "") or ""
            ).strip()

            if category and category.lower() != "not detected":
                categories.add(category)

        return {
            "total_books": total_titles,
            "total_titles": total_titles,
            "total_copies": total_copies,
            "available_copies": available_copies,
            "borrowed_copies": borrowed_copies,
            "categories": len(categories),
        }


excel_manager = ExcelManager()
