import pytest
from sqlalchemy import select
from sqlalchemy.orm import Query, InstrumentedAttribute

from modules.models import Patient, NameType, TableCategorical, TableNumerical, SessionNameIdsMatchingFilter
from medex.dto.filter import NumericalFilter, CategoricalFilter
from medex.services.filter import FilterService

# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
# noinspection PyUnresolvedReferences
from tests.fixtures.services import session_service, filter_service, filter_status


@pytest.fixture
def populate_data(db_session):
    db_session.add_all([
        Patient(name_id='p1', case_id='case_p1'),
        Patient(name_id='p2', case_id='case_p2'),

        NameType(orders=1, key='temperature', type='Double'),
        NameType(orders=2, key='diabetes', type='String'),
        NameType(orders=3, key='blood pressure', type='Double'),

        TableCategorical(
            id=1, name_id='p1', case_id='case_p1', measurement='baseline', date='2015-03-05',
            key='diabetes', value='nein'
        ),
        TableCategorical(
            id=2, name_id='p2', case_id='case_p2', measurement='baseline', date='2015-04-05',
            key='diabetes', value='ja'
        ),

        TableNumerical(
            id=3, name_id='p1', case_id='case_p1', measurement='baseline', date='2015-03-05',
            key='temperature', value=37.5
        ),
        TableNumerical(
            id=4, name_id='p2', case_id='case_p2', measurement='baseline', date='2015-04-05',
            key='temperature', value=40.7
        ),
        TableNumerical(
            id=5, name_id='p1', case_id='case_p1', measurement='baseline', date='2015-03-05',
            key='blood pressure', value=135
        ),

        SessionNameIdsMatchingFilter(
            session_id='unrelated-session', name_id='p1', filter='diabetes'
        ),
        SessionNameIdsMatchingFilter(
            session_id='unrelated-session', name_id='p2', filter='temperature'
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
    new_filter = NumericalFilter(from_value=39, to_value=43, min=30, max=43)
    filter_service.add_filter(entity='temperature', new_filter=new_filter)

    numerical_query_raw = select(TableNumerical.name_id, TableNumerical.key, TableNumerical.value)
    numerical_query_cooked = filter_service.apply_filter(TableNumerical, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 1
    assert numerical_result[0].name_id == 'p2'
    assert numerical_result[0].key == 'temperature'
    assert float(numerical_result[0].value) == 40.7

    categorical_query_raw = select(TableCategorical.name_id, TableCategorical.key, TableCategorical.value)
    categorical_query_cooked = filter_service.apply_filter(TableCategorical, categorical_query_raw)
    categorical_result = db_session.execute(categorical_query_cooked).all()
    assert len(categorical_result) == 1
    assert categorical_result[0].name_id == 'p2'
    assert categorical_result[0].key == 'diabetes'
    assert categorical_result[0].value == 'ja'


def test_categorical_filter(filter_service: FilterService, db_session, populate_data):
    new_filter = CategoricalFilter(categories=['nein'])
    filter_service.add_filter(entity='diabetes', new_filter=new_filter)

    numerical_query_raw = select(TableNumerical.name_id, TableNumerical.key, TableNumerical.value)
    numerical_query_cooked = filter_service.apply_filter(TableNumerical, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 2
    for i in [0, 1]:
        assert numerical_result[i].name_id == 'p1'
        assert numerical_result[i].key in ['temperature', 'blood pressure']
        assert float(numerical_result[0].value) in [37.5, 135]

    categorical_query_raw = select(TableCategorical.name_id, TableCategorical.key, TableCategorical.value)
    categorical_query_cooked = filter_service.apply_filter(TableCategorical, categorical_query_raw)
    categorical_result = db_session.execute(categorical_query_cooked).all()
    assert len(categorical_result) == 1
    assert categorical_result[0].name_id == 'p1'
    assert categorical_result[0].key == 'diabetes'
    assert categorical_result[0].value == 'nein'


def test_delete_all_filters(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)

    numerical_query_raw = select(TableNumerical.name_id, TableNumerical.key, TableNumerical.value)
    numerical_query_cooked = filter_service.apply_filter(TableNumerical, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 0

    filter_service.delete_all_filters()

    numerical_query_cooked = filter_service.apply_filter(TableNumerical, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 3


def _setup_filters_filtering_everything(filter_service):
    for entity, new_filter in [
        ('diabetes', CategoricalFilter(categories=['nein'])),
        ('temperature', NumericalFilter(from_value=39, to_value=43))
    ]:
        filter_service.add_filter(entity=entity, new_filter=new_filter)


def test_delete_one_filter(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)

    numerical_query_raw = select(TableNumerical.name_id, TableNumerical.key, TableNumerical.value)
    numerical_query_cooked = filter_service.apply_filter(TableNumerical, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 0

    filter_service.delete_filter('temperature')

    numerical_query_cooked = filter_service.apply_filter(TableNumerical, numerical_query_raw)
    numerical_result = db_session.execute(numerical_query_cooked).all()
    assert len(numerical_result) == 2


def test_dict(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)

    assert filter_service.dict() == {
        'filtered_patient_count': 0,
        'filters': {
            'diabetes': { 'categories': ['nein']},
            'temperature': {'from_value': 39.0, 'to_value': 43.0}
        }
    }


def test_dict_after_deleting_last_filter(filter_service: FilterService, db_session, populate_data):
    _setup_filters_filtering_everything(filter_service)
    filter_service.delete_filter('diabetes')
    filter_service.delete_filter('temperature')
    assert filter_service.dict() == {
        'filtered_patient_count': None,
        'filters': {}
    }
