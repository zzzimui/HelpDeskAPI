"""create initial categories

Revision ID: 36cd91e27783
Revises: 2d7c371a4d44
Create Date: 2026-09-23 16:03:52.668192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.utils import datetime

# revision identifiers, used by Alembic.
revision: str = '36cd91e27783'
down_revision: Union[str, Sequence[str], None] = '2d7c371a4d44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


time_now = datetime.get_naive_utc()


def upgrade() -> None:
    """Upgrade schema."""
    categories_table = sa.table(
        "categories",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String(length=32)),
        sa.column("description", sa.String(length=1000)),
        sa.column("is_active", sa.Boolean()),
        sa.column("is_deleted", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
    )

    op.bulk_insert(
        categories_table,
        [
            {
                "id": "7f1e8a4b-2c6d-4f91-9d3a-5b8e2c7a1f04",
                "name": "Hardware",
                "description": "Hardware-related problems",
                "is_active": True,
                "is_deleted": False,
                "created_at": time_now,
            },
            {
                "id": "b3c9d6e2-8a17-4f5b-91c4-6e2d7a0f3b85",
                "name": "Software",
                "description": "Software-related problems",
                "is_active": True,
                "is_deleted": False,
                "created_at": time_now,
            },
            {
                "id": "c5a2f8d1-6b39-4e07-a4c2-9f1d7b5e8a63",
                "name": "Network",
                "description": "Network-related problems",
                "is_active": True,
                "is_deleted": False,
                "created_at": time_now,
            },
            {
                "id": "e8d4b1f7-3c26-4a90-85e1-7b6d2f9a0c54",
                "name": "Access",
                "description": "Issues related to access and credentials",
                "is_active": True,
                "is_deleted": False,
                "created_at": time_now,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text(
            "DELETE FROM categories "
            "WHERE name IN ('Hardware', 'Software', 'Network', 'Access')"
        )
    )
