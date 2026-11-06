from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    async def compare_refresh_tokens(
        self,
        db: AsyncSession,
        token_hash_in: str
        ):
        result = await db.execute(
            select(self.model).where(self.model.token_hash == token_hash_in)
        )
        return result.scalar_one_or_none()


crud_refresh_tokens = CRUDRefreshTokens(RefreshToken)