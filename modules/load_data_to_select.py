import datetime
from sqlalchemy import func, union
from sqlalchemy.sql import select

from medex.services.database import get_db_session
from modules.models import Header, Patient, TableCategorical, TableNumerical, TableDate, NameType


def get_header():
    sql = select(Header.name_id, Header.measurement)
    db = get_db_session()
    rv = db.execute(sql).first()
    return rv.name_id, rv.measurement


def get_database_information():
    db_session = get_db_session()
    query_num = select(func.count(TableNumerical.name_id))
    query_cat = select(func.count(TableCategorical.name_id))
    query_date = select(func.count(TableDate.name_id))
    size_num_tab = db_session.execute(query_num).scalar()
    size_cat_tab = db_session.execute(query_cat).scalar()
    size_date_tab = db_session.execute(query_date).scalar()
    return size_num_tab, size_date_tab, size_cat_tab


def get_date():
    db_session = get_db_session()
    query = select(func.min(TableNumerical.date), func.max(TableNumerical.date))
    results = db_session.execute(query).first()
    start_date = datetime.datetime.strptime(results[0], '%Y-%m-%d').timestamp() * 1000
    end_date = datetime.datetime.strptime(results[1], '%Y-%m-%d').timestamp() * 1000
    return start_date, end_date


def get_number_of_patients():
    db = get_db_session()
    rv = db.execute(
        select(func.count(func.distinct(Patient.name_id)))
    )
    return rv.scalar()


def get_entities():
    db_session = get_db_session()
    query_select = select(NameType.key, NameType.type, NameType.description, NameType.synonym).order_by(NameType.orders)
    results = db_session.execute(query_select).all()
    num_entities = [row.type == 'Double' for row in results]
    cat_entities = [row.type == 'String' for row in results]
    date_entities = [row.type == 'Date' for row in results]
    length = (str(sum(num_entities)), str(sum(cat_entities)), str(sum(date_entities)))
    return length


def get_measurement():
    all_measurements = union(
        select(TableCategorical.measurement.label('measurement'), TableCategorical.date.label('date')),
        select(TableNumerical.measurement.label('measurement'), TableNumerical.date.label('date')),
        select(TableDate.measurement.label('measurement'), TableDate.date.label('date')),
    ).cte('all_measurements')
    first_date = func.min(all_measurements.c.date)
    ordered_list = (
        select(all_measurements.c.measurement, first_date)
        .group_by(all_measurements.c.measurement)
        .order_by(first_date)
    )
    db = get_db_session()
    rv = db.execute(ordered_list).all()
    measurement_list = [getattr(x, 'measurement') for x in rv]
    measurement_display = 'block' if len(rv) > 1 else 'none'
    return measurement_list, measurement_display
