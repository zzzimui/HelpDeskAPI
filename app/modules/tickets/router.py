from typing import Annotated
from uuid import UUID
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status
)
from fastapi_pagination import Page


# ┌─────────────────────────────────────────────────────────────────┐
# │  Exceptions                                                     │
# └─────────────────────────────────────────────────────────────────┘
from pydantic import ValidationError


# ┌─────────────────────────────────────────────────────────────────┐
# │  Models                                                         │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.tickets.models import TicketStatus


# ┌─────────────────────────────────────────────────────────────────┐
# │  Schemes                                                        │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.ticket_messages.scheme import (
    TicketMessageCreate,
    TicketMessagePublic
)
from app.modules.tickets.schema import (
    TicketCreate,
    TicketUserUpdate,
    TicketAgentUpdate,
    TicketAdminUpdate,
    TicketFilter,
    TicketPublic,
    TicketStatus
)


# ┌─────────────────────────────────────────────────────────────────┐
# │  Services                                                       │
# └─────────────────────────────────────────────────────────────────┘
from app.modules.tickets import service
from app.modules.ticket_messages.service import(
    generate_message,
    list_messages
)


# ┌─────────────────────────────────────────────────────────────────┐
# │  Deps                                                           │
# └─────────────────────────────────────────────────────────────────┘
from app.core.deps import SessionDep
from app.modules.auth.deps import CurrentActiveUser, CurrentSuperuser




router = APIRouter()

ROLE_TO_SCHEMA = {
    "CUSTOMER": TicketUserUpdate,
    "AGENT":    TicketAgentUpdate,
    "ADMIN":    TicketAdminUpdate,
}


# region Static

# ── GET Static ──────────────────────────────────────────────────────────────

@router.get("/", response_model=Page[TicketPublic])
async def list_tickets(
    session: SessionDep, 
    user: CurrentActiveUser, 
    filter: TicketFilter = Depends(),
    page: int = 1,
    limit: int = 100
):
    return await service.list_tickets(
        session, 
        user,
        filter,
        page,
        limit
    )


# ── POST Static ──────────────────────────────────────────────────────────────

@router.post("/")
async def create_ticket(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket: TicketCreate,
):
    return await service.generate_ticket(session, user, ticket)


# region Dynamic

# ── GET Dynamic ──────────────────────────────────────────────────────────────

@router.get("/{ticket_id}", response_model=TicketPublic)
async def get_ticket_or_404(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket_id: UUID,
):
    return await service.get_ticket_or_404(
        session, 
        user,
        ticket_id,
    )


@router.get("/{ticket_id}/messages", response_model=Page[TicketMessagePublic])
async def list_ticket_messages(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket_id: UUID,
    page: int = 1,
    limit: int = 100
):
    return await list_messages(
        session,
        user,
        ticket_id,
        page,
        limit
    )


# ── POST Dynamic ──────────────────────────────────────────────────────────────

@router.post("/{ticket_id}/messages", response_model=TicketMessagePublic)
async def create_ticket_message(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket_id: UUID,
    content: TicketMessageCreate
):
    return await generate_message(
        session,
        user,
        ticket_id,
        content, 
    )


# ── PATCH Dynamic ──────────────────────────────────────────────────────────────

@router.patch("/{ticket_id}", response_model=TicketPublic)
async def update_ticket(
    session: SessionDep,
    user: CurrentActiveUser,
    ticket_id: UUID,
    payload: Annotated[
        TicketUserUpdate | TicketAgentUpdate | TicketAdminUpdate,
        Body(
            openapi_examples={
                "User": {
                    "summary": "Customer-editable fields",
                    "value": {"title": "...", "description": "..."}
                },
                "Agent": {
                    "summary": "Agent-editable fields",
                    "value": {"priority": "low", "status": "open"}
                },
                "Admin": {
                    "summary": "Admin-editable fields",
                    "value": {
                        "title": "...",
                        "description": "...",
                        "status": "open",
                        "priority": "low",
                        "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "assigned_agent_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    }
                }
            }
        )
    ],
):

    # Is the client trying to send an empty payload?
    payload_data = payload.model_dump(exclude_unset=True)
    if not payload_data:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"message": "At least one field must be provided"},
        )

    # Does the client have the privilege to modify the requested resource?
    schema_cls = ROLE_TO_SCHEMA.get(user.role.permission.name)
    if schema_cls is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Role not allowed")

    # Revalidates the raw payload against the user role schema
    # here, forbidden fields are effectively rejected
    try:
        schema = schema_cls.model_validate(payload_data)
    except ValidationError as e:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Fields not permitted for your role",
                "errors": e.errors(include_input=False),
            },
        )

    return await service.update_ticket(session, user, schema.model_dump(exclude_unset=True), ticket_id)


@router.patch("/{ticket_id}/assign", response_model=TicketPublic)
async def assign_agent(
    session: SessionDep,
    user: CurrentSuperuser,
    ticket_id: UUID,
    agent_id: UUID
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