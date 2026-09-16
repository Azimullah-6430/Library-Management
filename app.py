import os
import re
import json
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_from_directory,
    session,
)
from werkzeug.utils import secure_filename
from openpyxl import Workbook, load_workbook
from PIL import Image, ImageOps


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "data")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "book_covers")

EXCEL_FILE = os.path.join(DATA_FOLDER, "library_books.xlsx")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "crescent-library-development-secret"
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# EXCEL STRUCTURE
# ============================================================

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
# EXCEL HELPERS
# ============================================================

def initialize_excel():
    """Create the Excel database if it does not exist."""

    if not os.path.exists(EXCEL_FILE):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Books"

        for column, header in enumerate(HEADERS, start=1):
            sheet.cell(row=1, column=column, value=header)

        workbook.save(EXCEL_FILE)
        return

    try:
        workbook = load_workbook(EXCEL_FILE)
        sheet = workbook.active

        existing_headers = [
            sheet.cell(row=1, column=i).value
            for i in range(1, sheet.max_column + 1)
        ]

        if existing_headers != HEADERS:
            workbook.close()

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Books"

            for column, header in enumerate(HEADERS, start=1):
                sheet.cell(row=1, column=column, value=header)

            workbook.save(EXCEL_FILE)

        workbook.close()

    except Exception:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Books"

        for column, header in enumerate(HEADERS, start=1):
            sheet.cell(row=1, column=column, value=header)

        workbook.save(EXCEL_FILE)
        workbook.close()


initialize_excel()


def get_workbook():
    initialize_excel()
    return load_workbook(EXCEL_FILE)


def normalize_book(row):
    """Convert an Excel row into a template-friendly dictionary."""

    values = list(row)

    while len(values) < len(HEADERS):
        values.append("")

    data = dict(zip(HEADERS, values))

    total = safe_int(data.get("Total Copies"), 0)
    available = safe_int(data.get("Available Copies"), 0)

    borrowed = max(total - available, 0)

    return {
        "book_id": clean_value(data.get("Book ID")),
        "title": clean_value(data.get("Book Title")),
        "author": clean_value(data.get("Author")),
        "subtitle": clean_value(data.get("Subtitle")),
        "isbn": clean_value(data.get("ISBN")),
        "category": clean_value(data.get("Category")),
        "publisher": clean_value(data.get("Publisher")),
        "year": clean_value(data.get("Publication Year")),
        "edition": clean_value(data.get("Edition")),
        "price": clean_value(data.get("Price")),
        "copies": total,
        "available": available,
        "borrowed": borrowed,
        "shelf": clean_value(data.get("Shelf Number")),
        "front_image": clean_value(data.get("Front Image")),
        "back_image": clean_value(data.get("Back Image")),
        "cover": clean_value(data.get("Front Image")),
        "date_added": clean_value(data.get("Date Added")),
        "scan_status": clean_value(data.get("Scan Status")),
    }


def clean_value(value):
    if value is None:
        return ""

    return str(value).strip()


def safe_int(value, default=0):
    try:
        if value in (None, ""):
            return default

        return int(float(value))

    except (ValueError, TypeError):
        return default


def get_all_books():
    workbook = get_workbook()
    sheet = workbook.active

    books = []

    for row in sheet.iter_rows(
        min_row=2,
        values_only=True
    ):
        if not any(value not in (None, "") for value in row):
            continue

        books.append(normalize_book(row))

    workbook.close()

    return books


def find_book(book_id):
    workbook = get_workbook()
    sheet = workbook.active

    for row_number in range(2, sheet.max_row + 1):

        current_id = clean_value(
            sheet.cell(row=row_number, column=1).value
        )

        if current_id == str(book_id):
            values = [
                sheet.cell(
                    row=row_number,
                    column=column
                ).value
                for column in range(1, len(HEADERS) + 1)
            ]

            workbook.close()

            return normalize_book(values)

    workbook.close()

    return None


def find_book_row(book_id):
    workbook = get_workbook()
    sheet = workbook.active

    for row_number in range(2, sheet.max_row + 1):

        current_id = clean_value(
            sheet.cell(row=row_number, column=1).value
        )

        if current_id == str(book_id):
            workbook.close()
            return row_number

    workbook.close()

    return None


