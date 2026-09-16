# ============================================================
# IMPORTS
# ============================================================

# -------------------- Standard Library ----------------------

import os
import uuid
from datetime import datetime


# -------------------- Flask ----------------------

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


# -------------------- Werkzeug ----------------------

from werkzeug.utils import secure_filename


# -------------------- Excel ----------------------

from openpyxl import (
    Workbook,
    load_workbook
)


# -------------------- Image Processing ----------------------

from PIL import Image


# -------------------- Project Utilities ----------------------

from utils.excel_manager import (
    create_excel_file,
    get_all_books,
    add_book,
    find_book,
    update_book,
    delete_book,
    get_book_count,
    get_statistics
)

from utils.image_manager import (
    allowed_image,
    validate_image,
    save_image,
    delete_image
)

from utils.book_manager import (
    BookManager
)
