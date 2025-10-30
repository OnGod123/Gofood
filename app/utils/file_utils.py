import imghdr
import os

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_FILE_SIZE_MB = 5  # adjust as needed

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_storage):
    """Validate uploaded image file type and size."""
    filename = file_storage.filename
    if not allowed_file(filename):
        raise ValueError("Unsupported file type")

    file_storage.seek(0, os.SEEK_END)
    size_mb = file_storage.tell() / (1024 * 1024)
    file_storage.seek(0)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError("File too large (max 5MB)")

    # check file signature
    header = file_storage.read(512)
    file_storage.seek(0)
    if not imghdr.what(None, header):
        raise ValueError("File is not a valid image")

    return True

