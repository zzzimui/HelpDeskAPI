"""enforce unique role permissions

Revision ID: 4b8a6c1d2e90
Revises: 36cd91e27783
Create Date: 2026-10-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4b8a6c1d2e90"
down_revision: Union[str, Sequence[str], None] = "36cd91e27783"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ranked_roles = """
        SELECT id,
               FIRST_VALUE(id) OVER (PARTITION BY permission ORDER BY id) AS canonical_id,
               ROW_NUMBER() OVER (PARTITION BY permission ORDER BY id) AS role_rank
        FROM roles
    """
    op.execute(
        sa.text(
            f"""
            WITH ranked_roles AS ({ranked_roles})
            UPDATE users AS user_row
            SET role_id = ranked_roles.canonical_id
            FROM ranked_roles
            WHERE user_row.role_id = ranked_roles.id
              AND ranked_roles.role_rank > 1
            """
        )
    )
    op.execute(
        sa.text(
            f"""
            WITH ranked_roles AS ({ranked_roles})
            DELETE FROM roles AS role_row
            USING ranked_roles
            WHERE role_row.id = ranked_roles.id
              AND ranked_roles.role_rank > 1
            """
        )
    )
    op.create_unique_constraint("uq_roles_permission", "roles", ["permission"])


def downgrade() -> None:
    op.drop_constraint("uq_roles_permission", "roles", type_="unique")