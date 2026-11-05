import re

from sqlalchemy.exc import IntegrityError

from app.exceptions.database import DatabaseIntegrityError, ForeignKeyViolationError
from app.exceptions.common import DuplicateAttributeError


def translate_integrity_error(
    exc: IntegrityError,
):
    """
    Convert a SQLAlchemy IntegrityError to a
    application specific exception
    """

    original_error = exc.orig
    message = str(original_error)

    if getattr(original_error, "sqlstate", None) == "23503":
        return ForeignKeyViolationError()

    match = re.search(
        r"UNIQUE constraint failed: ([^.]+)\.([^\s]+)",
        message,
    )

    if match:
        column = match.group(2)

        return DuplicateAttributeError(
            attribute=column,
        )

    return DatabaseIntegrityError(
        message="The database rejected the operation",
    )