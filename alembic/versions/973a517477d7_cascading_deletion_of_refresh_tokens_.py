"""Cascading deletion of refresh_tokens when a user is deleted

Revision ID: 973a517477d7
Revises: 7a91d2c4e6f0
Create Date: 2026-11-04 18:34:11.493092

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '973a517477d7'
down_revision: Union[str, Sequence[str], None] = '7a91d2c4e6f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("refresh_tokens_user_id_fkey", "refresh_tokens", type_="foreignkey")
    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("refresh_tokens_user_id_fkey", "refresh_tokens", type_="foreignkey")
    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens", "users",
        ["user_id"], ["id"],
    )