def add_book_to_excel(book):
    workbook = get_workbook()
    sheet = workbook.active

    row = [
        book.get("book_id", ""),
        book.get("title", ""),
        book.get("author", ""),
        book.get("subtitle", ""),
        book.get("isbn", ""),
        book.get("category", ""),
        book.get("publisher", ""),
        book.get("year", ""),
        book.get("edition", ""),
        book.get("price", ""),
        book.get("copies", 1),
        book.get("available", 1),
        book.get("borrowed", 0),
        book.get("shelf", ""),
        book.get("front_image", ""),
        book.get("back_image", ""),
        book.get(
            "date_added",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ),
        book.get("scan_status", "AI Scanned"),
    ]

    sheet.append(row)
    workbook.save(EXCEL_FILE)
    workbook.close()


def update_book_in_excel(book_id, book):
    row_number = find_book_row(book_id)

    if row_number is None:
        return False

    workbook = get_workbook()
    sheet = workbook.active

    values = [
        book.get("book_id", book_id),
        book.get("title", ""),
        book.get("author", ""),
        book.get("subtitle", ""),
        book.get("isbn", ""),
        book.get("category", ""),
        book.get("publisher", ""),
        book.get("year", ""),
        book.get("edition", ""),
        book.get("price", ""),
        book.get("copies", 1),
        book.get("available", 1),
        book.get("borrowed", 0),
        book.get("shelf", ""),
        book.get("front_image", ""),
        book.get("back_image", ""),
        book.get("date_added", ""),
        book.get("scan_status", "AI Scanned"),
    ]

    for column, value in enumerate(values, start=1):
        sheet.cell(
            row=row_number,
            column=column,
            value=value
        )

    workbook.save(EXCEL_FILE)
    workbook.close()

    return True


def delete_book_from_excel(book_id):
    row_number = find_book_row(book_id)

    if row_number is None:
        return False

    workbook = get_workbook()
    sheet = workbook.active

    sheet.delete_rows(row_number, 1)

    workbook.save(EXCEL_FILE)
    workbook.close()

    return True


# ============================================================
# IMAGE HANDLING
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}


def allowed_image(filename):
    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_IMAGE_EXTENSIONS


def save_book_image(file, image_type):
    """Validate, normalize and save a front/back book image."""

    if not file or not file.filename:
        return None, "Image was not selected."

    if not allowed_image(file.filename):
        return None, "Only PNG, JPG, JPEG and WEBP images are supported."

    try:
        file.seek(0)

        image = Image.open(file)

        image = ImageOps.exif_transpose(image)

        if image.width < 200 or image.height < 200:
            return None, "Image resolution is too small."

        image.thumbnail(
            (1800, 1800),
            Image.Resampling.LANCZOS
        )

        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")

        extension = "jpg"

        filename = secure_filename(
            f"{image_type}_{timestamp}.jpg"
        )

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        if image.mode == "RGBA":
            background = Image.new(
                "RGB",
                image.size,
                "white"
            )
            background.paste(
                image,
                mask=image.getchannel("A")
            )
            image = background

        image.save(
            filepath,
            "JPEG",
            quality=92,
            optimize=True
        )

        return filename, None

    except Exception as error:
        return None, f"Unable to process image: {error}"


def delete_image(filename):
    if not filename:
        return

    safe_name = os.path.basename(filename)

    filepath = os.path.join(
        UPLOAD_FOLDER,
        safe_name
    )

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass


# ============================================================
# BOOK ID
# ============================================================

def generate_book_id():
    books = get_all_books()

    highest_number = 0

    for book in books:
        book_id = book.get("book_id", "")

        match = re.search(
            r"(\d+)$",
            book_id
        )

        if match:
            highest_number = max(
                highest_number,
                int(match.group(1))
            )

    return f"LIB{highest_number + 1:04d}"


# ============================================================
# STATISTICS
# ============================================================

def calculate_statistics():
    books = get_all_books()

    total_titles = len(books)

    total_copies = sum(
        safe_int(book.get("copies"), 0)
        for book in books
    )

    available_copies = sum(
        safe_int(book.get("available"), 0)
        for book in books
    )

    borrowed_copies = sum(
        max(
            safe_int(book.get("copies"), 0)
            -
            safe_int(book.get("available"), 0),
            0
        )
        for book in books
    )

    categories = {}

    for book in books:
        category = book.get("category") or "Uncategorized"

        categories[category] = (
            categories.get(category, 0) + 1
        )

    return {
        "total_books": total_titles,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "borrowed_copies": borrowed_copies,
        "categories": categories,
    }


