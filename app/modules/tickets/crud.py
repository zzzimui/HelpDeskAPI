from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tickets.models import Ticket
from app.database.base_crud import CRUDBase
from app.modules.tickets.schema import(
    TicketCreate, 
    TicketUpdate,
)

class CRUDTicket(CRUDBase[Ticket, TicketCreate, TicketUpdate]):
    async def create_ticket(
        self,
        db: AsyncSession, 
        *,
        obj_in_data: dict
    ):
        db_obj = self.model(**obj_in_data)

        db.add(db_obj)
        await self.commit(db)
        await db.refresh(db_obj)
        return db_obj


crud_ticket = CRUDTicket(Ticket)