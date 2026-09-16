from flask import Flask, render_template, request, redirect, url_for
from openpyxl import Workbook, load_workbook
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
import os
import uuid

# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "book_covers")

EXCEL_FILE = os.path.join(DATA_FOLDER, "library_books.xlsx")

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# CHECK ALLOWED IMAGE
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )

# ============================================================
# CREATE EXCEL DATABASE
# ============================================================

def create_excel_file():

    if not os.path.exists(EXCEL_FILE):

        workbook = Workbook()

        sheet = workbook.active
        sheet.title = "Books"

        headers = [
            "Book ID",
            "Book Title",
            "Author",
            "ISBN",
            "Category",
            "Publisher",
            "Publication Year",
            "Total Copies",
            "Available Copies",
            "Shelf Number",
            "Cover Image",
            "Date Added"
        ]

        sheet.append(headers)

        workbook.save(EXCEL_FILE)

# ============================================================
# GET ALL BOOKS
# ============================================================

def get_all_books():

    create_excel_file()

    workbook = load_workbook(EXCEL_FILE)

    sheet = workbook["Books"]

    books = []

    for row in sheet.iter_rows(
        min_row=2,
        values_only=True
    ):

        if not row[0]:
            continue

        book = {
            "book_id": row[0],
            "title": row[1],
            "author": row[2],
            "isbn": row[3],
            "category": row[4],
            "publisher": row[5],
            "year": row[6],
            "total_copies": row[7],
            "available_copies": row[8],
            "shelf": row[9],
            "cover": row[10],
            "date_added": row[11]
        }

        books.append(book)

    workbook.close()

    return books

# ============================================================
# GENERATE BOOK ID
# ============================================================

def generate_book_id():

    create_excel_file()

    workbook = load_workbook(EXCEL_FILE)

    sheet = workbook["Books"]

    book_count = sheet.max_row - 1

    book_id = f"LIB{book_count + 1:04d}"

    workbook.close()

    return book_id

# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    books = get_all_books()

    total_books = len(books)

    total_copies = sum(
        int(book["total_copies"] or 0)
        for book in books
    )

    available_copies = sum(
        int(book["available_copies"] or 0)
        for book in books
    )

    borrowed_copies = (
        total_copies - available_copies
    )

    return render_template(
        "dashboard.html",
        total_books=total_books,
        total_copies=total_copies,
        available_copies=available_copies,
        borrowed_copies=borrowed_copies,
        books=books
    )

# ============================================================
# ADD BOOK
# ============================================================

@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        category = request.form.get("category", "").strip()
        publisher = request.form.get("publisher", "").strip()
        year = request.form.get("year", "").strip()
        copies = request.form.get("copies", "").strip()
        shelf = request.form.get("shelf", "").strip()

        cover = request.files.get("cover")

        # ----------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # ----------------------------------------------------

        if not title:
            return "Book title is required."

        if not author:
            return "Author name is required."

        if not copies:
            return "Number of copies is required."

        try:

            copies = int(copies)

            if copies <= 0:

                return "Copies must be greater than zero."

        except ValueError:

            return "Copies must be a valid number."

        # ----------------------------------------------------
        # GENERATE BOOK ID
        # ----------------------------------------------------

        book_id = generate_book_id()

        # ----------------------------------------------------
        # HANDLE BOOK COVER
        # ----------------------------------------------------

        cover_filename = ""

        if cover and cover.filename:

            if not allowed_file(cover.filename):

                return (
                    "Invalid image format. "
                    "Use PNG, JPG, JPEG or WEBP."
                )

            original_name = secure_filename(
                cover.filename
            )

            extension = os.path.splitext(
                original_name
            )[1].lower()

            cover_filename = (
                f"{book_id}_"
                f"{uuid.uuid4().hex}"
                f"{extension}"
            )

            cover_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                cover_filename
            )

            cover.save(cover_path)

            # ------------------------------------------------
            # VALIDATE IMAGE
            # ------------------------------------------------

            try:

                with Image.open(cover_path) as image:

                    image.verify()

            except Exception:

                if os.path.exists(cover_path):

                    os.remove(cover_path)

                return "Uploaded file is not a valid image."

        # ----------------------------------------------------
        # SAVE BOOK TO EXCEL
        # ----------------------------------------------------

        create_excel_file()

        workbook = load_workbook(EXCEL_FILE)

        sheet = workbook["Books"]

        current_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        sheet.append([
            book_id,
            title,
            author,
            isbn,
            category,
            publisher,
            year,
            copies,
            copies,
            shelf,
            cover_filename,
            current_date
        ])

        workbook.save(EXCEL_FILE)

        workbook.close()

        # ----------------------------------------------------
        # REDIRECT TO BOOK LIST
        # ----------------------------------------------------

        return redirect(
            url_for("books")
        )

    return render_template(
        "add_book.html"
    )

# ============================================================
# VIEW BOOKS
# ============================================================

@app.route("/books")
def books():

    books = get_all_books()

    return render_template(
        "books.html",
        books=books
    )

# ============================================================
# SERVE UPLOADED BOOK COVERS
# ============================================================

@app.route("/uploads/book_covers/<filename>")
def uploaded_cover(filename):

    from flask import send_from_directory

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    create_excel_file()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
