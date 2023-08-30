from datetime import datetime

import pytest
from medex.dto.scatter_plot import GroupByCategoricalEntity, ScaleScatterPlot, ScatterPlotDataRequest
from medex.services.scatter_plot import ScatterPlotService
from medex.database_schema import CategoricalValueTable, NumericalValueTable, EntityTable
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session


@pytest.fixture
def setup_scatter_plot_data(db_session):
    db_session.add_all([
        EntityTable(key='diabetes', type='String'),
        EntityTable(key='blood_pressure', type='Double'),
        EntityTable(key='temperature', type='Double'),
    ])
    db_session.commit()
    db_session.add_all([
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood_pressure', value=129
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood_pressure', value=138
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='blood_pressure', value=135
        ),
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 6, 20),
            key='temperature', value=38.5
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 6, 23),
            key='temperature', value=41.3
        ),
        CategoricalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='diabetes', value='nein'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='diabetes', value='ja'
        ),
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_scatter_plot_service(db_session, filter_service_mock, setup_scatter_plot_data):
    service = ScatterPlotService(
        database_session=db_session,
        filter_service=filter_service_mock
    )
    scatter_plot_data = ScatterPlotDataRequest(
        measurement_x_axis='baseline',
        entity_x_axis='blood_pressure',
        measurement_y_axis='baseline',
        entity_y_axis='temperature',
        scale=ScaleScatterPlot(log_x=True, log_y=False),
        add_group_by=GroupByCategoricalEntity(key='diabetes', categories=['ja', 'nein']))
    figure = service.get_image_svg(scatter_plot_data)
    byte_string = figure.decode('utf-8')
    assert byte_string.find('<svg')
