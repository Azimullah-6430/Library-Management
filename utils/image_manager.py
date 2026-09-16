import os
import uuid
from datetime import datetime
from typing import Optional

from PIL import Image, ImageOps


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads",
    "book_covers"
)

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024

MAX_IMAGE_DIMENSION = 2400


# ============================================================
# DIRECTORY
# ============================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# IMAGE MANAGER
# ============================================================

class ImageManager:

    def __init__(
        self,
        upload_folder: str = UPLOAD_FOLDER
    ):
        self.upload_folder = upload_folder

        os.makedirs(
            self.upload_folder,
            exist_ok=True
        )

    # ========================================================
    # VALID EXTENSION
    # ========================================================

    def allowed_file(
        self,
        filename: str
    ) -> bool:

        if not filename:
            return False

        if "." not in filename:
            return False

        extension = (
            filename
            .rsplit(".", 1)[1]
            .lower()
        )

        return extension in ALLOWED_EXTENSIONS

    # ========================================================
    # VALID IMAGE
    # ========================================================

    def validate_image(
        self,
        file
    ) -> bool:

        if file is None:
            return False

        filename = getattr(
            file,
            "filename",
            ""
        )

        if not self.allowed_file(
            filename
        ):
            return False

        try:

            file.seek(0)

            image = Image.open(
                file
            )

            image.verify()

            file.seek(0)

            return True

        except Exception:

            try:
                file.seek(0)
            except Exception:
                pass

            return False

    # ========================================================
    # IMAGE NORMALIZATION
    # ========================================================

    def normalize_image(
        self,
        image: Image.Image
    ) -> Image.Image:

        image = ImageOps.exif_transpose(
            image
        )

        if image.mode in (
            "RGBA",
            "LA",
        ):

            background = Image.new(
                "RGB",
                image.size,
                "white"
            )

            if image.mode == "RGBA":

                background.paste(
                    image,
                    mask=image.getchannel(
                        "A"
                    )
                )

            else:

                background.paste(
                    image,
                    mask=image.getchannel(
                        "A"
                    )
                )

            image = background

        else:

            image = image.convert(
                "RGB"
            )

        width, height = image.size

        if max(
            width,
            height
        ) > MAX_IMAGE_DIMENSION:

            scale = (
                MAX_IMAGE_DIMENSION
                / max(width, height)
            )

            new_size = (
                int(width * scale),
                int(height * scale)
            )

            image = image.resize(
                new_size,
                Image.Resampling.LANCZOS
            )

        return image

    # ========================================================
    # SAVE BOOK IMAGE
    # ========================================================

    def save_book_image(
        self,
        file,
        book_id: str,
        side: str
    ) -> Optional[str]:

        if file is None:
            return None

        if not self.validate_image(
            file
        ):
            raise ValueError(
                "Invalid book image."
            )

        side = str(
            side or ""
        ).strip().lower()

        if side not in (
            "front",
            "back",
        ):

            raise ValueError(
                "Image side must be front or back."
            )

        safe_book_id = (
            str(book_id)
            .strip()
            .replace(" ", "_")
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        unique_id = uuid.uuid4().hex[:8]

        filename = (
            f"{safe_book_id}_"
            f"{side}_"
            f"{timestamp}_"
            f"{unique_id}.jpg"
        )

        output_path = os.path.join(
            self.upload_folder,
            filename
        )

        try:

            file.seek(0)

            image = Image.open(
                file
            )

            image = self.normalize_image(
                image
            )

            image.save(
                output_path,
                format="JPEG",
                quality=92,
                optimize=True
            )

            return filename

        except Exception as error:

            if os.path.exists(
                output_path
            ):

                try:
                    os.remove(
                        output_path
                    )
                except Exception:
                    pass

            raise ValueError(
                f"Unable to save image: {error}"
            )

    # ========================================================
    # SAVE FROM PATH
    # ========================================================

    def save_image_from_path(
        self,
        source_path: str,
        book_id: str,
        side: str
    ) -> Optional[str]:

        if not source_path:
            return None

        if not os.path.exists(
            source_path
        ):
            raise FileNotFoundError(
                "Source image was not found."
            )

        side = str(
            side or ""
        ).strip().lower()

        if side not in (
            "front",
            "back",
        ):

            raise ValueError(
                "Image side must be front or back."
            )

        safe_book_id = (
            str(book_id)
            .strip()
            .replace(" ", "_")
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        unique_id = uuid.uuid4().hex[:8]

        filename = (
            f"{safe_book_id}_"
            f"{side}_"
            f"{timestamp}_"
            f"{unique_id}.jpg"
        )

        output_path = os.path.join(
            self.upload_folder,
            filename
        )

        try:

            image = Image.open(
                source_path
            )

            image = self.normalize_image(
                image
            )

            image.save(
                output_path,
                format="JPEG",
                quality=92,
                optimize=True
            )

            return filename

        except Exception as error:

            if os.path.exists(
                output_path
            ):

                try:
                    os.remove(
                        output_path
                    )
                except Exception:
                    pass

            raise ValueError(
                f"Unable to save image: {error}"
            )

    # ========================================================
    # DELETE IMAGE
    # ========================================================

    def delete_image(
        self,
        filename: str
    ) -> bool:

        if not filename:
            return False

        # Prevent directory traversal.
        safe_name = os.path.basename(
            filename
        )

        file_path = os.path.join(
            self.upload_folder,
            safe_name
        )

        if not os.path.exists(
            file_path
        ):
            return False

        try:

            os.remove(
                file_path
            )

            return True

        except Exception:

            return False

    # ========================================================
    # GET IMAGE PATH
    # ========================================================

    def get_image_path(
        self,
        filename: str
    ) -> Optional[str]:

        if not filename:
            return None

        safe_name = os.path.basename(
            filename
        )

        file_path = os.path.join(
            self.upload_folder,
            safe_name
        )

        if not os.path.exists(
            file_path
        ):
            return None

        return file_path

    # ========================================================
    # IMAGE EXISTS
    # ========================================================

    def image_exists(
        self,
        filename: str
    ) -> bool:

        return (
            self.get_image_path(
                filename
            )
            is not None
        )

    # ========================================================
    # DELETE BOOK IMAGES
    # ========================================================

    def delete_book_images(
        self,
        front_image: str = "",
        back_image: str = ""
    ) -> None:

        if front_image:

            self.delete_image(
                front_image
            )

        if back_image:

            self.delete_image(
                back_image
            )


# ============================================================
# GLOBAL INSTANCE
# ============================================================

image_manager = ImageManager()


# ============================================================
# COMPATIBILITY FUNCTIONS
# ============================================================

def allowed_file(
    filename: str
) -> bool:

    return image_manager.allowed_file(
        filename
    )


def validate_image(
    file
) -> bool:

    return image_manager.validate_image(
        file
    )


def save_book_image(
    file,
    book_id: str,
    side: str
) -> Optional[str]:

    return image_manager.save_book_image(
        file,
        book_id,
        side
    )


def save_image_from_path(
    source_path: str,
    book_id: str,
    side: str
) -> Optional[str]:

    return image_manager.save_image_from_path(
        source_path,
        book_id,
        side
    )


def delete_image(
    filename: str
) -> bool:

    return image_manager.delete_image(
        filename
    )


def get_image_path(
    filename: str
) -> Optional[str]:

    return image_manager.get_image_path(
        filename
    )


def image_exists(
    filename: str
) -> bool:

    return image_manager.image_exists(
        filename
    )
