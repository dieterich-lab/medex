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
        'session_filtered_name_ids',
        sa.Column('session_id', sa.String, primary_key=True),
        sa.Column('name_id', sa.String, primary_key=True),
    )
    op.create_index(
        'idx_session_filtered_name_ids_by_session_id',
        'session_filtered_name_ids',
        ['session_id']
    )

    op.create_table(
        'session_filtered_data_keys',
        sa.Column('session_id', sa.String, primary_key=True),
        sa.Column('name_id', sa.String, primary_key=True),
        sa.Column('key', sa.String),
    )
    op.create_index(
        'idx_session_filtered_data_keys_by_session_id',
        'session_filtered_data_keys',
        ['session_id']
    )


def downgrade() -> None:
    op.drop_table('session_filtered_name_ids')
    op.drop_table('session_filtered_data_keys')
