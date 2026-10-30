"""create initial roles

Revision ID: 7a91d2c4e6f0
Revises: 4b8a6c1d2e90
Create Date: 2026-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7a91d2c4e6f0"
down_revision: Union[str, Sequence[str], None] = "4b8a6c1d2e90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert the default roles."""
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Uuid()),
        sa.column(
            "permission",
            sa.Enum("CUSTOMER", "AGENT", "ADMIN", name="permissions"),
        ),
    )

    op.bulk_insert(
        roles_table,
        [
            {
                "id": "89ba3d7f-42c1-4a65-9f20-1b6e8d3c5a70",
                "permission": "CUSTOMER",
            },
            {
                "id": "4e2c8a61-7d35-4b90-a1f6-3c9e5d2b7a84",
                "permission": "AGENT",
            },
            {
                "id": "0f6d2b9a-5c31-4e87-b4a2-8d1f6c3e9b50",
                "permission": "ADMIN",
            },
        ],
    )


def downgrade() -> None:
    """Remove the default roles."""
    op.execute(
        sa.text(
            "DELETE FROM roles "
            "WHERE id IN ("
            "'89ba3d7f-42c1-4a65-9f20-1b6e8d3c5a70', "
            "'4e2c8a61-7d35-4b90-a1f6-3c9e5d2b7a84', "
            "'0f6d2b9a-5c31-4e87-b4a2-8d1f6c3e9b50'"
            ")"
        )
    )
