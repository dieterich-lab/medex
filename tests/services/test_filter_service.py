from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Query, InstrumentedAttribute

from medex.database_schema import PatientTable, EntityTable, CategoricalValueTable, NumericalValueTable, SessionPatientsMatchingFilterTable
from medex.dto.filter import NumericalFilter, CategoricalFilter
from medex.services.filter import FilterService

# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
# noinspection PyUnresolvedReferences
from tests.fixtures.services import session_service, filter_service, filter_status


@pytest.fixture
def populate_data(db_session):
    db_session.add_all([
        PatientTable(patient_id='p1', case_id='case_p1'),
        PatientTable(patient_id='p2', case_id='case_p2'),

        EntityTable(key='temperature', type='Double'),
        EntityTable(key='diabetes', type='String'),
        EntityTable(key='blood pressure', type='Double'),

        CategoricalValueTable(
            id=1, patient_id='p1', case_id='case_p1', measurement='baseline', date_time=datetime(2015, 3, 5),
            key='diabetes', value='nein'
        ),
        CategoricalValueTable(
            id=2, patient_id='p2', case_id='case_p2', measurement='baseline', date_time=datetime(2015, 4, 5),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            id=7, patient_id='p2', case_id='case_p2', measurement='follow up1', date_time=datetime(2016, 4, 5),
            key='diabetes', value='ja'
        ),

        NumericalValueTable(
            id=3, patient_id='p1', case_id='case_p1', measurement='baseline', date_time=datetime(2015, 3, 5),
            key='temperature', value=37.5
        ),
        NumericalValueTable(
            id=4, patient_id='p2', case_id='case_p2', measurement='baseline', date_time=datetime(2015, 4, 5),
            key='temperature', value=40.7
        ),
        NumericalValueTable(
            id=5, patient_id='p1', case_id='case_p1', measurement='baseline', date_time=datetime(2015, 3, 5),
            key='blood pressure', value=135
        ),
        NumericalValueTable(
            id=6, patient_id='p1', case_id='case_p1', measurement='follow up1', date_time=datetime(2016, 3, 6),
            key='blood pressure', value=138
        ),

        SessionPatientsMatchingFilterTable(
            session_id='unrelated-session', patient_id='p1', filter='diabetes'
        ),
        SessionPatientsMatchingFilterTable(
            session_id='unrelated-session', patient_id='p2', filter='temperature'
        ),
    ])
    db_session.commit()


def get_result_set_as_dict(query: Query):
    columns = []
    for item in query.column_descriptions:
        for name, value in item['entity'].__dict__.items():
            if isinstance(value, InstrumentedAttribute):
                columns.append(name)
    result_set = query.all()
    return [
        {col: row.__dict__[col] for col in columns}
        for row in result_set
    ]


def test_numerical_filter(filter_service: FilterService, db_session, populate_data):
    new_filter = NumericalFilter(measurement='baseline', from_value=39, to_value=43, min=30, max=43)
    filter_service.add_filter(entity='temperature', new_filter=new_filter)

    numerical_query_raw = select(NumericalValueTable.patient_id, NumericalValueTable.key, NumericalValueTable.value)
    numerical_query_cooked = filter_service.apply_filter(NumericalValueTable, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 1
    assert numerical_result[0].patient_id == 'p2'
    assert numerical_result[0].key == 'temperature'
    assert float(numerical_result[0].value) == 40.7

    categorical_query_raw = select(
        CategoricalValueTable.patient_id, CategoricalValueTable.key, CategoricalValueTable.value, CategoricalValueTable.measurement
    )
    categorical_query_cooked = (
        filter_service.apply_filter(CategoricalValueTable, categorical_query_raw)
        .order_by(CategoricalValueTable.date_time)
    )
    categorical_result = db_session.execute(categorical_query_cooked).all()
    assert len(categorical_result) == 2
    measurements = ['baseline', 'follow up1']
    for i in range(2):
        assert categorical_result[i].patient_id == 'p2'
        assert categorical_result[i].key == 'diabetes'
        assert categorical_result[i].value == 'ja'
        assert categorical_result[i].measurement == measurements[i]


def test_categorical_filter(filter_service: FilterService, db_session, populate_data):
    new_filter = CategoricalFilter(measurement='baseline', categories=['nein'])
    filter_service.add_filter(entity='diabetes', new_filter=new_filter)

    numerical_query_raw = select(NumericalValueTable.patient_id, NumericalValueTable.key, NumericalValueTable.value)
    numerical_query_cooked = filter_service.apply_filter(NumericalValueTable, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 3
    for i in [0, 1, 2]:
        assert numerical_result[i].patient_id == 'p1'
        assert numerical_result[i].key in ['temperature', 'blood pressure']
        assert float(numerical_result[0].value) in [37.5, 135, 138]

    categorical_query_raw = select(CategoricalValueTable.patient_id, CategoricalValueTable.key, CategoricalValueTable.value)
    categorical_query_cooked = filter_service.apply_filter(CategoricalValueTable, categorical_query_raw)
    categorical_result = db_session.execute(categorical_query_cooked).all()
    assert len(categorical_result) == 1
    assert categorical_result[0].patient_id == 'p1'
    assert categorical_result[0].key == 'diabetes'
    assert categorical_result[0].value == 'nein'


def test_delete_all_filters(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)

    numerical_query_raw = select(NumericalValueTable.patient_id, NumericalValueTable.key, NumericalValueTable.value)
    numerical_query_cooked = filter_service.apply_filter(NumericalValueTable, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 0

    filter_service.delete_all_filters()

    numerical_query_cooked = filter_service.apply_filter(NumericalValueTable, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 4


def _setup_filters_filtering_everything(filter_service):
    for entity, new_filter in [
        ('diabetes', CategoricalFilter(measurement='baseline', categories=['nein'])),
        ('temperature', NumericalFilter(measurement='baseline', from_value=39, to_value=43))
    ]:
        filter_service.add_filter(entity=entity, new_filter=new_filter)


def test_delete_one_filter(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)

    numerical_query_raw = select(NumericalValueTable.patient_id, NumericalValueTable.key, NumericalValueTable.value)
    numerical_query_cooked = filter_service.apply_filter(NumericalValueTable, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 0

    filter_service.delete_filter('temperature')

    numerical_query_cooked = filter_service.apply_filter(NumericalValueTable, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 3


def test_dict(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)

    assert filter_service.dict() == {
        'filtered_patient_count': 0,
        'filters': {
            'diabetes': {'measurement': 'baseline', 'categories': ['nein']},
            'temperature': {'measurement': 'baseline', 'from_value': 39.0, 'to_value': 43.0}
        }
    }


def test_dict_after_deleting_last_filter(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)
    filter_service.delete_filter('diabetes')
    filter_service.delete_filter('temperature')
    assert filter_service.dict() == {
        'filtered_patient_count': None,
        'filters': {},
    }
