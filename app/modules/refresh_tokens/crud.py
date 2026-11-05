from app.database.base_crud import CRUDBase
from app.modules.refresh_tokens.models import RefreshToken
from app.modules.refresh_tokens.schema import RefreshTokenCreate, RefreshTokenUpdate


class CRUDRefreshTokens(
    CRUDBase
    [
    RefreshToken, 
    RefreshTokenCreate, 
    RefreshTokenUpdate
    ]
):
    pass


crud_refresh_tokens = CRUDRefreshTokens(RefreshToken)