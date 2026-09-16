"""
Crescent College Library Management System
-------------------------------------------
Main Flask application.
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory
)

from utils.book_manager import BookManager


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(
    BASE_DIR,
    "data"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads",
    "book_covers"
)

EXCEL_FILE = os.path.join(
    DATA_FOLDER,
    "library_books.xlsx"
)


# Create required folders
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Secret key for Flask sessions and flash messages
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "crescent-library-development-key"
)

# Maximum upload size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# ============================================================
# BOOK MANAGER
# ============================================================

book_manager = BookManager(
    excel_file=EXCEL_FILE,
    upload_folder=UPLOAD_FOLDER
)


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def index():

    statistics = book_manager.get_library_statistics()

    books = book_manager.get_books()

    # Most recently added books
    recent_books = list(reversed(books[-4:]))

    return render_template(
        "dashboard.html",
        total_books=statistics["total_books"],
        total_copies=statistics["total_copies"],
        available_copies=statistics["available_copies"],
        borrowed_copies=statistics["borrowed_copies"],
        books=books,
        recent_books=recent_books
    )


# ============================================================
# ADD BOOK
# ============================================================

@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        author = request.form.get(
            "author",
            ""
        ).strip()

        isbn = request.form.get(
            "isbn",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        publisher = request.form.get(
            "publisher",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        copies = request.form.get(
            "copies",
            "1"
        ).strip()

        shelf = request.form.get(
            "shelf",
            ""
        ).strip()

        cover_file = request.files.get(
            "cover"
        )

        # Generate next Book ID
        existing_books = book_manager.get_books()

        book_id = f"LIB{len(existing_books) + 1:04d}"

        success, book, message = book_manager.create_book(
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            publisher=publisher,
            year=year,
            copies=copies,
            shelf=shelf,
            cover_file=cover_file
        )

        if success:
            flash(
                f"Book {book_id} added successfully.",
                "success"
            )

            return redirect(
                url_for("books")
            )

        flash(
            message,
            "error"
        )

        return render_template(
            "add_book.html"
        )

    return render_template(
        "add_book.html"
    )


# ============================================================
# ALL BOOKS
# ============================================================

@app.route("/books")
def books():

    search_query = request.args.get(
        "search",
        ""
    ).strip()

    if search_query:
        all_books = book_manager.search_books(
            search_query
        )
    else:
        all_books = book_manager.get_books()

    return render_template(
        "books.html",
        books=all_books,
        search_query=search_query
    )


# ============================================================
# BOOK DETAILS
# ============================================================

@app.route("/book/<book_id>")
def book_details(book_id):

    book = book_manager.get_book(
        book_id
    )

    if not book:
        flash(
            "Book not found.",
            "error"
        )

        return redirect(
            url_for("books")
        )

    return render_template(
        "book_details.html",
        book=book
    )


# ============================================================
# EDIT BOOK
# ============================================================

@app.route(
    "/edit-book/<book_id>",
    methods=["GET", "POST"]
)
def edit_book(book_id):

    book = book_manager.get_book(
        book_id
    )

    if not book:
        flash(
            "Book not found.",
            "error"
        )

        return redirect(
            url_for("books")
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        author = request.form.get(
            "author",
            ""
        ).strip()

        isbn = request.form.get(
            "isbn",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        publisher = request.form.get(
            "publisher",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        copies = request.form.get(
            "copies",
            "1"
        ).strip()

        shelf = request.form.get(
            "shelf",
            ""
        ).strip()

        cover_file = request.files.get(
            "cover"
        )

        success, updated_book, message = book_manager.edit_book(
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            publisher=publisher,
            year=year,
            copies=copies,
            shelf=shelf,
            cover_file=cover_file
        )

        if success:

            flash(
                "Book information updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "book_details",
                    book_id=book_id
                )
            )

        flash(
            message,
            "error"
        )

        # Reload the latest book information
        book = book_manager.get_book(
            book_id
        )

    return render_template(
        "edit_book.html",
        book=book
    )


# ============================================================
# DELETE BOOK
# ============================================================

@app.route(
    "/delete-book/<book_id>",
    methods=["POST"]
)
def delete_book(book_id):

    success, message = book_manager.remove_book(
        book_id
    )

    if success:

        flash(
            message,
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for("books")
    )


# ============================================================
# BOOK COVER
# ============================================================

@app.route(
    "/uploads/book_covers/<filename>"
)
def uploaded_cover(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# SEARCH
# ============================================================

@app.route("/search")
def search():

    search_query = request.args.get(
        "q",
        ""
    ).strip()

    results = book_manager.search_books(
        search_query
    )

    return render_template(
        "books.html",
        books=results,
        search_query=search_query
    )


# ============================================================
# CATEGORY FILTER
# ============================================================

@app.route("/category/<category>")
def category_books(category):

    books = book_manager.get_books_by_category(
        category
    )

    return render_template(
        "books.html",
        books=books,
        search_query=""
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return {
        "status": "success",
        "application": "Crescent College Library Management System"
    }


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "Book-cover image must not exceed 5 MB.",
        "error"
    )

    return redirect(
        url_for("add_book")
    )


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "base.html"
    ), 404


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
