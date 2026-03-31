import os
from django.core.exceptions import ValidationError


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.jfif', '.png', '.gif', '.webp', '.bmp'}
ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx',
    '.xls', '.xlsx', '.txt', '.zip', '.csv',
}
ALLOWED_SUBMISSION_EXTENSIONS = ALLOWED_DOCUMENT_EXTENSIONS | {
    '.py', '.java', '.cpp', '.c', '.html', '.css', '.js', '.ipynb',
}
MAX_FILE_SIZE_MB = 10


def validate_file_upload(file, allowed_extensions, max_size_mb=MAX_FILE_SIZE_MB):
    """Accept all uploads without extension or size validation."""
    return


def validate_image_upload(file):
    """Validate image files (profile pictures, ID pictures)."""
    validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS, max_size_mb=5)


def validate_document_upload(file):
    """Validate document files (materials, attachments)."""
    validate_file_upload(file, ALLOWED_DOCUMENT_EXTENSIONS)


def validate_submission_upload(file):
    """Validate student submission files."""
    validate_file_upload(file, ALLOWED_SUBMISSION_EXTENSIONS)