# ============================================================
# METADATA EXTRACTION
# ============================================================

def extract_isbn(text):
    """Find a likely ISBN-10 or ISBN-13 from OCR text."""

    if not text:
        return ""

    normalized = re.sub(
        r"(?i)isbn[\s:\-]*",
        "",
        text
    )

    candidates = re.findall(
        r"(?:97[89][\-\s]?)?\d(?:[\d\-\s]{8,16})[\dXx]",
        normalized
    )

    for candidate in candidates:
        isbn = re.sub(
            r"[^0-9Xx]",
            "",
            candidate
        )

        if len(isbn) in (10, 13):
            return isbn.upper()

    return ""


def extract_year(text):
    if not text:
        return ""

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    current_year = datetime.now().year

    for year in years:
        value = int(year)

        if 1000 <= value <= current_year:
            return str(value)

    return ""


def basic_text_metadata(front_text="", back_text=""):
    """
    Lightweight fallback parser.

    The dedicated scanner module can provide richer AI/OCR
    extraction. This function guarantees a structured response
    even when no AI service is configured.
    """

    combined = (
        f"{front_text}\n{back_text}"
    ).strip()

    return {
        "title": "",
        "author": "",
        "subtitle": "",
        "isbn": extract_isbn(combined),
        "category": "",
        "publisher": "",
        "year": extract_year(combined),
        "edition": "",
        "price": "",
    }


# ============================================================
# AUTHENTICATION
# ============================================================

DEMO_USERNAME = os.environ.get(
    "LIBRARY_USERNAME",
    "admin"
)

