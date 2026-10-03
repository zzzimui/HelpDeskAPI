from app.exceptions.base import AppModuleException

# class DatabaseAttributeError(AppModuleException):
#     def __init__(self, column: str, obj_name: str):
#         super().__init__(
#             message=f"{column!r} não é uma coluna válida da tabela {obj_name}",
#             status_code=422, 
#             code="UNPROCESSABLE_ENTITY"
#         )


class DatabaseIntegrityError(AppModuleException):
    def __init__(self, message: str = "Violação de integridade do banco de dados"):
        super().__init__(
            message=message,
            status_code=500,
            code="DATABASE_INTEGRITY_ERROR",
        )