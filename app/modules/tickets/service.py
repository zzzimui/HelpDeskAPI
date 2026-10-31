from fastapi import HTTPException, status
from typing import Dict, Set
from fastapi_pagination import Page

from copy import deepcopy

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import make_transient

from uuid import UUID, uuid4
from app.utils.datetime import get_naive_utc

# ┌─────────────────────────────────────────────────────────────────┐
# │  Exceptions                                                     │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.users.exceptions import (
    InactiveUserError,
    InvalidTransitionError
)
from app.modules.tickets.exceptions import InvalidPermissionError

# ┌─────────────────────────────────────────────────────────────────┐
# │  Models                                                         │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.users.models import User
from app.modules.tickets.models import Ticket, TicketStatus

# ┌─────────────────────────────────────────────────────────────────┐
# │  Schemes                                                        │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.tickets.schema import TicketCreate, TicketFilter

# ┌─────────────────────────────────────────────────────────────────┐
# │  Crud                                                           │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.tickets.crud import crud_ticket


# ┌─────────────────────────────────────────────────────────────────┐
# │  Services                                                       │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.users.service import read_user
from app.modules.categories.service import get_category_or_404
from app.modules.roles.service import get_role
from app.modules.ticket_history.service import generate_ticket_event


# ┌─────────────────────────────────────────────────────────────────┐
# │  Global                                                         │
# └─────────────────────────────────────────────────────────────────┘
# Status transitions allowed
TRANSITIONS: Dict[TicketStatus, Set[TicketStatus]] = {
    TicketStatus.OPEN:        {TicketStatus.IN_PROGRESS},
    TicketStatus.IN_PROGRESS: {TicketStatus.OPEN, TicketStatus.RESOLVED},
    TicketStatus.RESOLVED:    {TicketStatus.IN_PROGRESS, TicketStatus.CLOSED},
    TicketStatus.CLOSED:      {TicketStatus.RESOLVED},
}



# region Helper
# ── helper functions ──────────────────────────────────────────────────────────────

def _snapshot_ticket(ticket: Ticket) -> dict:
    copy = deepcopy(ticket)
    make_transient(copy)   # removes the link with the Session
    return copy


async def _validate_update_requirements(
    db: AsyncSession, 
    user: User, 
    schema: dict,
    ticket: Ticket
) -> None:
    # Is the customer's ticket open for modification?
    if user.role.permission.name == "CUSTOMER" and ticket.status.name != "OPEN":
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"message": f"Only open tickets can be updated by customers"}
        )

    # Is the user trying to change the category?
    # If so, does this category exist?
    category_id = schema.get("category_id")
    if category_id:
        await get_category_or_404(db, category_id)


async def _update_current_ticket_state(
    db: AsyncSession, 
    user: User, 
    schema: dict,
    ticket_id: UUID
):
    target_status = schema.get("status")
    if target_status:
        await change_status(db, user, ticket_id, target_status)

    assigned_agent = schema.get("assigned_agent")
    if assigned_agent:
        await assign_agent(db, user, ticket_id, assigned_agent)


# ── END OF helper functions ──────────────────────────────────────────────────────────────



# region CREATE
# ── create functions ──────────────────────────────────────────────────────────────

async def generate_ticket(
    db: AsyncSession, 
    user: User, 
    ticket: TicketCreate,
):
    # Precondition to ensure the ticket category exists
    await get_category_or_404(db, ticket.category_id)

    role_user = await get_role(db, user.role_id)
    if not role_user.permission.name == "CUSTOMER":
        raise InvalidPermissionError(permission=role_user.permission.name)

    obj_data = ticket.model_dump()
    obj_data["id"] = uuid4()
    obj_data["customer_id"] = user.id
    # The initial status must be open
    obj_data["status"] = "OPEN"

    await crud_ticket.create_ticket(db, obj_in_data=obj_data)

    await generate_ticket_event(
        db,
        user,
        ticket_id=obj_data["id"],
        action="CREATED",
        current_ticket=None,
        new_state={"status": "OPEN"},
    )

    return {"Message": "The ticket was successfully created!"}

# ── END of create functions ──────────────────────────────────────────────────────────────


# region READ
# ── read functions ──────────────────────────────────────────────────────────────

