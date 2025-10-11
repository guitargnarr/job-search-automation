"""Add followup_override_days to Company model

Revision ID: 001_followup_override
Revises:
Create Date: 2025-10-10 16:30:00.000000

V2.3 Refactor: Addressing Complexity-to-Value Ratio
- Adds explicit configuration column for company-specific follow-up timing
- Prioritizes user configuration over automated heuristics
- Reduces reliance on sparse metadata (interview_process, salary)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_followup_override'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add followup_override_days column to companies table"""
    op.add_column(
        'companies',
        sa.Column('followup_override_days', sa.Integer(), nullable=True)
    )


def downgrade():
    """Remove followup_override_days column from companies table"""
    op.drop_column('companies', 'followup_override_days')
