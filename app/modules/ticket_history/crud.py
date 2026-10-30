from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base_crud import CRUDBase
from app.modules.ticket_history.models import TicketHistory
from app.modules.ticket_history.scheme import (
    TicketHistoryCreate,
    TicketHistoryUpdate
)

class CRUDTicketHistory(
    CRUDBase[TicketHistory, TicketHistoryCreate, TicketHistoryUpdate]
):
    async def log_event(
        self, 
        db: AsyncSession, 
        *, 
        obj_in: dict
    ) -> TicketHistory:
        db_obj = self.model(**obj_in)
        
        db.add(db_obj)
        await self.commit(db)
        await db.refresh(db_obj)

        return db_obj


crud_ticket_history = CRUDTicketHistory(TicketHistory)