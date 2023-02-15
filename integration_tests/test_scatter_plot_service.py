import pytest
from medex.dto.scatter_plot import DateRange, GroupByCategoricalEntity, ScaleScatterPlot, ScatterPlotDataRequest
from medex.services.scatter_plot import ScatterPlotService
from modules.models import TableCategorical, TableNumerical, NameType
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session


@pytest.fixture
def setup_scatter_plot_data(db_session):
    db_session.add_all([
        NameType(key='diabetes', type='String'),
        NameType(key='blood_pressure', type='Double'),
        NameType(key='temperature', type='Double'),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='blood_pressure', value=129
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='blood_pressure', value=138
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='blood_pressure', value=135
        ),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-06-20', key='temperature', value=38.5
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-06-23', key='temperature', value=41.3
        ),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='diabetes', value='nein'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='diabetes', value='ja'
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
        date_range=DateRange(from_date='2021-05-15', to_date='2021-06-23'),
        add_group_by=GroupByCategoricalEntity(key='diabetes', categories=['ja', 'nein']))
    figure = service.get_image_svg(scatter_plot_data)
    byte_string = figure.decode('utf-8')
    assert byte_string.find('<svg')
