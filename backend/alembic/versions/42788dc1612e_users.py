"""your_revision_message.

Revision ID: 42788dc1612e
Create Date: 2025-10-18 09:14:23.100438

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "42788dc1612e"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MAIN_SCHEMA = "auth_service"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {MAIN_SCHEMA}")

    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("stytch_user_id", sa.String(length=100), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_obsolete", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        schema=MAIN_SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("users", schema=MAIN_SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {MAIN_SCHEMA} CASCADE")
