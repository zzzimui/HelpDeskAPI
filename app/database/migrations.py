# Hub-and-Spoke design pattern

# I'm not sure if this file should be named 'migrations'
# but I'll leave it like that for now

# 1. Imports the original base
from app.database.base_class import Base  

from app.modules.categories.models import Category
from app.modules.refresh_tokens.models import RefreshToken
from app.modules.roles.models import Role
from app.modules.ticket_history.models import TicketHistory
from app.modules.ticket_messages.models import TicketMessage
from app.modules.tickets.models import Ticket
from app.modules.users.models import User


# This explicitly states: "I am exporting these classes on purpose"
# to avoid complaints that imported modules are not being used
__all__ = [
	"Base",
	"Category",
	"RefreshToken",
	"Role",
	"Ticket",
	"TicketHistory",
	"TicketMessage",
	"User",
]