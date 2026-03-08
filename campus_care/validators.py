import os
from django.core.exceptions import ValidationError


ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx',
    '.xls', '.xlsx', '.txt', '.zip', '.csv',
}
ALLOWED_SUBMISSION_EXTENSIONS = ALLOWED_DOCUMENT_EXTENSIONS | {
    '.py', '.java', '.cpp', '.c', '.html', '.css', '.js', '.ipynb',
}
MAX_FILE_SIZE_MB = 10


def validate_file_upload(file, allowed_extensions, max_size_mb=MAX_FILE_SIZE_MB):
    """Validate file extension and size."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f'File type "{ext}" is not allowed. '
            f'Allowed types: {", ".join(sorted(allowed_extensions))}'
        )
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File too large. Maximum size: {max_size_mb}MB.')


def validate_image_upload(file):
    """Validate image files (profile pictures, ID pictures)."""
    validate_file_upload(file, ALLOWED_IMAGE_EXTENSIONS, max_size_mb=5)


def validate_document_upload(file):
    """Validate document files (materials, attachments)."""
    validate_file_upload(file, ALLOWED_DOCUMENT_EXTENSIONS)


def validate_submission_upload(file):
    """Validate student submission files."""
    validate_file_upload(file, ALLOWED_SUBMISSION_EXTENSIONS)
