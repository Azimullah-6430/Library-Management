import os
import traceback
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    jsonify
)

from utils.book_manager import BookManager
from utils.excel_manager import create_excel_file


# ============================================================
# PATH CONFIGURATION
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


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# CREATE EXCEL DATABASE IF IT DOES NOT EXIST
# ============================================================

try:
    create_excel_file(EXCEL_FILE)
    print("Excel database initialized successfully.")
except Exception as error:
    print("WARNING: Could not initialize Excel database.")
    print("Error:", error)
    traceback.print_exc()


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "crescent-library-development-secret"
)

# Maximum upload size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# BOOK MANAGER
# ============================================================

book_manager = BookManager(
    excel_file=EXCEL_FILE,
    upload_folder=UPLOAD_FOLDER
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def generate_book_id():
    """
    Generate a unique Book ID.

    Examples:
        LIB0001
        LIB0002
        LIB0003

    Deleted book IDs will not be reused.
    """

    try:
        books = book_manager.get_books()
    except Exception:
        books = []

    highest_number = 0

    for book in books:

        book_id = str(
            book.get("book_id", "")
        ).strip().upper()

        if not book_id.startswith("LIB"):
            continue

        number_part = book_id[3:]

        try:
            number = int(number_part)

            if number > highest_number:
                highest_number = number

        except ValueError:
            continue

    return f"LIB{highest_number + 1:04d}"


def get_book_form_data(form):
    """
    Read and clean book information from HTML form.
    """

    return {
        "title": form.get("title", "").strip(),
        "author": form.get("author", "").strip(),
        "isbn": form.get("isbn", "").strip(),
        "category": form.get("category", "").strip(),
        "publisher": form.get("publisher", "").strip(),
        "year": form.get("year", "").strip(),
        "copies": form.get("copies", "").strip(),
        "shelf": form.get("shelf", "").strip()
    }


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    try:

        statistics = book_manager.get_library_statistics()

        books = book_manager.get_books()

        return render_template(
            "dashboard.html",
            statistics=statistics,
            books=books,
            current_date=datetime.now().strftime(
                "%d %B %Y"
            )
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("DASHBOARD ERROR")
        print("=" * 70)

        print("Error:", error)

        traceback.print_exc()

        print("=" * 70 + "\n")

        return """
        <h1>Crescent College Library</h1>
        <h2>Dashboard Error</h2>

        <p>
            The application is running, but the dashboard
            encountered an error.
        </p>

        <p>
            Check the terminal for the complete traceback.
        </p>

        """, 500


# ============================================================
# ALL BOOKS
# ============================================================

@app.route("/books")
def books_page():

    try:

        search_query = request.args.get(
            "search",
            ""
        ).strip()

        if search_query:

            books = book_manager.search_books(
                search_query
            )

        else:

            books = book_manager.get_books()

        return render_template(
            "books.html",
            books=books,
            search_query=search_query
        )

    except Exception as error:

        print("\nBOOKS PAGE ERROR")
        traceback.print_exc()

        flash(
            f"Unable to load books: {error}",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )


# ============================================================
# ADD BOOK
# ============================================================

@app.route(
    "/add-book",
    methods=["GET", "POST"]
)
def add_book():

    if request.method == "GET":

        return render_template(
            "add_book.html"
        )

    try:

        # ----------------------------------------------------
        # GET FORM DATA
        # ----------------------------------------------------

        book_data = get_book_form_data(
            request.form
        )

        # ----------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # ----------------------------------------------------

        if not book_data["title"]:

            flash(
                "Book title is required.",
                "danger"
            )

            return render_template(
                "add_book.html"
            )

        if not book_data["author"]:

            flash(
                "Author name is required.",
                "danger"
            )

            return render_template(
                "add_book.html"
            )

        if not book_data["copies"]:

            flash(
                "Number of copies is required.",
                "danger"
            )

            return render_template(
                "add_book.html"
            )

        # ----------------------------------------------------
        # GENERATE BOOK ID
        # ----------------------------------------------------

        book_data["book_id"] = generate_book_id()

        # ----------------------------------------------------
        # GET COVER IMAGE
        # ----------------------------------------------------

        cover_file = request.files.get(
            "cover"
        )

        # ----------------------------------------------------
        # CREATE BOOK
        # ----------------------------------------------------

        result = book_manager.create_book(
            book_data,
            cover_file
        )

        # BookManager returns:
        # (success, message)

        success, message = result

        if success:

            flash(
                message,
                "success"
            )

            return redirect(
                url_for("books_page")
            )

        flash(
            message,
            "danger"
        )

        return render_template(
            "add_book.html"
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("ADD BOOK ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70 + "\n")

        flash(
            f"Unable to add book: {error}",
            "danger"
        )

        return render_template(
            "add_book.html"
        )


# ============================================================
# BOOK DETAILS
# ============================================================

@app.route(
    "/book/<book_id>"
)
def book_details(book_id):

    try:

        book = book_manager.get_book(
            book_id
        )

        if not book:

            flash(
                "Book not found.",
                "danger"
            )

            return redirect(
                url_for("books_page")
            )

        return render_template(
            "book_details.html",
            book=book
        )

    except Exception as error:

        print("\nBOOK DETAILS ERROR")
        traceback.print_exc()

        flash(
            f"Unable to load book: {error}",
            "danger"
        )

        return redirect(
            url_for("books_page")
        )


# ============================================================
# EDIT BOOK
# ============================================================

@app.route(
    "/edit-book/<book_id>",
    methods=["GET", "POST"]
)
def edit_book(book_id):

    try:

        # ----------------------------------------------------
        # FIND BOOK
        # ----------------------------------------------------

        book = book_manager.get_book(
            book_id
        )

        if not book:

            flash(
                "Book not found.",
                "danger"
            )

            return redirect(
                url_for("books_page")
            )

        # ----------------------------------------------------
        # DISPLAY EDIT PAGE
        # ----------------------------------------------------

        if request.method == "GET":

            return render_template(
                "edit_book.html",
                book=book
            )

        # ----------------------------------------------------
        # GET UPDATED DATA
        # ----------------------------------------------------

        book_data = get_book_form_data(
            request.form
        )

        book_data["book_id"] = book_id

        # Preserve existing cover
        book_data["cover"] = book.get(
            "cover",
            ""
        )

        # ----------------------------------------------------
        # NEW COVER
        # ----------------------------------------------------

        cover_file = request.files.get(
            "cover"
        )

        # ----------------------------------------------------
        # UPDATE BOOK
        # ----------------------------------------------------

        success, message = book_manager.edit_book(
            book_id,
            book_data,
            cover_file
        )

        if success:

            flash(
                message,
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
            "danger"
        )

        updated_book = book_manager.get_book(
            book_id
        )

        return render_template(
            "edit_book.html",
            book=updated_book
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("EDIT BOOK ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70 + "\n")

        flash(
            f"Unable to update book: {error}",
            "danger"
        )

        return redirect(
            url_for(
                "book_details",
                book_id=book_id
            )
        )


# ============================================================
# DELETE BOOK
# ============================================================

@app.route(
    "/delete-book/<book_id>",
    methods=["POST", "GET"]
)
def delete_book(book_id):

    try:

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
                "danger"
            )

    except Exception as error:

        print("\nDELETE BOOK ERROR")
        traceback.print_exc()

        flash(
            f"Unable to delete book: {error}",
            "danger"
        )

    return redirect(
        url_for("books_page")
    )


# ============================================================
# SEARCH API
# ============================================================

@app.route("/search")
def search_books():

    try:

        query = request.args.get(
            "q",
            ""
        ).strip()

        if query:

            results = book_manager.search_books(
                query
            )

        else:

            results = book_manager.get_books()

        return jsonify(results)

    except Exception as error:

        print("\nSEARCH ERROR")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# CATEGORY FILTER
# ============================================================

@app.route(
    "/category/<path:category>"
)
def category_books(category):

    try:

        books = book_manager.get_books_by_category(
            category
        )

        return render_template(
            "books.html",
            books=books,
            search_query="",
            selected_category=category
        )

    except Exception as error:

        print("\nCATEGORY ERROR")
        traceback.print_exc()

        flash(
            f"Unable to load category: {error}",
            "danger"
        )

        return redirect(
            url_for("books_page")
        )


# ============================================================
# AVAILABLE BOOKS
# ============================================================

@app.route("/available-books")
def available_books():

    try:

        books = book_manager.get_available_books()

        return render_template(
            "books.html",
            books=books,
            search_query=""
        )

    except Exception as error:

        print("\nAVAILABLE BOOKS ERROR")
        traceback.print_exc()

        flash(
            f"Unable to load available books: {error}",
            "danger"
        )

        return redirect(
            url_for("books_page")
        )


# ============================================================
# BORROWED BOOKS
# ============================================================

@app.route("/borrowed-books")
def borrowed_books():

    try:

        books = book_manager.get_borrowed_books()

        return render_template(
            "books.html",
            books=books,
            search_query=""
        )

    except Exception as error:

        print("\nBORROWED BOOKS ERROR")
        traceback.print_exc()

        flash(
            f"Unable to load borrowed books: {error}",
            "danger"
        )

        return redirect(
            url_for("books_page")
        )


# ============================================================
# STATISTICS API
# ============================================================

@app.route("/api/statistics")
def statistics_api():

    try:

        statistics = book_manager.get_library_statistics()

        return jsonify({
            "success": True,
            "statistics": statistics
        })

    except Exception as error:

        print("\nSTATISTICS API ERROR")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# BOOKS API
# ============================================================

@app.route("/api/books")
def books_api():

    try:

        books = book_manager.get_books()

        return jsonify({
            "success": True,
            "books": books
        })

    except Exception as error:

        print("\nBOOKS API ERROR")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# SINGLE BOOK API
# ============================================================

@app.route(
    "/api/books/<book_id>"
)
def single_book_api(book_id):

    try:

        book = book_manager.get_book(
            book_id
        )

        if not book:

            return jsonify({
                "success": False,
                "message": "Book not found."
            }), 404

        return jsonify({
            "success": True,
            "book": book
        })

    except Exception as error:

        print("\nSINGLE BOOK API ERROR")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# BOOK COVER IMAGE ROUTE
# ============================================================

@app.route(
    "/uploads/book_covers/<path:filename>"
)
def uploaded_book_cover(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health_check():

    return jsonify({
        "status": "healthy",
        "application": "Crescent College Library Management System",
        "database": "Excel",
        "timestamp": datetime.now().isoformat()
    })


# ============================================================
# 404 ERROR
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <!DOCTYPE html>

    <html>

    <head>
        <title>Page Not Found</title>

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                text-align: center;
                padding: 80px;
            }

            .box {
                background: white;
                max-width: 600px;
                margin: auto;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 5px 25px rgba(0,0,0,0.08);
            }

            h1 {
                font-size: 60px;
                margin: 0;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 24px;
                background: #111827;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }

        </style>

    </head>

    <body>

        <div class="box">

            <h1>404</h1>

            <h2>Page Not Found</h2>

            <p>
                The requested page does not exist.
            </p>

            <a href="/">
                Go to Dashboard
            </a>

        </div>

    </body>

    </html>
    """, 404


# ============================================================
# FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "The uploaded file is too large. Maximum size is 5 MB.",
        "danger"
    )

    return redirect(
        request.referrer or
        url_for("add_book")
    )


# ============================================================
# INTERNAL SERVER ERROR
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    print("\n" + "=" * 70)
    print("FLASK INTERNAL SERVER ERROR")
    print("=" * 70)

    print("Error:", error)

    print("\nFULL TRACEBACK:")

    traceback.print_exc()

    print("=" * 70 + "\n")

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Crescent Library - Server Error
        </title>

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                color: #222;
                padding: 50px;
            }

            .error-box {
                max-width: 750px;
                margin: auto;
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 5px 25px rgba(0,0,0,0.08);
            }

            h1 {
                color: #c62828;
            }

            .message {
                background: #fff3f3;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            }

            a {
                display: inline-block;
                margin-top: 20px;
                padding: 12px 24px;
                background: #111827;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }

        </style>

    </head>

    <body>

        <div class="error-box">

            <h1>
                Internal Server Error
            </h1>

            <p>
                The Crescent College Library application
                encountered an unexpected error.
            </p>

            <div class="message">

                <strong>
                    Please check the terminal for the
                    complete Python traceback.
                </strong>

            </div>

            <a href="/">
                Return to Dashboard
            </a>

        </div>

    </body>

    </html>
    """, 500


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("CRESCENT COLLEGE LIBRARY MANAGEMENT SYSTEM")
    print("=" * 70)
    print()
    print("Application : Flask")
    print("Database    : Excel")
    print(f"Excel File  : {EXCEL_FILE}")
    print(f"Uploads     : {UPLOAD_FOLDER}")
    print()
    print("Local URL   : http://127.0.0.1:5000")
    print("Health URL  : http://127.0.0.1:5000/health")
    print()
    print("=" * 70)
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
