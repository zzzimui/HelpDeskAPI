from typing import Dict, Set
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

# ┌─────────────────────────────────────────────────────────────────┐
# │  Exceptions                                                     │
# └─────────────────────────────────────────────────────────────────┘
from sqlalchemy.exc import DatabaseError
from app.modules.users.exceptions import (
    InactiveUserError,
    UnprivilegedUserError,
    InvalidTransitionError
)
from app.modules.tickets.exceptions import (
    InvalidPermissionError, 
    AppDatabaseError
)

# ┌─────────────────────────────────────────────────────────────────┐
# │  Models                                                         │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.users.models import User
from app.modules.tickets.models import Ticket, TicketStatus

# ┌─────────────────────────────────────────────────────────────────┐
# │  Schemes                                                        │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.tickets.scheme import (
    TicketCreate,
    
    TicketUpdate,
    TicketAgentUpdate,
    TicketAdminUpdate,
    
    TicketPublic,
    TicketFilter
)

# ┌─────────────────────────────────────────────────────────────────┐
# │  Crud                                                           │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.tickets.crud import crud_ticket


# ┌─────────────────────────────────────────────────────────────────┐
# │  Services                                                       │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.users.service import read_user
from app.modules.categories.service import get_category_by_id
from app.modules.roles.service import get_role




# Status transitions allowed
TRANSITIONS: Dict[TicketStatus, Set[TicketStatus]] = {
    TicketStatus.OPEN:        {TicketStatus.IN_PROGRESS},
    TicketStatus.IN_PROGRESS: {TicketStatus.OPEN, TicketStatus.RESOLVED},
    TicketStatus.RESOLVED:    {TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.CLOSED:      {TicketStatus.RESOLVED},
}


# region HELPER
# ── create functions ──────────────────────────────────────────────────────────────

# async def ...

# ── END of helper functions ──────────────────────────────────────────────────────────────




# region CREATE
# ── create functions ──────────────────────────────────────────────────────────────

async def generate_ticket(
        db: AsyncSession, 
        user: User, 
        ticket: TicketCreate,
    ):
    # Precondition to ensure that the category exists
    await get_category_by_id(db, ticket.category_id)

    user_role = await get_role(db, role_id=user.role_id)
    user_permission = user_role.permission.name

    if not user_permission is "CUSTOMER":
        raise InvalidPermissionError(permission=user_permission)

    obj_data = ticket.model_dump()

    obj_data["id"] = uuid4()
    # Needs be an authenticated user
    obj_data["customer_id"] = user.id
    # The initial status must be open
    obj_data["status"] = "OPEN"

    try:
        await crud_ticket.create_ticket(db, obj_in_data=obj_data)
    except DatabaseError:
        raise AppDatabaseError()

    return {"Message": "The ticket was successfully created!"}

# ── END of create functions ──────────────────────────────────────────────────────────────


# region READ
# ── read functions ──────────────────────────────────────────────────────────────

async def get_ticket(
        db: AsyncSession, 
        user: User,
        ticket_id: str
    ) -> TicketPublic:
    """
    Gets a specific ticket based on its ID.
    """
    role_user = await get_role(db, user.role_id)

    queries = []

    if role_user.permission.name == "CUSTOMER":
        queries.append(crud_ticket.model.customer_id == user.id)
    elif role_user.permission.name == "AGENT":
        queries.append(crud_ticket.model.assigned_agent_id == user.id)

    return await crud_ticket.get(
        db,
        ticket_id,
        extra_conditions=queries or None
    )

async def get_tickets(
        db: AsyncSession, 
        user: User,
        filter: TicketFilter,
        page: int = 1,
        limit: int = 100
    ) -> Page[Ticket]:
    role_user = await get_role(db, user.role_id)

    queries = []

    # Extrai apenas os campos preenchidos no schema Pydantic
    selected_filter = filter.model_dump(exclude_none=True)

    if role_user.permission.name == "CUSTOMER":
        # retorne ticket(x) somente se ele pertencer a esse usuário
        queries.append(crud_ticket.model.customer_id == user.id)

    elif role_user.permission.name == "AGENT":
        # retorna ticket(x) apenas se tcket(x) for atribuido à ele
        queries.append(crud_ticket.model.assigned_agent_id == user.id)

    return await crud_ticket.get_multi(
        db, 
        filters=selected_filter,
        extra_conditions=queries or None,
        page=page,
        limit=limit,
    )

# ── END of read functions ──────────────────────────────────────────────────────────────



# region UPDATE
# ── update functions ──────────────────────────────────────────────────────────────

async def update_ticket(
    db: AsyncSession, 
    user: User, 
    updated_ticket: TicketUpdate,
    agent_ticket: TicketAgentUpdate,
    admin_ticket: TicketAdminUpdate,
    ticket_id: str
) -> Ticket:
    # CUSTOMER
    # Pode alterar determinadas informações enquanto o ticket estiver OPEN.
    role_user = await get_role(db, user.role_id)
    ticket = await get_ticket(db, user, ticket_id)

    # customer
    if ticket.status.name == "OPEN" and role_user.permission.name == "CUSTOMER":
        return await crud_ticket.update(db, db_obj=updated_ticket)
    # agent
    elif role_user.permission.name == "AGENT":
        return await crud_ticket.update(db, db_obj=agent_ticket)

    # admin
    return await crud_ticket.update(db, db_obj=admin_ticket)

    

async def assign_agent(
    db: AsyncSession,
    admin_user: User, 
    ticket_id: str,
    agent_id: str
):
    # agent_id pertence a um usuário?
    target_agent: User = await read_user(db, agent_id)

    if target_agent.is_active is False:
        raise InactiveUserError()

    agent_role = await get_role(db, target_agent.role_id)
    if not agent_role.permission.name == "AGENT":
        raise InvalidPermissionError(agent_role.permission.name)

    target_ticket = await get_ticket(db, admin_user, ticket_id)
    
    updated_ticket = {
        "assigned_agent_id": agent_id
    }

    return await crud_ticket.update(db, db_obj=target_ticket, obj_in=updated_ticket)


async def change_status(
    db: AsyncSession, 
    agent: User, 
    ticket_id: UUID,
    target_status: TicketStatus
) -> Ticket:
    current_ticket: Ticket = await get_ticket(db, agent, ticket_id)

    # Verifies whether the transition requested by the agent is valid
    if not target_status in TRANSITIONS.get(current_ticket.status, set()):
        raise InvalidTransitionError(current_ticket.status.value, target_status.value)

    ticket_updated = {"status": target_status}
    
    return await crud_ticket.update(db, db_obj=current_ticket, obj_in=ticket_updated)

# ── END of update functions ──────────────────────────────────────────────────────────────


    
