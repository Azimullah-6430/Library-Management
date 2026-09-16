from flask import Flask, render_template, request, redirect, url_for
from openpyxl import Workbook, load_workbook
from PIL import Image
import os
import uuid

app = Flask(__name__)

# -----------------------------
# Folder configuration
# -----------------------------

UPLOAD_FOLDER = "uploads/book_covers"
DATA_FOLDER = "data"
EXCEL_FILE = os.path.join(DATA_FOLDER, "library_books.xlsx")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -----------------------------
# Create Excel file
# -----------------------------

def create_excel_file():

    if not os.path.exists(EXCEL_FILE):

        workbook = Workbook()
        sheet = workbook.active

        sheet.title = "Books"

        headers = [
            "Book ID",
            "Title",
            "Author",
            "ISBN",
            "Category",
            "Publisher",
            "Year",
            "Copies",
            "Shelf",
            "Cover"
        ]

        sheet.append(headers)

        workbook.save(EXCEL_FILE)


# -----------------------------
# Home page
# -----------------------------

@app.route("/")
def index():

    create_excel_file()

    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook["Books"]

    total_books = sheet.max_row - 1

    return render_template(
        "index.html",
        total_books=total_books
    )


# -----------------------------
# Add book page
# -----------------------------

@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    create_excel_file()

    if request.method == "POST":

        title = request.form["title"]
        author = request.form["author"]
        isbn = request.form["isbn"]
        category = request.form["category"]
        publisher = request.form["publisher"]
        year = request.form["year"]
        copies = request.form["copies"]
        shelf = request.form["shelf"]

        cover = request.files["cover"]

        # Generate unique Book ID
        workbook = load_workbook(EXCEL_FILE)
        sheet = workbook["Books"]

        book_number = sheet.max_row

        book_id = f"LIB{book_number:03d}"

        # Save cover
        cover_filename = ""

        if cover and cover.filename:

            extension = os.path.splitext(
                cover.filename
            )[1].lower()

            cover_filename = f"{book_id}_{uuid.uuid4().hex}{extension}"

            cover_path = os.path.join(
                UPLOAD_FOLDER,
                cover_filename
            )

            cover.save(cover_path)

            # Validate image
            try:
                Image.open(cover_path).verify()

            except Exception:

                os.remove(cover_path)

                return "Invalid image file."

        # Add book to Excel
        sheet.append([
            book_id,
            title,
            author,
            isbn,
            category,
            publisher,
            year,
            copies,
            shelf,
            cover_filename
        ])

        workbook.save(EXCEL_FILE)

        return redirect(url_for("books"))

    return render_template("add_book.html")


# -----------------------------
# View books
# -----------------------------

@app.route("/books")
def books():

    create_excel_file()

    workbook = load_workbook(EXCEL_FILE)

    sheet = workbook["Books"]

    books_list = []

    for row in sheet.iter_rows(
        min_row=2,
        values_only=True
    ):

        books_list.append({
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "isbn": row[3],
            "category": row[4],
            "publisher": row[5],
            "year": row[6],
            "copies": row[7],
            "shelf": row[8],
            "cover": row[9]
        })

    return render_template(
        "books.html",
        books=books_list
    )


# -----------------------------
# Run application
# -----------------------------

if __name__ == "__main__":

    create_excel_file()

    app.run(
        debug=True
    )