DEMO_PASSWORD = os.environ.get(
    "LIBRARY_PASSWORD",
    "admin123"
)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == DEMO_USERNAME
            and password == DEMO_PASSWORD
        ):
            session["logged_in"] = True
            session["username"] = username

            flash(
                "Welcome to Crescent Library.",
                "success"
            )

            return redirect(
                url_for("index")
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# MAIN PAGES
# ============================================================

@app.route("/")
def index():

    books = get_all_books()
    statistics = calculate_statistics()

    return render_template(
        "dashboard.html",
        books=books,
        total_books=statistics["total_books"],
        total_copies=statistics["total_copies"],
        available_copies=statistics["available_copies"],
        borrowed_copies=statistics["borrowed_copies"],
        categories=statistics["categories"],
    )


@app.route("/books")
def books():

    query = request.args.get(
        "search",
        ""
    ).strip().lower()

    all_books = get_all_books()

    if query:

        filtered_books = []

        for book in all_books:

            searchable = " ".join([
                book.get("book_id", ""),
                book.get("title", ""),
                book.get("author", ""),
                book.get("isbn", ""),
                book.get("category", ""),
                book.get("publisher", ""),
                book.get("shelf", ""),
            ]).lower()

            if query in searchable:
                filtered_books.append(book)

        all_books = filtered_books

    return render_template(
        "books.html",
        books=all_books,
        search_query=query,
    )


# ============================================================
# ADD BOOK
# ============================================================

@app.route("/add-book", methods=["GET", "POST"])
def add_book():

    if request.method == "GET":
        return render_template(
            "add_book.html",
            current_year=datetime.now().year,
            categories=sorted({
                book["category"]
                for book in get_all_books()
                if book["category"]
            }),
        )

    front_file = request.files.get(
        "front_image"
    )

    back_file = request.files.get(
        "back_image"
    )

    if not front_file or not front_file.filename:
        flash(
            "Please upload the front image of the book.",
            "danger"
        )
        return redirect(url_for("add_book"))

    if not back_file or not back_file.filename:
        flash(
            "Please upload the back image of the book.",
            "danger"
        )
        return redirect(url_for("add_book"))

    front_image, front_error = save_book_image(
        front_file,
        "front"
    )

    if front_error:
        flash(front_error, "danger")
        return redirect(url_for("add_book"))

    back_image, back_error = save_book_image(
        back_file,
        "back"
    )

    if back_error:
        delete_image(front_image)
        flash(back_error, "danger")
        return redirect(url_for("add_book"))

    try:

        extracted_data = {}

        raw_metadata = request.form.get(
            "extracted_data",
            ""
        ).strip()

        if raw_metadata:

            try:
                extracted_data = json.loads(
                    raw_metadata
                )

            except json.JSONDecodeError:
                extracted_data = {}

        title = str(
            extracted_data.get("title", "")
        ).strip()

        author = str(
            extracted_data.get("author", "")
        ).strip()

        subtitle = str(
            extracted_data.get("subtitle", "")
        ).strip()

        isbn = str(
            extracted_data.get("isbn", "")
        ).strip()

        category = str(
            extracted_data.get("category", "")
        ).strip()

        publisher = str(
            extracted_data.get("publisher", "")
        ).strip()

        year = str(
            extracted_data.get("year", "")
        ).strip()

        edition = str(
            extracted_data.get("edition", "")
        ).strip()

        price = str(
            extracted_data.get("price", "")
        ).strip()

        # Duplicate ISBN protection
        if isbn:

            existing_books = get_all_books()

            for existing in existing_books:

                existing_isbn = re.sub(
                    r"[^0-9Xx]",
                    "",
                    existing.get("isbn", "")
                )

                incoming_isbn = re.sub(
                    r"[^0-9Xx]",
                    "",
                    isbn
                )

                if (
                    existing_isbn
                    and incoming_isbn
                    and existing_isbn == incoming_isbn
                ):
                    delete_image(front_image)
                    delete_image(back_image)

                    flash(
                        f"This ISBN already exists as "
                        f"{existing['book_id']}.",
                        "warning"
                    )

                    return redirect(
                        url_for("add_book")
                    )

        book_id = generate_book_id()

        book = {
            "book_id": book_id,
            "title": title or "Not detected",
            "author": author or "Not detected",
            "subtitle": subtitle,
            "isbn": isbn or "Not detected",
            "category": category or "Uncategorized",
            "publisher": publisher or "Not detected",
            "year": year or "Not detected",
            "edition": edition or "Not detected",
            "price": price or "Not detected",
            "copies": 1,
            "available": 1,
            "borrowed": 0,
            "shelf": "",
            "front_image": front_image,
            "back_image": back_image,
            "date_added": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "scan_status": "AI Scanned",
        }

        add_book_to_excel(book)

        flash(
            f"Book {book_id} was added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "book_details",
                book_id=book_id
            )
        )

    except Exception as error:

        delete_image(front_image)
        delete_image(back_image)

        flash(
            f"Unable to save the book: {error}",
            "danger"
        )

        return redirect(
            url_for("add_book")
        )


# ============================================================
# SCAN BOOK API
# ============================================================

@app.route("/scan-book", methods=["POST"])
def scan_book():

    front_file = request.files.get(
        "front_image"
    )

    back_file = request.files.get(
        "back_image"
    )

    if not front_file or not front_file.filename:
        return jsonify({
            "success": False,
            "error": "Front book image is required."
        }), 400

    if not back_file or not back_file.filename:
        return jsonify({
            "success": False,
            "error": "Back book image is required."
        }), 400

    front_path = None
    back_path = None

    try:

        front_filename, front_error = save_book_image(
            front_file,
            "scan_front"
        )

        if front_error:
            return jsonify({
                "success": False,
                "error": front_error
            }), 400

        back_filename, back_error = save_book_image(
            back_file,
            "scan_back"
        )

        if back_error:
            delete_image(front_filename)

            return jsonify({
                "success": False,
                "error": back_error
            }), 400

        front_path = os.path.join(
            UPLOAD_FOLDER,
            front_filename
        )

        back_path = os.path.join(
            UPLOAD_FOLDER,
            back_filename
        )

        result = {
            "title": "",
            "author": "",
            "subtitle": "",
            "isbn": "",
            "category": "",
            "publisher": "",
            "year": "",
            "edition": "",
            "price": "",
        }

        # Try the dedicated scanner if available.
        try:

            from utils.book_scanner import scan_book_images

            scanned = scan_book_images(
                front_path,
                back_path
            )

            if isinstance(scanned, dict):
                result.update(scanned)

        except ImportError:
            pass

        except Exception:
            # Scanner errors should not crash the Flask server.
            pass

        # Always attempt ISBN normalization.
        if not result.get("isbn"):

            result["isbn"] = ""

        result["isbn"] = re.sub(
            r"[^0-9Xx]",
            "",
            str(result.get("isbn", ""))
        )

        # Scan images are temporary.
        delete_image(front_filename)
        delete_image(back_filename)

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as error:

        if front_path:
            delete_image(
                os.path.basename(front_path)
            )

        if back_path:
            delete_image(
                os.path.basename(back_path)
            )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ============================================================
