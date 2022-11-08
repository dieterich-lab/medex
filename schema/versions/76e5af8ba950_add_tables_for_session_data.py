"""Add tables for session data

Revision ID: 76e5af8ba950
Revises: 76fe5e335240
Create Date: 2022-11-03 15:58:20.363320

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76e5af8ba950'
down_revision = '76fe5e335240'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'sessions',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('created', sa.DateTime),
        sa.Column('last_touched', sa.DateTime),
    )
    op.create_table(
        'session_filtered_name_ids',
        sa.Column('session_id', sa.String, sa.ForeignKey('sessions.id'), primary_key=True),
        sa.Column('name_id', sa.String, primary_key=True),
    )
    op.create_index(
        'idx_session_filtered_name_ids_by_session_id',
        'session_filtered_name_ids',
        ['session_id']
    )

    op.create_table(
        'session_name_ids_matching_filter',
        sa.Column('session_id', sa.String, sa.ForeignKey('sessions.id'), primary_key=True),
        sa.Column('name_id', sa.String, primary_key=True),
        sa.Column('filter', sa.String),
    )
    op.create_index(
        'idx_session_name_ids_matching_filter_by_session_id',
        'session_name_ids_matching_filter',
        ['session_id']
    )

    op.create_table(
        'session_filtered_case_ids',
        sa.Column('session_id', sa.String, sa.ForeignKey('sessions.id'), primary_key=True),
        sa.Column('case_id', sa.String, primary_key=True),
    )
    op.create_index(
        'idx_session_filtered_case_ids_by_session_id',
        'session_filtered_case_ids',
        ['session_id']
    )


def downgrade() -> None:
    op.drop_table('session_filtered_name_ids')
    op.drop_table('session_name_ids_matching_filter')
    op.drop_table('session_filtered_case_ids')
    op.drop_table('sessions')
