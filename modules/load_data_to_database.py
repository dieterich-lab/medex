from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from medex.services.database import get_db_session
from modules.models import TableNumerical, TableCategorical, TableDate, Patient, Header, NameType
from sqlalchemy.sql import union, select, insert
import pandas as pd


def load_header(header):
    db_session = get_db_session()
    db_session.execute(
        insert(Header).values(name_id=header[0], measurement=header[2])
    )
    db_session.commit()


def load_entities(entities):
    db_session = get_db_session()
    stmt = insert(NameType)
    with open(entities, 'r', encoding="utf8") as in_file:
        head = next(in_file)
        add_index_flag = 'order' not in head
        line_number = 1
        for row in in_file:
            params = _get_entity_dict_from_row(row, add_index_flag, line_number)
            line_number += 1
            try:
                db_session.execute(stmt, params)
            except SQLAlchemyError as e:
                print(f"Warning: Failed to load entities.csv, line {line_number} - skipping: {str(e)}")
    db_session.commit()
    in_file.close()
    df = pd.read_csv(entities)
    numerical_entities, date_entities = df[df['type'] == 'Double']['key'], df[df['type'] == 'Date']['key']
    numerical_entities, date_entities = numerical_entities.to_list(), date_entities.to_list()

    return numerical_entities, date_entities


def _get_columns_of_table(table):
    return [column.key for column in table.__table__.columns]


_ENTITY_COLUMN_LIST = _get_columns_of_table(NameType)


def _get_entity_dict_from_row(row, add_index_flag, index):
    items = [x.strip() for x in row.split(',')]
    if add_index_flag:
        items.insert(0, str(index))
    items = items + [''] * (7 - len(items))
    return {
        _ENTITY_COLUMN_LIST[i]: items[i]
        for i in range(7)
    }


def load_data(entities_path, dataset_path, header):
    """
    Load data from entities.csv, data.csv,header.csv files into examination table in Postgresql
    """
    # load data from header.csv file to header table
    numerical_entities, date_entities = load_entities(entities_path)
    load_dataset(dataset_path, header, numerical_entities, date_entities)


class ImportValidationError(Exception):
    pass


def load_dataset(dataset, header, numerical_entities, date_entities):
    db_session = get_db_session()
    with open(dataset, 'r', encoding="utf8") as in_file:
        line_number = 0
        add_visit_flag = 'Visit' not in header
        for row in in_file:
            line_number += 1
            entity, items = _get_data_from_row(row, line_number, add_visit_flag)
            if entity is None:
                continue
            meta_data = _get_meta_data_for_entity(entity, numerical_entities, date_entities)
            _do_insert(db_session, meta_data, items, line_number)
    db_session.commit()


def _get_data_from_row(row, line_number, add_visit_flag):
    items = [x.strip() for x in row.split(',')]
    items.insert(0, str(line_number))
    if add_visit_flag:
        items.insert(2, '1')
    if len(items) > 8:
        items[7] = ';'.join(items[7:])
        items = items[:8]
    if len(items) < 8:
        print(f"dataset.csv, line {line_number}: Too few fields - skipping!")
        return None, None
    items[6] = items[6].replace("  ", " ")
    return items[6], items


def _validate_numerical(x):
    try:
        float(x)
    except ValueError:
        raise ImportValidationError(f"Value '{x} is not numerical!")


def _validate_date(x):
    try:
        datetime.strptime(x, '%Y-%m-%d')   # Is that good enough?
    except Exception:
        raise ImportValidationError(f"Value '{x} is not a Date in format YYYY-MM-DD!")


def _validate_categorical(x):
    pass


_META_DATA_BY_ENITITY_TYPE = {
    'categorical': {
        'columns': _get_columns_of_table(TableCategorical),
        'statement': insert(TableCategorical),
        'validator': _validate_categorical,
    },
    'numerical': {
        'columns': _get_columns_of_table(TableNumerical),
        'statement': insert(TableNumerical),
        'validator': _validate_numerical,
    },
    'date': {
        'columns': _get_columns_of_table(TableDate),
        'statement': insert(TableDate),
        'validator': _validate_date,
    }
}


def _get_meta_data_for_entity(entity, numerical_entities, date_entities):
    if entity in numerical_entities:
        entity_type = 'numerical'
    elif entity in date_entities:
        entity_type = 'date'
    else:
        entity_type = 'categorical'
    return _META_DATA_BY_ENITITY_TYPE[entity_type]


def _do_insert(db_session, meta_data, items, line_number):
    validator = meta_data['validator']
    try:
        validator(items[7])
    except ImportValidationError as e:
        print(f"Warning: Failed to load dataset.csv, line {line_number} - skipping: {str(e)}")
        return

    columns = meta_data['columns']
    statement = meta_data['statement']
    params = {columns[i]: items[i] for i in range(8)}
    db_session.execute(statement , params)


def patient_table():
    s_union = union(select(TableCategorical.name_id, TableCategorical.case_id),
                    select(TableNumerical.name_id, TableNumerical.case_id),
                    select(TableDate.name_id, TableDate.case_id)).subquery()
    s_select = select(s_union.c.name_id, s_union.c.case_id).group_by(s_union.c.name_id, s_union.c.case_id)
    sql_statement = insert(Patient).from_select(['name_id', 'case_id'], s_select)
    db_session = get_db_session()
    db_session.execute(sql_statement)
    db_session.commit()
