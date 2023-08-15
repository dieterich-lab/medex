"""add_indices_for_value_tables

Revision ID: a6728cb21f33
Revises: 629d6f63b58f
Create Date: 2023-08-15 16:59:26.054273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6728cb21f33'
down_revision = '629d6f63b58f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ['numerical_value', 'categorical_value', 'date_value']:
        op.create_index(
            f"idx_{table}_patient_id_measurement_key",  table,
            ['patient_id', 'measurement', 'key']
        )


def downgrade() -> None:
    for table in ['numerical_value', 'categorical_value', 'date_value']:
        op.drop_index(f"idx_{table}_patient_id_measurement_key")
