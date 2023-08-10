"""database_refactoring

Revision ID: 629d6f63b58f
Revises: ca78ba6d243b
Create Date: 2023-08-09 14:16:31.007682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '629d6f63b58f'
down_revision = 'ca78ba6d243b'
branch_labels = None
depends_on = None

TABLE_NAME_MAP = [
    ('name_type', 'entity'),
    ('examination_numerical', 'numerical_value'),
    ('examination_categorical', 'categorical_value'),
    ('examination_date', 'date_value'),
    ('sessions', 'session'),
    ('session_filtered_name_ids', 'session_filtered_patient'),
    ('session_filtered_case_ids', 'session_filtered_case_id'),
    ('session_name_ids_matching_filter', 'session_patients_matching_filter'),
]

TABLES_WITH_NAME_ID = [
    'header',
    'patient',
    'numerical_value',
    'categorical_value',
    'date_value',
    'session_filtered_patient',
    'session_patients_matching_filter',
]

INDEX_NAME_MAP = [
    ('idx_name_id_patient', 'idx_patient_id'),
    ('idx_name_id_num', 'idx_patient_id_num'),
    ('idx_name_id_cat', 'idx_patient_id_cat'),
    ('idx_name_id_date', 'idx_patient_id_date'),
    ('idx_session_filtered_name_ids_by_session_id', 'idx_session_filtered_patient_ids_by_session_id'),
    ('idx_session_name_ids_matching_filter_by_session_id', 'idx_session_patient_ids_matching_filter_by_session_id'),
]

TABLES_WITH_DATE_TIME = [
    'numerical_value',
    'categorical_value',
    'date_value',
]

SEQUENCE_NAME_MAP = [
    ('examination_categorical_id_seq', 'categorical_value_id_seq'),
    ('examination_numerical_id_seq', 'numerical_value_id_seq'),
    ('examination_date_id_seq', 'date_value_id_seq'),
]


def upgrade() -> None:
    for old_name, new_name in TABLE_NAME_MAP:
        op.rename_table(old_name, new_name)

    for table in TABLES_WITH_NAME_ID:
        op.alter_column(table, column_name='name_id', new_column_name='patient_id')

    for old_name, new_name in INDEX_NAME_MAP:
        op.execute(f"ALTER INDEX {old_name} RENAME TO {new_name}")

    for old_name, new_name in SEQUENCE_NAME_MAP:
        op.execute(f"ALTER SEQUENCE {old_name} RENAME TO {new_name}")

    op.drop_column('entity', 'show')
    for table in TABLES_WITH_DATE_TIME:
        op.add_column(table, sa.Column('date_time', sa.DateTime))
        op.execute(f"""UPDATE {table}
            SET date_time = CASE 
                        WHEN date = NULL THEN NULL
                        WHEN time = NULL THEN TO_TIMESTAMP('YYYY-MM-DD', date)
                        ELSE TO_TIMESTAMP('YYYY-MM-DD HH24:MI:SS', date || ' ' || time)
                    END
        """)
        op.drop_column(table, 'date')
        op.drop_column(table, 'time')


def downgrade() -> None:
    for table in TABLES_WITH_DATE_TIME:
        op.add_column(table, sa.Column('date', sa.String))
        op.add_column(table, sa.Column('time', sa.String))
        op.execute(f"""UPDATE {table}
            SET date = CASE 
                    WHEN date_time = NULL THEN NULL
                    ELSE TO_CHAR(date_time, 'YYYY-MM-DD')
                END,
                time = CASE
                    WHEN date_time = NULL THEN NULL
                    ELSE TO_CHAR(date_time, 'HH24:MI:SS')
                END
        """)
        op.drop_column(table, 'date_time')
    op.add_column('entity', sa.Column('show', sa.String))

    for old_name, new_name in SEQUENCE_NAME_MAP:
        op.execute(f"ALTER SEQUENCE {new_name} RENAME TO {old_name}")

    for old_name, new_name in INDEX_NAME_MAP:
        op.execute(f"ALTER INDEX {new_name} RENAME TO {old_name}")

    for table in TABLES_WITH_NAME_ID:
        op.alter_column(table, column_name='patient_id', new_column_name='name_id')

    for old_name, new_name in TABLE_NAME_MAP:
        op.rename_table(new_name, old_name)
