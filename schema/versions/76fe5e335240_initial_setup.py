"""Initial Setup

Revision ID: 76fe5e335240
Revises: 
Create Date: 2022-11-03 14:58:19.326929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76fe5e335240'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'header',
        sa.Column('name_id', sa.String, primary_key=True),
        sa.Column('measurement', sa.String)
    )

    op.create_table(
        'patient',
        sa.Column('name_id', sa.String, primary_key=True),
        sa.Column('case_id', sa.String, primary_key=True)
    )
    op.create_index('idx_name_id_patient',  'patient', ['name_id'])
    op.create_index('idx_case_id_patient', 'patient', ['case_id'])

    op.create_table(
        'name_type',
        sa.Column('orders', sa.Integer),
        sa.Column('key', sa.String, primary_key=True),
        sa.Column('type', sa.String),
        sa.Column('synonym', sa.String),
        sa.Column('description', sa.String),
        sa.Column('unit', sa.String),
        sa.Column('show', sa.String),
    )

    op.create_table(
        'examination_numerical',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name_id', sa.String),
        sa.Column('case_id', sa.String),
        sa.Column('measurement', sa.String),
        sa.Column('date', sa.String),
        sa.Column('time', sa.String),
        sa.Column('key', sa.String, sa.ForeignKey('name_type.key')),
        sa.Column('value', sa.Numeric),
    )
    op.create_index('idx_key_num', 'examination_numerical', ['key'])
    op.create_index('idx_name_id_num', 'examination_numerical', ['name_id'])

    op.create_table(
        'examination_categorical',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name_id', sa.String),
        sa.Column('case_id', sa.String),
        sa.Column('measurement', sa.String),
        sa.Column('date', sa.String),
        sa.Column('time', sa.String),
        sa.Column('key', sa.String, sa.ForeignKey('name_type.key')),
        sa.Column('value', sa.String),
    )
    op.create_index('idx_key_cat', 'examination_categorical', ['key'])
    op.create_index('idx_name_id_cat', 'examination_categorical', ['name_id'])

    op.create_table(
        'examination_date',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name_id', sa.String),
        sa.Column('case_id', sa.String),
        sa.Column('measurement', sa.String),
        sa.Column('date', sa.String),
        sa.Column('time', sa.String),
        sa.Column('key', sa.String, sa.ForeignKey('name_type.key')),
        sa.Column('value', sa.Date),
    )
    op.create_index('idx_key_date', 'examination_date', ['key'])
    op.create_index('idx_name_id_date', 'examination_date', ['name_id'])


def downgrade() -> None:
    for name in [
        'header', 'patient', 'name_type', 'examination_numerical',
        'examination_categorical', 'examination_date'
    ]:
        op.drop_table(name)
    for name in [
        'idx_name_id_patient', 'idx_case_id_patient',
        'idx_key_num', 'idx_name_id_num',
        'idx_key_cat', 'idx_name_id_cat',
        'idx_key_date', 'idx_name_id_date',
    ]:
        op.drop_index(name)
