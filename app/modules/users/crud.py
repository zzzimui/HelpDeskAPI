from app.modules.users.models import User
from app.modules.users.schema import UserCreate, UserUpdate
from app.database.base_crud import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, exists, or_, select

from app.modules.ticket_history.models import TicketHistory
from app.modules.ticket_messages.models import TicketMessage
from app.modules.tickets.models import Ticket


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def register_user(self, db: AsyncSession, obj_in: dict) -> (User|None):
        db_obj = self.model(**obj_in)
        
        db.add(db_obj)
        await self.commit(db)
        await db.refresh(db_obj)

        # return db_obj

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, db: AsyncSession, username: str) -> User:
        result = await db.execute(select(self.model).where(self.model.username == username))
        return result.scalar_one_or_none()

    async def update_user_status(self, db: AsyncSession, *, db_obj: User):
        db.add(db_obj)
        await self.commit(db)
        await db.refresh(db_obj)

        return db_obj

    async def check_associated_records(self, db: AsyncSession, user: User):
        return await db.scalar(
            select(
                or_(
                    # has ticket?
                    exists().where(Ticket.customer_id == user.id),
                    exists().where(Ticket.assigned_agent_id == user.id),
                    # has message?
                    exists().where(TicketMessage.author_id == user.id),
                    # has history?
                    exists().where(TicketHistory.user_id == user.id),
                )
            )
        )


crud_user = CRUDUser(User)