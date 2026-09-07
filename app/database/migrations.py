# Hub-and-Spoke design pattern

# I'm not sure if this file should be named 'migrations'
# but I'll leave it like that for now

# 1. Imports the original base
from app.database.base_class import Base  

# 2. Import all application models here so that Alembic becomes aware of them
from app.modules.users.models import User


# This explicitly states: "I am exporting these classes on purpose"
# to avoid complaints that imported modules are not being used
__all__ = ["Base", "User"]