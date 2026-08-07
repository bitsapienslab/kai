"""add extracted_insights to conversation_events

Revision ID: 0002_add_extracted_insights
Revises: 0001_initial
Create Date: 2026-08-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0002_add_extracted_insights"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "conversation_events",
        sa.Column(
            "extracted_insights",
            sa.JSON(),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("conversation_events", "extracted_insights")
