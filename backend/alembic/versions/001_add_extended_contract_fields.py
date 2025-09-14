"""Add extended contract fields and new models

Revision ID: 001_extended_fields
Revises: 
Create Date: 2024-09-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_extended_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем новые поля к таблице parties
    op.add_column('parties', sa.Column('ogrn', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('okpo', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('okved', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('bank_name', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('bank_account', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('correspondent_account', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('bik', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('director_name', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('director_position', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('acting_basis', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('email', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('legal_address', sa.String(), nullable=True))
    op.add_column('parties', sa.Column('postal_address', sa.String(), nullable=True))
    
    # Добавляем новые поля к таблице contracts
    op.add_column('contracts', sa.Column('contract_type', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('place_of_conclusion', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('work_object_name', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('work_object_address', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('cadastral_number', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('land_area', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('construction_permit', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('permit_date', sa.Date(), nullable=True))
    op.add_column('contracts', sa.Column('amount_including_vat', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('vat_amount', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('vat_rate', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('retention_percentage', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('payment_terms_days', sa.Integer(), nullable=True))
    op.add_column('contracts', sa.Column('work_start_date', sa.Date(), nullable=True))
    op.add_column('contracts', sa.Column('work_completion_date', sa.Date(), nullable=True))
    op.add_column('contracts', sa.Column('warranty_period_months', sa.Integer(), nullable=True))
    op.add_column('contracts', sa.Column('warranty_start_basis', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('delay_penalty_first_week', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('delay_penalty_after_week', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('late_payment_penalty', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('document_penalty_amount', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('site_violation_penalty', sa.Numeric(), nullable=True))
    op.add_column('contracts', sa.Column('project_documentation', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('status', sa.String(), nullable=True, default='active'))
    op.add_column('contracts', sa.Column('currency', sa.String(), nullable=True, default='RUB'))
    op.add_column('contracts', sa.Column('force_majeure_clause', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('dispute_resolution', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('governing_law', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('contracts', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('contracts', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    
    # Создаем FK constraint для created_by_user_id
    op.create_foreign_key('fk_contracts_created_by_user', 'contracts', 'users', ['created_by_user_id'], ['id'])
    
    # Создаем новые таблицы
    op.create_table('contract_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('attachment_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('number', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('is_integral_part', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('contract_penalties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('penalty_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('penalty_rate', sa.Numeric(), nullable=True),
        sa.Column('penalty_amount', sa.Numeric(), nullable=True),
        sa.Column('period_days', sa.Integer(), nullable=True),
        sa.Column('calculation_basis', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('contract_milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('milestone_name', sa.String(), nullable=False),
        sa.Column('planned_start_date', sa.Date(), nullable=True),
        sa.Column('planned_end_date', sa.Date(), nullable=True),
        sa.Column('actual_start_date', sa.Date(), nullable=True),
        sa.Column('actual_end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='planned'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('milestone_amount', sa.Numeric(), nullable=True),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('contact_persons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('party_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('position', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.ForeignKeyConstraint(['party_id'], ['parties.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Удаляем новые таблицы
    op.drop_table('contact_persons')
    op.drop_table('contract_milestones')
    op.drop_table('contract_penalties')
    op.drop_table('contract_attachments')
    
    # Удаляем FK constraint
    op.drop_constraint('fk_contracts_created_by_user', 'contracts', type_='foreignkey')
    
    # Удаляем новые поля из contracts
    op.drop_column('contracts', 'created_by_user_id')
    op.drop_column('contracts', 'updated_at')
    op.drop_column('contracts', 'created_at')
    op.drop_column('contracts', 'governing_law')
    op.drop_column('contracts', 'dispute_resolution')
    op.drop_column('contracts', 'force_majeure_clause')
    op.drop_column('contracts', 'currency')
    op.drop_column('contracts', 'status')
    op.drop_column('contracts', 'project_documentation')
    op.drop_column('contracts', 'site_violation_penalty')
    op.drop_column('contracts', 'document_penalty_amount')
    op.drop_column('contracts', 'late_payment_penalty')
    op.drop_column('contracts', 'delay_penalty_after_week')
    op.drop_column('contracts', 'delay_penalty_first_week')
    op.drop_column('contracts', 'warranty_start_basis')
    op.drop_column('contracts', 'warranty_period_months')
    op.drop_column('contracts', 'work_completion_date')
    op.drop_column('contracts', 'work_start_date')
    op.drop_column('contracts', 'payment_terms_days')
    op.drop_column('contracts', 'retention_percentage')
    op.drop_column('contracts', 'vat_rate')
    op.drop_column('contracts', 'vat_amount')
    op.drop_column('contracts', 'amount_including_vat')
    op.drop_column('contracts', 'permit_date')
    op.drop_column('contracts', 'construction_permit')
    op.drop_column('contracts', 'land_area')
    op.drop_column('contracts', 'cadastral_number')
    op.drop_column('contracts', 'work_object_address')
    op.drop_column('contracts', 'work_object_name')
    op.drop_column('contracts', 'place_of_conclusion')
    op.drop_column('contracts', 'contract_type')
    
    # Удаляем новые поля из parties
    op.drop_column('parties', 'postal_address')
    op.drop_column('parties', 'legal_address')
    op.drop_column('parties', 'email')
    op.drop_column('parties', 'phone')
    op.drop_column('parties', 'acting_basis')
    op.drop_column('parties', 'director_position')
    op.drop_column('parties', 'director_name')
    op.drop_column('parties', 'bik')
    op.drop_column('parties', 'correspondent_account')
    op.drop_column('parties', 'bank_account')
    op.drop_column('parties', 'bank_name')
    op.drop_column('parties', 'okved')
    op.drop_column('parties', 'okpo')
    op.drop_column('parties', 'ogrn')