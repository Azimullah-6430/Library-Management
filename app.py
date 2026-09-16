import os
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


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "book_covers")

EXCEL_FILE = os.path.join(DATA_FOLDER, "library_books.xlsx")


# Create required folders automatically
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = "crescent-library-secret-key"

# Maximum uploaded file size = 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# ============================================================
# BOOK MANAGER
# ============================================================

book_manager = BookManager(
    excel_file=EXCEL_FILE,
    upload_folder=UPLOAD_FOLDER
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_book_id():
    """
    Generate the next unique Book ID.

    Example:
    LIB0001
    LIB0002
    LIB0003
    """

    books = book_manager.get_books()

    highest_number = 0

    for book in books:
        book_id = str(book.get("book_id", ""))

        if book_id.startswith("LIB"):
            try:
                number = int(book_id.replace("LIB", ""))
                highest_number = max(highest_number, number)
            except ValueError:
                continue

    return f"LIB{highest_number + 1:04d}"


def get_form_book_data(form):
    """
    Read book information from the submitted form.
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
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    statistics = book_manager.get_library_statistics()
    books = book_manager.get_books()

    return render_template(
        "dashboard.html",
        statistics=statistics,
        books=books,
        current_date=datetime.now().strftime("%d %B %Y")
    )


# ============================================================
# ALL BOOKS
# ============================================================

@app.route("/books")
def books():

    search_query = request.args.get("search", "").strip()

    if search_query:
        book_list = book_manager.search_books(search_query)
    else:
        book_list = book_manager.get_books()

    return render_template(
        "books.html",
        books=book_list,
        search_query=search_query
    )


# ============================================================
# ADD BOOK
# ============================================================

@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":

        try:

            book_data = get_form_book_data(request.form)

            # Generate unique Book ID
            book_id = generate_book_id()

            book_data["book_id"] = book_id

            # Cover image
            cover_file = request.files.get("cover")

            # Create book
            success, message = book_manager.create_book(
                book_data,
                cover_file
            )

            if success:
                flash(message, "success")
                return redirect(url_for("books"))

            flash(message, "danger")

        except Exception as error:

            print("ADD BOOK ERROR:", error)

            flash(
                f"Unable to add book: {str(error)}",
                "danger"
            )

    return render_template("add_book.html")


# ============================================================
# BOOK DETAILS
# ============================================================

@app.route("/book/<book_id>")
def book_details(book_id):

    book = book_manager.get_book(book_id)

    if not book:

        flash("Book not found.", "danger")

        return redirect(url_for("books"))

    return render_template(
        "book_details.html",
        book=book
    )


# ============================================================
# EDIT BOOK
# ============================================================

@app.route("/edit-book/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    book = book_manager.get_book(book_id)

    if not book:

        flash("Book not found.", "danger")

        return redirect(url_for("books"))

    if request.method == "POST":

        try:

            book_data = get_form_book_data(request.form)

            # Keep the existing Book ID
            book_data["book_id"] = book_id

            # Existing cover
            book_data["cover"] = book.get("cover", "")

            # New cover
            cover_file = request.files.get("cover")

            success, message = book_manager.edit_book(
                book_id,
                book_data,
                cover_file
            )

            if success:

                flash(message, "success")

                return redirect(
                    url_for(
                        "book_details",
                        book_id=book_id
                    )
                )

            flash(message, "danger")

        except Exception as error:

            print("EDIT BOOK ERROR:", error)

            flash(
                f"Unable to update book: {str(error)}",
                "danger"
            )

    # Refresh book data
    book = book_manager.get_book(book_id)

    return render_template(
        "edit_book.html",
        book=book
    )


# ============================================================
# DELETE BOOK
# ============================================================

@app.route("/delete-book/<book_id>", methods=["POST", "GET"])
def delete_book(book_id):

    try:

        success, message = book_manager.remove_book(book_id)

        if success:
            flash(message, "success")
        else:
            flash(message, "danger")

    except Exception as error:

        print("DELETE BOOK ERROR:", error)

        flash(
            f"Unable to delete book: {str(error)}",
            "danger"
        )

    return redirect(url_for("books"))


# ============================================================
# SEARCH BOOKS
# ============================================================

@app.route("/search")
def search():

    query = request.args.get("q", "").strip()

    if query:

        results = book_manager.search_books(query)

    else:

        results = book_manager.get_books()

    return jsonify(results)


# ============================================================
# CATEGORY FILTER
# ============================================================

@app.route("/category/<path:category>")
def category_books(category):

    books = book_manager.get_books_by_category(category)

    return render_template(
        "books.html",
        books=books,
        search_query="",
        selected_category=category
    )


# ============================================================
# AVAILABLE BOOKS
# ============================================================

@app.route("/available-books")
def available_books():

    books = book_manager.get_available_books()

    return render_template(
        "books.html",
        books=books,
        search_query=""
    )


# ============================================================
# BORROWED BOOKS
# ============================================================

@app.route("/borrowed-books")
def borrowed_books():

    books = book_manager.get_borrowed_books()

    return render_template(
        "books.html",
        books=books,
        search_query=""
    )


# ============================================================
# LIBRARY STATISTICS API
# ============================================================

@app.route("/api/statistics")
def statistics_api():

    statistics = book_manager.get_library_statistics()

    return jsonify(statistics)


# ============================================================
# BOOKS API
# ============================================================

@app.route("/api/books")
def books_api():

    books = book_manager.get_books()

    return jsonify(books)


# ============================================================
# SINGLE BOOK API
# ============================================================

@app.route("/api/books/<book_id>")
def book_api(book_id):

    book = book_manager.get_book(book_id)

    if not book:

        return jsonify({
            "success": False,
            "message": "Book not found"
        }), 404

    return jsonify({
        "success": True,
        "book": book
    })


# ============================================================
# SERVE BOOK COVER IMAGES
# ============================================================

@app.route("/uploads/book_covers/<filename>")
def uploaded_book_cover(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "application": "Crescent College Library Management System",
        "timestamp": datetime.now().isoformat()
    })


# ============================================================
# 404 ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "base.html"
    ), 404


# ============================================================
# 413 ERROR HANDLER
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "The uploaded image is too large. Maximum size is 5 MB.",
        "danger"
    )

    return redirect(
        request.referrer or url_for("add_book")
    )


# ============================================================
# 500 ERROR HANDLER
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    print("SERVER ERROR:", error)

    return """
    <h1>Internal Server Error</h1>
    <p>Something went wrong while processing your request.</p>
    <p>Please check the terminal for more details.</p>
    """, 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CRESCENT COLLEGE LIBRARY MANAGEMENT SYSTEM")
    print("=" * 60)

    print(f"Database File : {EXCEL_FILE}")
    print(f"Upload Folder : {UPLOAD_FOLDER}")
    print("Server        : http://127.0.0.1:5000")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
