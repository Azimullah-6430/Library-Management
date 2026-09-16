"""
Book Manager
------------
Main book-management logic for the
Crescent College Library Management System.
"""

import os
from datetime import datetime

from .excel_manager import (
    get_all_books,
    add_book,
    find_book,
    update_book,
    delete_book,
    get_statistics
)

from .image_manager import (
    save_image,
    delete_image
)


class BookManager:
    """
    Handles all book-related operations.
    """

    def __init__(self, excel_file, upload_folder):
        self.excel_file = excel_file
        self.upload_folder = upload_folder

    # ---------------------------------------------------------
    # GET ALL BOOKS
    # ---------------------------------------------------------

    def get_books(self):
        """
        Return all books from the Crescent College library.
        """

        return get_all_books(self.excel_file)

    # ---------------------------------------------------------
    # GET SINGLE BOOK
    # ---------------------------------------------------------

    def get_book(self, book_id):
        """
        Find a book using its Book ID / Accession Number.
        """

        return find_book(
            self.excel_file,
            book_id
        )

    # ---------------------------------------------------------
    # ADD NEW BOOK
    # ---------------------------------------------------------

    def create_book(
        self,
        book_id,
        title,
        author,
        isbn="",
        category="",
        publisher="",
        year="",
        copies=1,
        shelf="",
        cover_file=None
    ):
        """
        Create and store a new book.

        Returns:
            tuple:
                (True, book, message)
            or
                (False, None, error_message)
        """

        # Validate title
        if not title or not title.strip():
            return False, None, "Book title is required."

        # Validate author
        if not author or not author.strip():
            return False, None, "Author name is required."

        # Validate copies
        try:
            copies = int(copies)

            if copies < 1:
                return False, None, "Number of copies must be at least 1."

        except (ValueError, TypeError):
            return False, None, "Number of copies must be a valid number."

        # Check whether Book ID already exists
        existing_book = self.get_book(book_id)

        if existing_book:
            return False, None, "A book with this ID already exists."

        cover_filename = ""

        # Save cover image if uploaded
        if cover_file and cover_file.filename:

            success, filename, message = save_image(
                cover_file,
                self.upload_folder
            )

            if not success:
                return False, None, message

            cover_filename = filename

        # Current date
        date_added = datetime.now().strftime("%Y-%m-%d")

        # Create book dictionary
        book = {
            "book_id": book_id,
            "title": title.strip(),
            "author": author.strip(),
            "isbn": isbn.strip() if isbn else "",
            "category": category.strip() if category else "",
            "publisher": publisher.strip() if publisher else "",
            "year": year,
            "copies": copies,
            "available": copies,
            "shelf": shelf.strip() if shelf else "",
            "cover": cover_filename,
            "date_added": date_added
        }

        try:
            # Save to Excel
            add_book(
                self.excel_file,
                book
            )

        except Exception as error:

            # If Excel save fails, remove uploaded image
            if cover_filename:
                delete_image(
                    cover_filename,
                    self.upload_folder
                )

            return False, None, f"Unable to save book: {error}"

        return True, book, "Book added successfully."

    # ---------------------------------------------------------
    # UPDATE BOOK
    # ---------------------------------------------------------

    def edit_book(
        self,
        book_id,
        title,
        author,
        isbn="",
        category="",
        publisher="",
        year="",
        copies=1,
        shelf="",
        cover_file=None
    ):
        """
        Update an existing book.

        The available-copy count is adjusted based on
        the change in total copies.
        """

        # Find existing book
        existing_book = self.get_book(book_id)

        if not existing_book:
            return False, None, "Book not found."

        # Validate title
        if not title or not title.strip():
            return False, None, "Book title is required."

        # Validate author
        if not author or not author.strip():
            return False, None, "Author name is required."

        # Validate copies
        try:
            copies = int(copies)

            if copies < 1:
                return False, None, "Number of copies must be at least 1."

        except (ValueError, TypeError):
            return False, None, "Number of copies must be a valid number."

        # Existing total copies
        old_total = int(existing_book.get("copies", 0))

        # Existing available copies
        old_available = int(existing_book.get("available", 0))

        # Calculate borrowed copies
        borrowed_copies = old_total - old_available

        # New total cannot be less than currently borrowed copies
        if copies < borrowed_copies:
            return (
                False,
                None,
                f"Cannot reduce total copies below {borrowed_copies} "
                f"because those copies are currently borrowed."
            )

        # Calculate new available copies
        new_available = copies - borrowed_copies

        # Keep existing cover by default
        cover_filename = existing_book.get("cover", "")

        # Track old cover
        old_cover_filename = cover_filename

        # If librarian uploaded a new cover
        if cover_file and cover_file.filename:

            success, filename, message = save_image(
                cover_file,
                self.upload_folder
            )

            if not success:
                return False, None, message

            cover_filename = filename

        # Updated book dictionary
        updated_book = {
            "book_id": book_id,
            "title": title.strip(),
            "author": author.strip(),
            "isbn": isbn.strip() if isbn else "",
            "category": category.strip() if category else "",
            "publisher": publisher.strip() if publisher else "",
            "year": year,
            "copies": copies,
            "available": new_available,
            "shelf": shelf.strip() if shelf else "",
            "cover": cover_filename,
            "date_added": existing_book.get("date_added", "")
        }

        try:

            success = update_book(
                self.excel_file,
                book_id,
                updated_book
            )

            if not success:

                # Remove newly uploaded image if Excel update fails
                if (
                    cover_filename
                    and cover_filename != old_cover_filename
                ):
                    delete_image(
                        cover_filename,
                        self.upload_folder
                    )

                return False, None, "Unable to update the book."

        except Exception as error:

            # Remove newly uploaded image if something goes wrong
            if (
                cover_filename
                and cover_filename != old_cover_filename
            ):
                delete_image(
                    cover_filename,
                    self.upload_folder
                )

            return False, None, f"Unable to update book: {error}"

        # Delete old cover after successful update
        if (
            old_cover_filename
            and old_cover_filename != cover_filename
        ):
            delete_image(
                old_cover_filename,
                self.upload_folder
            )

        return True, updated_book, "Book updated successfully."

    # ---------------------------------------------------------
    # DELETE BOOK
    # ---------------------------------------------------------

    def remove_book(self, book_id):
        """
        Delete a book and its associated cover image.
        """

        book = self.get_book(book_id)

        if not book:
            return False, "Book not found."

        # Do not allow deletion if copies are currently borrowed
        total_copies = int(book.get("copies", 0))
        available_copies = int(book.get("available", 0))

        borrowed_copies = total_copies - available_copies

        if borrowed_copies > 0:
            return (
                False,
                "This book cannot be deleted because "
                f"{borrowed_copies} copy/copies are currently borrowed."
            )

        try:

            success = delete_book(
                self.excel_file,
                book_id
            )

            if not success:
                return False, "Unable to delete the book."

        except Exception as error:

            return False, f"Unable to delete book: {error}"

        # Delete cover image
        cover_filename = book.get("cover", "")

        if cover_filename:
            delete_image(
                cover_filename,
                self.upload_folder
            )

        return True, "Book deleted successfully."

    # ---------------------------------------------------------
    # SEARCH BOOKS
    # ---------------------------------------------------------

    def search_books(self, search_term=""):
        """
        Search books by:
        - Title
        - Author
        - ISBN
        - Category
        - Book ID
        """

        books = self.get_books()

        if not search_term:
            return books

        search_term = search_term.lower().strip()

        results = []

        for book in books:

            searchable_values = [
                book.get("book_id", ""),
                book.get("title", ""),
                book.get("author", ""),
                book.get("isbn", ""),
                book.get("category", ""),
                book.get("publisher", ""),
                book.get("shelf", "")
            ]

            searchable_text = " ".join(
                str(value).lower()
                for value in searchable_values
            )

            if search_term in searchable_text:
                results.append(book)

        return results

    # ---------------------------------------------------------
    # FILTER BY CATEGORY
    # ---------------------------------------------------------

    def get_books_by_category(self, category):
        """
        Return books belonging to a specific category.
        """

        books = self.get_books()

        if not category:
            return books

        category = category.lower().strip()

        return [
            book
            for book in books
            if str(book.get("category", "")).lower().strip()
            == category
        ]

    # ---------------------------------------------------------
    # GET STATISTICS
    # ---------------------------------------------------------

    def get_library_statistics(self):
        """
        Return dashboard statistics.
        """

        return get_statistics(
            self.excel_file
        )

    # ---------------------------------------------------------
    # GET CATEGORIES
    # ---------------------------------------------------------

    def get_categories(self):
        """
        Return unique book categories.
        """

        books = self.get_books()

        categories = set()

        for book in books:

            category = str(
                book.get("category", "")
            ).strip()

            if category:
                categories.add(category)

        return sorted(
            categories,
            key=str.lower
        )

    # ---------------------------------------------------------
    # GET AUTHORS
    # ---------------------------------------------------------

    def get_authors(self):
        """
        Return unique authors in the library catalog.
        """

        books = self.get_books()

        authors = set()

        for book in books:

            author = str(
                book.get("author", "")
            ).strip()

            if author:
                authors.add(author)

        return sorted(
            authors,
            key=str.lower
        )

    # ---------------------------------------------------------
    # GET AVAILABLE BOOKS
    # ---------------------------------------------------------

    def get_available_books(self):
        """
        Return books that currently have at least one
        available copy.
        """

        books = self.get_books()

        return [
            book
            for book in books
            if int(book.get("available", 0)) > 0
        ]

    # ---------------------------------------------------------
    # GET BORROWED BOOKS
    # ---------------------------------------------------------

    def get_borrowed_books(self):
        """
        Return books that currently have borrowed copies.
        """

        books = self.get_books()

        borrowed_books = []

        for book in books:

            total = int(book.get("copies", 0))
            available = int(book.get("available", 0))

            if total > available:
                borrowed_books.append(book)

        return borrowed_books