# BOOK DETAILS
# ============================================================

@app.route("/book/<book_id>")
def book_details(book_id):

    book = find_book(book_id)

    if not book:

        flash(
            "Book not found.",
            "danger"
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

    book = find_book(book_id)

    if not book:

        flash(
            "Book not found.",
            "danger"
        )

        return redirect(
            url_for("books")
        )

    if request.method == "GET":

        return render_template(
            "edit_book.html",
            book=book,
            current_year=datetime.now().year,
            categories=sorted({
                item["category"]
                for item in get_all_books()
                if item["category"]
            }),
        )

    title = request.form.get(
        "title",
        book["title"]
    ).strip()

    author = request.form.get(
        "author",
        book["author"]
    ).strip()

    subtitle = request.form.get(
        "subtitle",
        book["subtitle"]
    ).strip()

    isbn = request.form.get(
        "isbn",
        book["isbn"]
    ).strip()

    category = request.form.get(
        "category",
        book["category"]
    ).strip()

    publisher = request.form.get(
        "publisher",
        book["publisher"]
    ).strip()

    year = request.form.get(
        "year",
        book["year"]
    ).strip()

    edition = request.form.get(
        "edition",
        book["edition"]
    ).strip()

    price = request.form.get(
        "price",
        book["price"]
    ).strip()

    total_copies = safe_int(
        request.form.get(
            "copies",
            book["copies"]
        ),
        book["copies"]
    )

    borrowed = book["borrowed"]

    if total_copies < borrowed:

        flash(
            f"Total copies cannot be less than "
            f"the {borrowed} borrowed copies.",
            "danger"
        )

        return redirect(
            url_for(
                "edit_book",
                book_id=book_id
            )
        )

    available = total_copies - borrowed

    front_image = book["front_image"]
    back_image = book["back_image"]

    new_front = None
    new_back = None

    front_file = request.files.get(
        "front_image"
    )

    back_file = request.files.get(
        "back_image"
    )

    try:

        if front_file and front_file.filename:

            new_front, error = save_book_image(
                front_file,
                "front"
            )

            if error:
                flash(error, "danger")
                return redirect(
                    url_for(
                        "edit_book",
                        book_id=book_id
                    )
                )

            front_image = new_front

        if back_file and back_file.filename:

            new_back, error = save_book_image(
                back_file,
                "back"
            )

            if error:

                if new_front:
                    delete_image(new_front)

                flash(error, "danger")

                return redirect(
                    url_for(
                        "edit_book",
                        book_id=book_id
                    )
                )

            back_image = new_back

        updated_book = {
            "book_id": book_id,
            "title": title,
            "author": author,
            "subtitle": subtitle,
            "isbn": isbn,
            "category": category,
            "publisher": publisher,
            "year": year,
            "edition": edition,
            "price": price,
            "copies": total_copies,
            "available": available,
            "borrowed": borrowed,
            "shelf": book["shelf"],
            "front_image": front_image,
            "back_image": back_image,
            "date_added": book["date_added"],
            "scan_status": book["scan_status"] or "AI Scanned",
        }

        success = update_book_in_excel(
            book_id,
            updated_book
        )

        if not success:

            if new_front:
                delete_image(new_front)

            if new_back:
                delete_image(new_back)

            flash(
                "Unable to update the book.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_book",
                    book_id=book_id
                )
            )

        if new_front and book["front_image"]:
            delete_image(
                book["front_image"]
            )

        if new_back and book["back_image"]:
            delete_image(
                book["back_image"]
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

    except Exception as error:

        if new_front:
            delete_image(new_front)

        if new_back:
            delete_image(new_back)

        flash(
            f"Unable to update book: {error}",
            "danger"
        )

        return redirect(
            url_for(
                "edit_book",
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

    book = find_book(book_id)

    if not book:

        flash(
            "Book not found.",
            "danger"
        )

        return redirect(
            url_for("books")
        )

    try:

        success = delete_book_from_excel(
            book_id
        )

        if not success:

            flash(
                "Unable to delete the book.",
                "danger"
            )

            return redirect(
                url_for("books")
            )

        delete_image(
            book.get("front_image")
        )

        delete_image(
            book.get("back_image")
        )

        flash(
            f"Book {book_id} deleted successfully.",
            "success"
        )

    except Exception as error:

        flash(
            f"Unable to delete book: {error}",
            "danger"
        )

    return redirect(
        url_for("books")
    )


# ============================================================
# CATEGORY
# ============================================================

@app.route("/category/<path:category>")
def category_books(category):

    all_books = get_all_books()

    filtered_books = [
        book
        for book in all_books
        if book["category"].lower()
        == category.lower()
    ]

    return render_template(
        "books.html",
        books=filtered_books,
        search_query="",
        selected_category=category,
    )


# ============================================================
# AVAILABLE / BORROWED
# ============================================================

@app.route("/available-books")
def available_books():

    books = [
        book
        for book in get_all_books()
        if book["available"] > 0
    ]

    return render_template(
        "books.html",
        books=books,
        search_query="",
        selected_category="Available Books",
    )


@app.route("/borrowed-books")
def borrowed_books():

    books = [
        book
        for book in get_all_books()
        if book["borrowed"] > 0
    ]

    return render_template(
        "books.html",
        books=books,
        search_query="",
        selected_category="Borrowed Books",
    )


# ============================================================
# SEARCH API
# ============================================================

@app.route("/search")
def search():

    query = request.args.get(
        "q",
        ""
    ).strip().lower()

    results = []

    for book in get_all_books():

        searchable = " ".join([
            book["book_id"],
            book["title"],
            book["author"],
            book["isbn"],
            book["category"],
            book["publisher"],
        ]).lower()

        if query in searchable:
            results.append(book)

    return jsonify({
        "success": True,
        "count": len(results),
        "books": results,
    })


# ============================================================
# API STATISTICS
# ============================================================

@app.route("/api/statistics")
def api_statistics():

    return jsonify(
        calculate_statistics()
    )


# ============================================================
# API BOOKS
# ============================================================

@app.route("/api/books")
def api_books():

    return jsonify({
        "success": True,
        "count": len(get_all_books()),
        "books": get_all_books(),
    })


@app.route("/api/books/<book_id>")
def api_book(book_id):

    book = find_book(book_id)

    if not book:

        return jsonify({
            "success": False,
            "error": "Book not found."
        }), 404

    return jsonify({
        "success": True,
        "book": book,
    })


# ============================================================
# UPLOADED IMAGES
# ============================================================

@app.route(
    "/uploads/book_covers/<path:filename>"
)
def uploaded_cover(filename):

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
        "timestamp": datetime.now().isoformat(),
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "Resource not found."
        }), 404

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>404 - Crescent Library</title>
        <style>
            body {
                font-family: Inter, Arial, sans-serif;
                background: #f5f7fb;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
            }

            .error {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 15px 50px rgba(0,0,0,.08);
            }

            h1 {
                font-size: 64px;
                margin: 0;
            }

            a {
                color: #14213d;
                text-decoration: none;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="error">
            <h1>404</h1>
            <p>The requested page could not be found.</p>
            <a href="/">Return to Dashboard</a>
        </div>
    </body>
    </html>
    """, 404


@app.errorhandler(413)
def file_too_large(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "Uploaded file is too large. Maximum size is 10 MB."
        }), 413

    flash(
        "Uploaded file is too large. Maximum size is 10 MB.",
        "danger"
    )

    return redirect(
        url_for("add_book")
    )


@app.errorhandler(500)
def internal_error(error):

    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "Internal server error."
        }), 500

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Crescent Library - Error</title>
        <style>
            body {
                font-family: Inter, Arial, sans-serif;
                background: #f5f7fb;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
            }

            .error {
                max-width: 520px;
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 15px 50px rgba(0,0,0,.08);
            }

            a {
                color: #14213d;
                text-decoration: none;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="error">
            <h1>Something went wrong</h1>
            <p>
                The library system encountered an unexpected error.
            </p>
            <a href="/">Return to Dashboard</a>
        </div>
    </body>
    </html>
    """, 500


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
