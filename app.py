import os
import uuid
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
    jsonify,
    session
)

from werkzeug.utils import secure_filename

from openpyxl import Workbook, load_workbook
from PIL import Image


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


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "crescent-library-development-secret"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum complete request size
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# ============================================================
# EXCEL CONFIGURATION
# ============================================================

HEADERS = [
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


ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


MAX_IMAGE_SIZE = 5 * 1024 * 1024


# ============================================================
# EXCEL DATABASE INITIALIZATION
# ============================================================

def initialize_excel():
    """
    Create the Excel database if it does not exist.

    If the file exists but is empty/corrupt, recreate it.
    """

    try:

        if not os.path.exists(EXCEL_FILE):

            workbook = Workbook()

            worksheet = workbook.active
            worksheet.title = "Books"

            worksheet.append(HEADERS)

            workbook.save(EXCEL_FILE)

            print("Created Excel database:")
            print(EXCEL_FILE)

            return

        # Try opening existing workbook
        workbook = load_workbook(
            EXCEL_FILE
        )

        if "Books" not in workbook.sheetnames:

            worksheet = workbook.create_sheet(
                "Books"
            )

            worksheet.append(HEADERS)

            workbook.save(
                EXCEL_FILE
            )

        else:

            worksheet = workbook["Books"]

            # If completely empty
            if worksheet.max_row == 1 and worksheet["A1"].value is None:

                worksheet.delete_rows(
                    1,
                    worksheet.max_row
                )

                worksheet.append(
                    HEADERS
                )

                workbook.save(
                    EXCEL_FILE
                )

        workbook.close()

    except Exception as error:

        print()
        print("=" * 70)
        print("EXCEL INITIALIZATION ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70)

        # Backup corrupt file
        if os.path.exists(EXCEL_FILE):

            backup_name = (
                EXCEL_FILE
                + ".backup_"
                + datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )
            )

            try:

                os.rename(
                    EXCEL_FILE,
                    backup_name
                )

                print(
                    f"Corrupt Excel file backed up to: {backup_name}"
                )

            except Exception:

                pass

        # Create fresh database
        workbook = Workbook()

        worksheet = workbook.active
        worksheet.title = "Books"

        worksheet.append(
            HEADERS
        )

        workbook.save(
            EXCEL_FILE
        )

        workbook.close()

        print("Created fresh Excel database.")


# Initialize database immediately
initialize_excel()


# ============================================================
# EXCEL HELPERS
# ============================================================

def get_workbook():

    initialize_excel()

    return load_workbook(
        EXCEL_FILE
    )


def normalize_book(row):
    """
    Convert an Excel row into the dictionary format
    expected by the HTML templates.
    """

    return {

        "book_id": row[0] or "",

        "title": row[1] or "",

        "author": row[2] or "",

        "isbn": row[3] or "",

        "category": row[4] or "",

        "publisher": row[5] or "",

        "year": row[6] or "",

        "copies": row[7] or 0,

        "available": row[8] or 0,

        "shelf": row[9] or "",

        "cover": row[10] or "",

        "date_added": row[11] or ""
    }


def get_all_books():

    try:

        workbook = get_workbook()

        worksheet = workbook["Books"]

        books = []

        for row in worksheet.iter_rows(
            min_row=2,
            values_only=True
        ):

            # Skip completely empty rows
            if not any(
                value is not None
                for value in row
            ):
                continue

            # Ensure row has 12 values
            row = list(row)

            while len(row) < 12:
                row.append("")

            books.append(
                normalize_book(row)
            )

        workbook.close()

        return books

    except Exception:

        traceback.print_exc()

        return []


def find_book(book_id):

    book_id = str(
        book_id
    ).strip()

    workbook = get_workbook()

    worksheet = workbook["Books"]

    for row_number in range(
        2,
        worksheet.max_row + 1
    ):

        value = worksheet.cell(
            row_number,
            1
        ).value

        if str(value).strip() == book_id:

            row = [
                worksheet.cell(
                    row_number,
                    column
                ).value
                for column in range(
                    1,
                    13
                )
            ]

            workbook.close()

            return normalize_book(
                row
            )

    workbook.close()

    return None


def add_book_to_excel(book):

    workbook = get_workbook()

    worksheet = workbook["Books"]

    worksheet.append([
        book["book_id"],
        book["title"],
        book["author"],
        book["isbn"],
        book["category"],
        book["publisher"],
        book["year"],
        book["copies"],
        book["available"],
        book["shelf"],
        book["cover"],
        book["date_added"]
    ])

    workbook.save(
        EXCEL_FILE
    )

    workbook.close()


def update_book_in_excel(
    book_id,
    book
):

    workbook = get_workbook()

    worksheet = workbook["Books"]

    for row_number in range(
        2,
        worksheet.max_row + 1
    ):

        current_id = worksheet.cell(
            row_number,
            1
        ).value

        if str(current_id).strip() == str(book_id).strip():

            values = [
                book["book_id"],
                book["title"],
                book["author"],
                book["isbn"],
                book["category"],
                book["publisher"],
                book["year"],
                book["copies"],
                book["available"],
                book["shelf"],
                book["cover"],
                book["date_added"]
            ]

            for column, value in enumerate(
                values,
                start=1
            ):

                worksheet.cell(
                    row_number,
                    column
                ).value = value

            workbook.save(
                EXCEL_FILE
            )

            workbook.close()

            return True

    workbook.close()

    return False


def delete_book_from_excel(book_id):

    workbook = get_workbook()

    worksheet = workbook["Books"]

    for row_number in range(
        2,
        worksheet.max_row + 1
    ):

        current_id = worksheet.cell(
            row_number,
            1
        ).value

        if str(current_id).strip() == str(book_id).strip():

            worksheet.delete_rows(
                row_number,
                1
            )

            workbook.save(
                EXCEL_FILE
            )

            workbook.close()

            return True

    workbook.close()

    return False


# ============================================================
# NUMBER HELPERS
# ============================================================

def safe_int(
    value,
    default=0
):

    try:

        return int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        try:

            return int(
                float(value)
            )

        except (
            ValueError,
            TypeError
        ):

            return default


# ============================================================
# IMAGE HELPERS
# ============================================================

def is_allowed_image(filename):

    if not filename:
        return False

    extension = (
        filename
        .rsplit(
            ".",
            1
        )[-1]
        .lower()
    )

    return extension in ALLOWED_IMAGE_EXTENSIONS


def save_cover_image(file):

    if not file:
        return ""


    if not file.filename:
        return ""


    if not is_allowed_image(
        file.filename
    ):

        raise ValueError(
            "Only PNG, JPG, JPEG and WEBP images are allowed."
        )


    # Check file size
    file.seek(
        0,
        os.SEEK_END
    )

    file_size = file.tell()

    file.seek(
        0
    )


    if file_size > MAX_IMAGE_SIZE:

        raise ValueError(
            "Image size must not exceed 5 MB."
        )


    # Verify actual image content
    try:

        image = Image.open(
            file
        )

        image.verify()

        file.seek(
            0
        )

    except Exception:

        raise ValueError(
            "The uploaded file is not a valid image."
        )


    # Secure original name
    original_name = secure_filename(
        file.filename
    )

    extension = (
        original_name
        .rsplit(
            ".",
            1
        )[-1]
        .lower()
    )


    # Unique filename
    filename = (
        f"{uuid.uuid4().hex}."
        f"{extension}"
    )


    destination = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    file.save(
        destination
    )


    return filename


def delete_cover_image(filename):

    if not filename:
        return

    safe_name = os.path.basename(
        filename
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_name
    )

    if os.path.exists(
        file_path
    ):

        try:

            os.remove(
                file_path
            )

        except Exception:

            traceback.print_exc()


# ============================================================
# BOOK ID GENERATOR
# ============================================================

def generate_book_id():

    books = get_all_books()

    highest = 0

    for book in books:

        book_id = str(
            book.get(
                "book_id",
                ""
            )
        ).strip().upper()

        if not book_id.startswith(
            "LIB"
        ):
            continue

        try:

            number = int(
                book_id[3:]
            )

            highest = max(
                highest,
                number
            )

        except ValueError:

            continue

    return f"LIB{highest + 1:04d}"


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics(
    books
):

    total_books = len(
        books
    )

    total_copies = 0

    available_copies = 0

    for book in books:

        total_copies += safe_int(
            book.get(
                "copies",
                0
            )
        )

        available_copies += safe_int(
            book.get(
                "available",
                0
            )
        )

    borrowed_copies = (
        total_copies
        - available_copies
    )

    if borrowed_copies < 0:
        borrowed_copies = 0

    return {

        "total_books": total_books,

        "total_copies": total_copies,

        "available_copies": available_copies,

        "borrowed_copies": borrowed_copies
    }


# ============================================================
# FORM DATA
# ============================================================

def get_form_data():

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
        ""
    ).strip()

    shelf = request.form.get(
        "shelf",
        ""
    ).strip()


    return {

        "title": title,

        "author": author,

        "isbn": isbn,

        "category": category,

        "publisher": publisher,

        "year": year,

        "copies": copies,

        "shelf": shelf
    }


