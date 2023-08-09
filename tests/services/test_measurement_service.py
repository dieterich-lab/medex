from datetime import datetime

from medex.database_schema import CategoricalValueTable, NumericalValueTable, HeaderTable
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
from medex.services.measurement import MeasurementService


def test_measurement_simple(db_session):
    db_session.add_all([
        HeaderTable(patient_id='Name ID', measurement='Measurement'),
        CategoricalValueTable(
            patient_id='p1', case_id='c1', measurement='0', date_time=datetime(2021, 5, 15),
            key='diabetes', value='nein'
        ),
    ])

    info = MeasurementService(db_session=db_session).get_info()

    assert info.display_name == 'Measurement'
    assert info.values == ['0']


def test_measurement_numerical(db_session):
    db_session.add_all([
        HeaderTable(patient_id='Name ID', measurement='Visit'),
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=129
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=138
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='blood pressure', value=135
        )
    ])

    info = MeasurementService(db_session=db_session).get_info()

    assert info.display_name == 'Visit'
    assert info.values == ['baseline', 'follow up1']


def test_measurement_complex(db_session):
    db_session.add_all([
        HeaderTable(patient_id='Name ID', measurement='Visit'),
        CategoricalValueTable(
            patient_id='p1', case_id='c1', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='diabetes', value='nein'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2022, 5, 15),
            key='diabetes', value='ja'
        ),
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=129
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=138
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='blood pressure', value=135
        )
    ])

    info = MeasurementService(db_session=db_session).get_info()

    assert info.display_name == 'Visit'
    assert info.values == ['baseline', 'follow up1']
