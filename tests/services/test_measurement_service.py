from medex.database_schema import TableCategorical, TableNumerical, Header
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
from medex.services.measurement import MeasurementService


def test_measurement_simple(db_session):
    db_session.add_all([
        Header(name_id='Name ID', measurement='Measurement'),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='0', date='2021-05-15', key='diabetes', value='nein'
        ),
    ])

    info = MeasurementService(db_session=db_session).get_info()

    assert info.display_name == 'Measurement'
    assert info.values == ['0']


def test_measurement_numerical(db_session):
    db_session.add_all([
        Header(name_id='Name ID', measurement='Visit'),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='blood pressure', value=129
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='blood pressure', value=138
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='blood pressure', value=135
        )
    ])

    info = MeasurementService(db_session=db_session).get_info()

    assert info.display_name == 'Visit'
    assert info.values == ['baseline', 'follow up1']


def test_measurement_complex(db_session):
    db_session.add_all([
        Header(name_id='Name ID', measurement='Visit'),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='follow up1', date='2022-05-15', key='diabetes', value='nein'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2022-05-15', key='diabetes', value='ja'
        ),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='blood pressure', value=129
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='blood pressure', value=138
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='blood pressure', value=135
        )
    ])

    info = MeasurementService(db_session=db_session).get_info()

    assert info.display_name == 'Visit'
    assert info.values == ['baseline', 'follow up1']