# ============================================================
# VALIDATE BOOK DATA
# ============================================================

def validate_book_data(
    data
):

    if not data["title"]:

        return False, (
            "Book title is required."
        )


    if not data["author"]:

        return False, (
            "Author name is required."
        )


    if not data["copies"]:

        return False, (
            "Number of copies is required."
        )


    copies = safe_int(
        data["copies"],
        -1
    )

    if copies < 1:

        return False, (
            "Number of copies must be at least 1."
        )


    if data["year"]:

        year = safe_int(
            data["year"],
            -1
        )

        current_year = (
            datetime.now().year
        )

        if year < 0:

            return False, (
                "Publication year must be a valid number."
            )

        if year > current_year:

            return False, (
                "Publication year cannot be in the future."
            )


    return True, ""


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    try:

        books = get_all_books()

        statistics = calculate_statistics(
            books
        )

        return render_template(
            "dashboard.html",
            books=books,
            statistics=statistics,
            current_date=datetime.now().strftime(
                "%d %B %Y"
            )
        )

    except Exception as error:

        print()
        print("=" * 70)
        print("DASHBOARD ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70)

        return render_template(
            "base.html"
        ), 500


# ============================================================
# BOOK LIST
# ============================================================

@app.route(
    "/books"
)
def books():

    try:

        search_query = request.args.get(
            "search",
            ""
        ).strip()

        all_books = get_all_books()

        if search_query:

            query = search_query.lower()

            all_books = [
                book
                for book in all_books

                if (
                    query
                    in str(
                        book.get(
                            "book_id",
                            ""
                        )
                    ).lower()
                    or
                    query
                    in str(
                        book.get(
                            "title",
                            ""
                        )
                    ).lower()
                    or
                    query
                    in str(
                        book.get(
                            "author",
                            ""
                        )
                    ).lower()
                    or
                    query
                    in str(
                        book.get(
                            "isbn",
                            ""
                        )
                    ).lower()
                    or
                    query
                    in str(
                        book.get(
                            "category",
                            ""
                        )
                    ).lower()
                    or
                    query
                    in str(
                        book.get(
                            "publisher",
                            ""
                        )
                    ).lower()
                )
            ]

        return render_template(
            "books.html",
            books=all_books,
            search_query=search_query
        )

    except Exception:

        print("BOOK LIST ERROR")

        traceback.print_exc()

        flash(
            "Unable to load books.",
            "danger"
        )

        return redirect(
            url_for(
                "dashboard"
            )
        )


# ============================================================
# ADD BOOK
# ============================================================

@app.route(
    "/add-book",
    methods=[
        "GET",
        "POST"
    ]
)
def add_book():

    if request.method == "GET":

        return render_template(
            "add_book.html"
        )


    try:

        data = get_form_data()


        # Validate
        valid, message = validate_book_data(
            data
        )

        if not valid:

            flash(
                message,
                "danger"
            )

            return render_template(
                "add_book.html"
            )


        book_id = generate_book_id()


        # Cover
        cover_file = request.files.get(
            "cover"
        )

        cover_filename = ""


        if cover_file and cover_file.filename:

            cover_filename = save_cover_image(
                cover_file
            )


        copies = safe_int(
            data["copies"]
        )


        book = {

            "book_id": book_id,

            "title": data["title"],

            "author": data["author"],

            "isbn": data["isbn"],

            "category": data["category"],

            "publisher": data["publisher"],

            "year": data["year"],

            "copies": copies,

            "available": copies,

            "shelf": data["shelf"],

            "cover": cover_filename,

            "date_added": datetime.now().strftime(
                "%Y-%m-%d"
            )
        }


        add_book_to_excel(
            book
        )


        flash(
            f"Book {book_id} added successfully.",
            "success"
        )


        return redirect(
            url_for(
                "books"
            )
        )


    except ValueError as error:

        flash(
            str(error),
            "danger"
        )

        return render_template(
            "add_book.html"
        )


    except Exception as error:

        print("ADD BOOK ERROR")

        traceback.print_exc()

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
def book_details(
    book_id
):

    try:

        book = find_book(
            book_id
        )

        if not book:

            flash(
                "Book not found.",
                "danger"
            )

            return redirect(
                url_for(
                    "books"
                )
            )


        return render_template(
            "book_details.html",
            book=book
        )


    except Exception:

        print("BOOK DETAILS ERROR")

        traceback.print_exc()

        flash(
            "Unable to load book details.",
            "danger"
        )

        return redirect(
            url_for(
                "books"
            )
        )


# ============================================================
# EDIT BOOK
# ============================================================

@app.route(
    "/edit-book/<book_id>",
    methods=[
        "GET",
        "POST"
    ]
)
def edit_book(
    book_id
):

    book = find_book(
        book_id
    )

    if not book:

        flash(
            "Book not found.",
            "danger"
        )

        return redirect(
            url_for(
                "books"
            )
        )


    if request.method == "GET":

        return render_template(
            "edit_book.html",
            book=book
        )


    try:

        data = get_form_data()


        valid, message = validate_book_data(
            data
        )

        if not valid:

            flash(
                message,
                "danger"
            )

            return render_template(
                "edit_book.html",
                book=book
            )


        new_total = safe_int(
            data["copies"]
        )


        old_total = safe_int(
            book.get(
                "copies",
                0
            )
        )


        old_available = safe_int(
            book.get(
                "available",
                0
            )
        )


        borrowed = (
            old_total
            - old_available
        )


        # Do not allow total copies
        # to become less than borrowed.
        if new_total < borrowed:

            flash(
                "Total copies cannot be less than the number of borrowed copies.",
                "danger"
            )

            return render_template(
                "edit_book.html",
                book=book
            )


        new_available = (
            new_total
            - borrowed
        )


        cover_filename = book.get(
            "cover",
            ""
        )


        new_cover = request.files.get(
            "cover"
        )


        if new_cover and new_cover.filename:

            new_cover_filename = save_cover_image(
                new_cover
            )


            old_cover = cover_filename

            cover_filename = new_cover_filename

            delete_cover_image(
                old_cover
            )


        updated_book = {

            "book_id": book_id,

            "title": data["title"],

            "author": data["author"],

            "isbn": data["isbn"],

            "category": data["category"],

            "publisher": data["publisher"],

            "year": data["year"],

            "copies": new_total,

            "available": new_available,

            "shelf": data["shelf"],

            "cover": cover_filename,

            "date_added": book.get(
                "date_added",
                datetime.now().strftime(
                    "%Y-%m-%d"
                )
            )
        }


        updated = update_book_in_excel(
            book_id,
            updated_book
        )


        if not updated:

            flash(
                "Book could not be updated.",
                "danger"
            )

            return render_template(
                "edit_book.html",
                book=book
            )


        flash(
            "Book updated successfully.",
            "success"
        )


        return redirect(
            url_for(
                "book_details",
                book_id=book_id
            )
        )


    except ValueError as error:

        flash(
            str(error),
            "danger"
        )

        return render_template(
            "edit_book.html",
            book=book
        )


    except Exception as error:

        print("EDIT BOOK ERROR")

        traceback.print_exc()

        flash(
            f"Unable to update book: {error}",
            "danger"
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
    methods=[
        "POST",
        "GET"
    ]
)
def delete_book(
    book_id
):

    try:

        book = find_book(
            book_id
        )

        if not book:

            flash(
                "Book not found.",
                "danger"
            )

            return redirect(
                url_for(
                    "books"
                )
            )


        total = safe_int(
            book.get(
                "copies",
                0
            )
        )


        available = safe_int(
            book.get(
                "available",
                0
            )
        )


        borrowed = (
            total
            - available
        )


        # Never delete a book
        # while copies are borrowed.
        if borrowed > 0:

            flash(
                "This book cannot be deleted because copies are currently borrowed.",
                "danger"
            )

            return redirect(
                url_for(
                    "books"
                )
            )


        deleted = delete_book_from_excel(
            book_id
        )


        if deleted:

            delete_cover_image(
                book.get(
                    "cover",
                    ""
                )
            )

            flash(
                "Book deleted successfully.",
                "success"
            )

        else:

            flash(
                "Book could not be deleted.",
                "danger"
            )


    except Exception as error:

        print("DELETE BOOK ERROR")

        traceback.print_exc()

        flash(
            f"Unable to delete book: {error}",
            "danger"
        )


    return redirect(
        url_for(
            "books"
        )
    )


# ============================================================
# CATEGORY
# ============================================================

@app.route(
    "/category/<path:category>"
)
def category_books(
    category
):

    try:

        books_list = get_all_books()

        category_lower = (
            category
            .strip()
            .lower()
        )


        filtered = [

            book

            for book in books_list

            if str(
                book.get(
                    "category",
                    ""
                )
            ).strip().lower()
            == category_lower
        ]


        return render_template(
            "books.html",
            books=filtered,
            search_query=""
        )


    except Exception:

        traceback.print_exc()

        flash(
            "Unable to load category.",
            "danger"
        )

        return redirect(
            url_for(
                "books"
            )
        )


# ============================================================
# AVAILABLE BOOKS
# ============================================================

@app.route(
    "/available-books"
)
def available_books():

    books_list = get_all_books()

    available = [

        book

        for book in books_list

        if safe_int(
            book.get(
                "available",
                0
            )
        ) > 0
    ]


    return render_template(
        "books.html",
        books=available,
        search_query=""
    )


# ============================================================
# BORROWED BOOKS
# ============================================================

@app.route(
    "/borrowed-books"
)
def borrowed_books():

    books_list = get_all_books()

    borrowed = [

        book

        for book in books_list

        if (
            safe_int(
                book.get(
                    "copies",
                    0
                )
            )
            -
            safe_int(
                book.get(
                    "available",
                    0
                )
            )
        ) > 0
    ]


    return render_template(
        "books.html",
        books=borrowed,
        search_query=""
    )


# ============================================================
# SEARCH API
# ============================================================

@app.route(
    "/search"
)
def search():

    query = request.args.get(
        "q",
        ""
    ).strip().lower()


    books_list = get_all_books()


    if not query:

        return jsonify(
            books_list
        )


    results = [

        book

        for book in books_list

        if (
            query
            in str(
                book.get(
                    "book_id",
                    ""
                )
            ).lower()

            or

            query
            in str(
                book.get(
                    "title",
                    ""
                )
            ).lower()

            or

            query
            in str(
                book.get(
                    "author",
                    ""
                )
            ).lower()

            or

            query
            in str(
                book.get(
                    "isbn",
                    ""
                )
            ).lower()

            or

            query
            in str(
                book.get(
                    "category",
                    ""
                )
            ).lower()

            or

            query
            in str(
                book.get(
                    "publisher",
                    ""
                )
            ).lower()

            or

            query
            in str(
                book.get(
                    "shelf",
                    ""
                )
            ).lower()
        )
    ]


    return jsonify(
        results
    )


# ============================================================
# STATISTICS API
# ============================================================

@app.route(
    "/api/statistics"
)
def statistics_api():

    try:

        books_list = get_all_books()

        statistics = calculate_statistics(
            books_list
        )

        return jsonify(
            statistics
        )

    except Exception as error:

        traceback.print_exc()

        return jsonify({
            "error": str(error)
        }), 500


# ============================================================
# BOOKS API
# ============================================================

@app.route(
    "/api/books"
)
def books_api():

    try:

        return jsonify(
            get_all_books()
        )

    except Exception as error:

        traceback.print_exc()

        return jsonify({
            "error": str(error)
        }), 500


# ============================================================
# SINGLE BOOK API
# ============================================================

@app.route(
    "/api/books/<book_id>"
)
def book_api(
    book_id
):

    book = find_book(
        book_id
    )


    if not book:

        return jsonify({
            "error": "Book not found"
        }), 404


    return jsonify(
        book
    )


# ============================================================
# BOOK COVER ROUTE
# ============================================================

@app.route(
    "/uploads/book_covers/<path:filename>"
)
def uploaded_book_cover(
    filename
):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )


    username = request.form.get(
        "username",
        ""
    ).strip()


    password = request.form.get(
        "password",
        ""
    )


    # Demo credentials
    if (
        username == "admin"
        and
        password == "admin123"
    ):

        session["logged_in"] = True

        return redirect(
            url_for(
                "dashboard"
            )
        )


    flash(
        "Invalid username or password.",
        "danger"
    )


    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for(
            "login"
        )
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health"
)
def health():

    try:

        initialize_excel()

        books_count = len(
            get_all_books()
        )


        return jsonify({

            "status": "healthy",

            "application":
                "Crescent College Library Management System",

            "database":
                "Excel",

            "database_file":
                EXCEL_FILE,

            "books":
                books_count,

            "timestamp":
                datetime.now().isoformat()
        })


    except Exception as error:

        traceback.print_exc()

        return jsonify({

            "status": "error",

            "error":
                str(error)

        }), 500


