from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_pagination import Page

from app.modules.tickets import service
from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.scheme import (
    TicketCreate,
    TicketUpdate, 
    TicketAgentUpdate,
    TicketAdminUpdate,
    TicketFilter,
    TicketPublic,
    TicketStatus
)

from app.core.deps import SessionDep
from app.modules.auth.deps import CurrentActiveUser, CurrentSuperuser

router = APIRouter()


# region Static

# ── GET ──────────────────────────────────────────────────────────────

@router.get("/", response_model=Page[TicketPublic])
async def list_tickets(
    session: SessionDep, 
    user: CurrentActiveUser, 
    filter: TicketFilter = Depends(),
    page: int = 1,
    limit: int = 100
):
    return await service.get_tickets(
        session, 
        user,
        filter,
        page,
        limit
    )

# ── POST ──────────────────────────────────────────────────────────────


@router.post("/")
async def create_ticket(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket: TicketCreate,
):
    return await service.generate_ticket(session, user, ticket)



# region Dynamic

# ── GET ──────────────────────────────────────────────────────────────

@router.get("/{ticket_id}", response_model=TicketPublic)
async def get_ticket(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket_id: str,
):
    return await service.get_ticket(
        session, 
        user,
        ticket_id,
    )


# ── PATCH ──────────────────────────────────────────────────────────────

@router.patch("/{ticket_id}", response_model=TicketPublic)
async def update_ticket(
    session: SessionDep,
    user: CurrentActiveUser,
    updated_ticket: TicketUpdate,
    agent_ticket: TicketAgentUpdate,
    admin_ticket: TicketAdminUpdate,
    ticket_id: str,
):
    return await service.update_ticket(
        session, 
        user,
        updated_ticket,
        ticket_id,
    )

@router.patch("/{ticket_id}/assign", response_model=TicketPublic)
async def assign_agent(
    session: SessionDep,
    user: CurrentSuperuser,
    ticket_id: str,
    agent_id: str
):
    """
    Admin function:

    Admin assigns an agent.
    """
    return await service.assign_agent(
        session, 
        user,
        ticket_id,
        agent_id,
    )


@router.patch("/{ticket_id}/status", response_model=TicketPublic)
async def change_status(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket_id: UUID,
    target_status: TicketStatus
):
    return await service.change_status(
        session, 
        user,
        ticket_id,
        target_status
    )