async def get_ticket_or_404(
    db: AsyncSession, 
    user: User,
    ticket_id: str
) -> Ticket:
    """
    Gets a specific ticket based on its ID.
    """
    role_user = await get_role(db, user.role_id)

    queries = []

    if role_user.permission.name == "CUSTOMER":
        queries.append(crud_ticket.model.customer_id == user.id)
    elif role_user.permission.name == "AGENT":
        queries.append(crud_ticket.model.assigned_agent_id == user.id)

    ticket = await crud_ticket.get(
        db,
        ticket_id,
        extra_conditions=queries or None
    )
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found; Verify whether the provided ticket belongs to the authenticated user",
        )

    return ticket

async def list_tickets(
    db: AsyncSession, 
    user: User,
    filter: TicketFilter,
    page: int = 1,
    limit: int = 100
) -> Page[Ticket]:
    role_user = await get_role(db, user.role_id)

    queries = []

    # Extract only the fields filled in the Pydantic schema
    selected_filter = filter.model_dump(exclude_none=True)

    if role_user.permission.name == "CUSTOMER":
        queries.append(crud_ticket.model.customer_id == user.id)

    elif role_user.permission.name == "AGENT":
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
    schema: dict,
    ticket_id: str
) -> Ticket:
    # Does the target ticket exist?
    target_ticket = await get_ticket_or_404(db, user, ticket_id)

    # Does the request meet all the requirements?
    await _validate_update_requirements(
        db, 
        user,
        schema=schema,
        ticket=target_ticket
    )

    # preserves the current state of the ticket 
    # while the actual ticket is subsequently updated
    old_snapshot: Ticket = _snapshot_ticket(target_ticket)

    # records the updates in the database
    await _update_current_ticket_state(
        db,
        user,
        schema,
        ticket_id=target_ticket.id
    )

    # Finally:
    await generate_ticket_event(
        db,
        user,
        ticket_id=target_ticket.id,
        # action
        action="UPDATED",
        current_ticket=old_snapshot,
        new_state=schema
    )

    schema["updated_at"] = get_naive_utc()
    updated_ticket = await crud_ticket.update(db, db_obj=target_ticket, obj_in=schema)

    return updated_ticket

    

async def assign_agent(
    db: AsyncSession,
    admin_user: User, 
    ticket_id: UUID,
    agent_id: UUID
):
    """
    Assigns a ticket to an agent
    """

    # Does the provided agent_id belong to a user?
    target_agent: User = await read_user(db, agent_id)

    # Is it active?
    if target_agent.is_active is False:
        raise InactiveUserError()

    # Does it act as an agent?
    agent_role = await get_role(db, target_agent.role_id)
    if not agent_role.permission.name == "AGENT":
        raise InvalidPermissionError(agent_role.permission.name)

    # If so...
    target_ticket = await get_ticket_or_404(db, admin_user, ticket_id)
    updated_ticket = await crud_ticket.update(
        db, 
        db_obj=target_ticket, 
        obj_in={"assigned_agent_id": agent_id}
    )

    # Finally:
    await generate_ticket_event(
        db,
        user=admin_user,
        ticket_id=updated_ticket.id,
        action="ASSIGNED",
        current_ticket_state={"assigned_agent_id": target_ticket.assigned_agent_id},
        new_state={"assigned_agent_id": agent_id}
    )

    return updated_ticket


async def change_status(
    db: AsyncSession, 
    user: User, 
    ticket_id: UUID,
    target_status: TicketStatus
) -> Ticket:
    current_ticket: Ticket = await get_ticket_or_404(db, user, ticket_id)

    # Is the transition via the agent valid?
    if not target_status in TRANSITIONS.get(current_ticket.status, set()):
        raise InvalidTransitionError(current_ticket.status.value, target_status)

    # If so...
    ticket_updated = {"status": target_status}

    if target_status.value == "open" or target_status.value == "in_progress":
        ticket_updated["resolved_at"] = None
        ticket_updated["closed_at"] = None
    elif target_status.value == "resolved":
        ticket_updated["resolved_at"] = get_naive_utc()
        ticket_updated["closed_at"] = None
    elif target_status.value == "closed":
        ticket_updated["closed_at"] = get_naive_utc()

    ticket_updated["updated_at"] = get_naive_utc()

    updated_ticket = await crud_ticket.update(db, db_obj=current_ticket, obj_in=ticket_updated)
    return updated_ticket

# ── END of update functions ──────────────────────────────────────────────────────────────


    
