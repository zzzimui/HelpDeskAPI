from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base_crud import CRUDBase
from app.modules.ticket_messages.models import TicketMessage
from app.modules.ticket_messages.scheme import (
    TicketMessageCreate,
    TicketMessageUpdate
)


class CRUDTicketMessage(CRUDBase[TicketMessage, TicketMessageCreate, TicketMessageUpdate]):
    async def create_ticket_message(
        self, 
        db: AsyncSession, 
        obj_in: dict
    ) -> (TicketMessage|None):
        # Instantiate the SQLAlchemy model by unpacking the dictionary
        db_obj = self.model(**obj_in)
        
        db.add(db_obj)
        await self.commit(db)
        await db.refresh(db_obj)

        return db_obj


crud_ticket_message = CRUDTicketMessage(TicketMessage)