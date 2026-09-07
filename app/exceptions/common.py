from app.exceptions.base import AppModuleException

class DuplicateAttributeError(AppModuleException):
    def __init__(
            self, 
            attribute: str | None = None,
            constraint: str | None = None
        ):
        super().__init__(
            message=(
                f"O atributo {attribute!r} já está em uso"
                if attribute
                else "O valor único inserido já está em uso"
            ),
            status_code=409,  # Conflict
            code="DUPLICATE_ATTRIBUTE"
        )

        self.attribute = attribute
        self.constraint = constraint