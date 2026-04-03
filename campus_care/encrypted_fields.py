import base64
import hashlib

from django.conf import settings
from django.db import models


class EncryptedTextField(models.TextField):
    """
    Fernet-backed encrypted text storage with backward-compatible plaintext reads.
    Stored format: "enc::<fernet-token>".
    """

    prefix = "enc::"
    description = "Encrypted text"

    @classmethod
    def _get_fernet(cls):
        # Lazy import keeps startup resilient even before dependencies are installed.
        from cryptography.fernet import Fernet

        key_material = str(
            getattr(settings, "FIELD_ENCRYPTION_KEY", None) or settings.SECRET_KEY
        ).encode("utf-8")
        digest = hashlib.sha256(key_material).digest()
        fernet_key = base64.urlsafe_b64encode(digest)
        return Fernet(fernet_key)

    def _decrypt_if_needed(self, value):
        if value is None or value == "":
            return value
        if not isinstance(value, str):
            value = str(value)
        if not value.startswith(self.prefix):
            # Backward compatibility for existing plaintext rows.
            return value
        token = value[len(self.prefix) :].encode("utf-8")
        try:
            return self._get_fernet().decrypt(token).decode("utf-8")
        except Exception:
            # Never hard-fail reads on malformed legacy values.
            return value

    def from_db_value(self, value, expression, connection):
        return self._decrypt_if_needed(value)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            return self._decrypt_if_needed(value)
        return value

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == "":
            return value
        if not isinstance(value, str):
            value = str(value)
        if value.startswith(self.prefix):
            return value
        token = self._get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
        return f"{self.prefix}{token}"
