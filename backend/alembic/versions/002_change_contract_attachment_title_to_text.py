"""change contract attachment title to text

Revision ID: 002_change_title_to_text
Revises: 001_extended_fields
Create Date: 2025-09-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_change_title_to_text'
down_revision = '001_extended_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Change the title column in contract_attachments from String to Text
    op.alter_column('contract_attachments', 'title', type_=sa.Text(), existing_type=sa.String())


def downgrade():
    # Change the title column in contract_attachments from Text back to String
    op.alter_column('contract_attachments', 'title', type_=sa.String(), existing_type=sa.Text())