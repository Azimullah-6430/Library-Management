# utils/image_manager.py

import os
import uuid
from datetime import datetime

from PIL import Image, ImageOps


class ImageManager:
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    MAX_IMAGE_SIZE = 2400

    def __init__(self, upload_folder="uploads/book_covers"):
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

    def allowed_file(self, filename):
        if not filename or "." not in filename:
            return False

        extension = filename.rsplit(".", 1)[1].lower()
        return extension in self.ALLOWED_EXTENSIONS

    def normalize_image(self, image):
        image = ImageOps.exif_transpose(image)

        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, "white")
            alpha = image.getchannel("A")
            background.paste(image, mask=alpha)
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        width, height = image.size

        if max(width, height) > self.MAX_IMAGE_SIZE:
            scale = self.MAX_IMAGE_SIZE / max(width, height)
            new_size = (
                int(width * scale),
                int(height * scale),
            )
            image = image.resize(
                new_size,
                Image.Resampling.LANCZOS
            )

        return image

    def save_image(self, file_storage, book_id, image_type):
        if not file_storage or not file_storage.filename:
            return ""

        if not self.allowed_file(file_storage.filename):
            raise ValueError(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG, or WEBP."
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:10]

        filename = (
            f"{book_id}_{image_type}_"
            f"{timestamp}_{unique_id}.jpg"
        )

        file_path = os.path.join(
            self.upload_folder,
            filename
        )

        image = Image.open(file_storage)
        image = self.normalize_image(image)

        image.save(
            file_path,
            format="JPEG",
            quality=92,
            optimize=True
        )

        return filename

    def save_uploaded_image(self, file_storage, book_id, image_type):
        return self.save_image(
            file_storage,
            book_id,
            image_type
        )

    def delete_image(self, filename):
        if not filename:
            return False

        file_path = os.path.join(
            self.upload_folder,
            os.path.basename(filename)
        )

        if os.path.exists(file_path):
            os.remove(file_path)
            return True

        return False

    def get_image_path(self, filename):
        if not filename:
            return None

        file_path = os.path.join(
            self.upload_folder,
            os.path.basename(filename)
        )

        return file_path if os.path.exists(file_path) else None


image_manager = ImageManager()
