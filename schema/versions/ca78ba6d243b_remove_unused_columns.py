"""remove unused columns

Revision ID: ca78ba6d243b
Revises: 76e5af8ba950
Create Date: 2023-02-08 12:00:03.549591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca78ba6d243b'
down_revision = '76e5af8ba950'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('name_type', 'orders')


def downgrade() -> None:
    op.add_column('name_type', sa.Column('orders', sa.Integer))
