"""Create wallets table

Revision ID: 3a2943012782
Revises: d62bea66a1dd
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3a2943012782"
down_revision: Union[str, Sequence[str], None] = "d62bea66a1dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wallets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("wallet_type", sa.String(length=20), nullable=False),
        sa.Column(
            "opening_balance",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "current_balance",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("wallets")