# ============================================================
# 404 ERROR
# ============================================================

@app.errorhandler(404)
def page_not_found(
    error
):

    return """

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Page Not Found
        </title>

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
                box-shadow:
                    0 5px 25px
                    rgba(0,0,0,0.08);
            }

            h1 {
                font-size: 64px;
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

            <h2>
                Page Not Found
            </h2>

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
def file_too_large(
    error
):

    flash(
        "Uploaded file is too large. Maximum size is 5 MB.",
        "danger"
    )


    return redirect(
        request.referrer
        or
        url_for(
            "add_book"
        )
    )


# ============================================================
# INTERNAL SERVER ERROR
# ============================================================

@app.errorhandler(500)
def internal_server_error(
    error
):

    print()
    print("=" * 70)
    print("INTERNAL SERVER ERROR")
    print("=" * 70)

    print(
        "Error:",
        error
    )

    traceback.print_exc()

    print("=" * 70)


    return """

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            Crescent Library - Error
        </title>

        <style>

            body {
                font-family: Arial, sans-serif;
                background: #f5f7fa;
                padding: 50px;
            }

            .box {
                max-width: 750px;
                margin: auto;
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow:
                    0 5px 25px
                    rgba(0,0,0,0.08);
            }

            h1 {
                color: #c62828;
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

            <h1>
                Internal Server Error
            </h1>

            <p>
                The application encountered an unexpected error.
            </p>

            <p>
                Please check the terminal for the complete
                Python traceback.
            </p>

            <a href="/">
                Return to Dashboard
            </a>

        </div>

    </body>

    </html>

    """, 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("CRESCENT COLLEGE LIBRARY MANAGEMENT SYSTEM")
    print("=" * 70)

    print()
    print("Application : Flask")
    print("Database    : Excel")

    print()
    print("Excel File:")
    print(EXCEL_FILE)

    print()
    print("Book Covers:")
    print(UPLOAD_FOLDER)

    print()
    print("Dashboard:")
    print("http://127.0.0.1:5000/")

    print()
    print("Login:")
    print("http://127.0.0.1:5000/login")

    print()
    print("Health:")
    print("http://127.0.0.1:5000/health")

    print()
    print("Demo Login:")
    print("Username: admin")
    print("Password: admin123")

    print()
    print("=" * 70)
    print()


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
