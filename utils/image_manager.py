"""
Image Manager
-------------
Handles book-cover image validation, saving, and deletion
for the Crescent College Library Management System.
"""

import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename


# Allowed image extensions
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

# Maximum image size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


def allowed_image(filename):
    """
    Check whether the uploaded file has an allowed extension.

    Returns:
        bool
    """

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def validate_image(file):
    """
    Validate an uploaded book-cover image.

    Checks:
    - File exists
    - Valid extension
    - File size
    - Actual image format

    Returns:
        tuple: (True, "Valid image") or (False, "Error message")
    """

    if file is None:
        return False, "No image was uploaded."

    if not file.filename:
        return False, "No image was selected."

    if not allowed_image(file.filename):
        return False, "Only PNG, JPG, JPEG, and WEBP images are allowed."

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return False, "Image size must not exceed 5 MB."

    if file_size == 0:
        return False, "The uploaded image is empty."

    # Verify that the file is actually an image
    try:
        image = Image.open(file)
        image.verify()

        file.seek(0)

    except Exception:
        file.seek(0)
        return False, "The uploaded file is not a valid image."

    return True, "Valid image."


def generate_image_filename(original_filename):
    """
    Generate a unique and secure filename.

    Example:
        book_cover.jpg
        ->
        a8f31c2d_book_cover.jpg
    """

    safe_filename = secure_filename(original_filename)

    unique_id = uuid.uuid4().hex[:8]

    return f"{unique_id}_{safe_filename}"


def save_image(file, upload_folder):
    """
    Validate and save a book-cover image.

    Returns:
        tuple:
            (True, filename, message)
        or
            (False, None, error_message)
    """

    is_valid, message = validate_image(file)

    if not is_valid:
        return False, None, message

    # Make sure upload directory exists
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename
    filename = generate_image_filename(file.filename)

    # Full path
    file_path = os.path.join(upload_folder, filename)

    try:
        file.save(file_path)

        # Re-open saved image to make sure it is valid
        with Image.open(file_path) as image:
            image.verify()

    except Exception:
        # Remove partially saved file if something went wrong
        if os.path.exists(file_path):
            os.remove(file_path)

        return False, None, "Unable to save the book-cover image."

    return True, filename, "Book-cover image uploaded successfully."


def delete_image(filename, upload_folder):
    """
    Delete a book-cover image.

    Returns:
        bool
    """

    if not filename:
        return False

    # Prevent path traversal
    safe_filename = secure_filename(filename)

    if safe_filename != filename:
        return False

    file_path = os.path.join(upload_folder, safe_filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False

    return False


def image_exists(filename, upload_folder):
    """
    Check whether a book-cover image exists.
    """

    if not filename:
        return False

    safe_filename = secure_filename(filename)

    if safe_filename != filename:
        return False

    file_path = os.path.join(upload_folder, safe_filename)

    return os.path.isfile(file_path)
