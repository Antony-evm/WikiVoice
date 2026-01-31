"""add sessions and queries tables.

Revision ID: a1b2c3d4e5f6
Revises: 42788dc1612e
Create Date: 2026-01-31

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "42788dc1612e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MAIN_SCHEMA = "auth_service"


def upgrade() -> None:
    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column("session_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey(f"{MAIN_SCHEMA}.users.user_id"),
            nullable=False,
        ),
        sa.Column(
            "title", sa.String(length=255), server_default="New Conversation", nullable=False
        ),
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
    op.create_index("idx_sessions_user_id", "sessions", ["user_id"], schema=MAIN_SCHEMA)

    # Create queries table
    op.create_table(
        "queries",
        sa.Column("query_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey(f"{MAIN_SCHEMA}.sessions.session_id"),
            nullable=False,
        ),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("input_mode", sa.String(length=10), server_default="text", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        schema=MAIN_SCHEMA,
    )
    op.create_index("idx_queries_session_id", "queries", ["session_id"], schema=MAIN_SCHEMA)


def downgrade() -> None:
    # Drop queries table
    op.drop_index("idx_queries_session_id", table_name="queries", schema=MAIN_SCHEMA)
    op.drop_table("queries", schema=MAIN_SCHEMA)

    # Drop sessions table
    op.drop_index("idx_sessions_user_id", table_name="sessions", schema=MAIN_SCHEMA)
    op.drop_table("sessions", schema=MAIN_SCHEMA)

    # Restore old columns to users table
    op.add_column(
        "users",
        sa.Column("user_authentication_method", sa.String(50), nullable=True),
        schema=MAIN_SCHEMA,
    )
    op.add_column(
        "users",
        sa.Column("device_token", sa.String(255), nullable=True),
        schema=MAIN_SCHEMA,
    )
    op.add_column(
        "users",
        sa.Column("user_status_id", sa.Integer(), nullable=True),
        schema=MAIN_SCHEMA,
    )
    op.add_column(
        "users",
        sa.Column("user_type_id", sa.Integer(), nullable=True),
        schema=MAIN_SCHEMA,
    )
    op.add_column(
        "users",
        sa.Column("first_name", sa.String(50), nullable=True),
        schema=MAIN_SCHEMA,
    )
    op.add_column(
        "users",
        sa.Column("last_name", sa.String(100), nullable=True),
        schema=MAIN_SCHEMA,
    )
    op.add_column(
        "users",
        sa.Column("timezone", sa.String(64), nullable=True),
        schema=MAIN_SCHEMA,
    )
