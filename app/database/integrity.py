import re

from sqlalchemy.exc import IntegrityError

from app.exceptions.database import DatabaseIntegrityError
from app.exceptions.common import DuplicateAttributeError


def translate_integrity_error(
    exc: IntegrityError,
):
    """
    Converte um IntegrityError do SQLAlchemy em uma
    exceção específica da aplicação.
    """

    original_error = exc.orig
    message = str(original_error)

    # SQLite:
    # UNIQUE constraint failed: users.username
    match = re.search(
        r"UNIQUE constraint failed: ([^.]+)\.([^\s]+)",
        message,
    )

    if match:
        # table = match.group(1)
        column = match.group(2)

        return DuplicateAttributeError(
            attribute=column,
        )

    return DatabaseIntegrityError(
        message="The database rejected the operation",
    )