import os
from flask import session

from medex.dto.filter import FilterStatus
from medex.services.barchart import BarChartService
from medex.services.basic_stats import BasicStatisticsService
from medex.services.boxplot import BoxplotService
from medex.services.data import DataService
from medex.services.database import get_db_session
from medex.services.heatmap import HeatmapService
from medex.services.histogram import HistogramService
from medex.services.measurement import MeasurementService
from medex.services.scatter_plot import ScatterPlotService
from medex.services.session import SessionService
from medex.services.filter import FilterService
from medex.services.entity import EntityService


def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = os.urandom(10).hex()
    return session['session_id']


def get_filter_service():
    database_session = get_db_session()
    session_service = SessionService(
        database_session=database_session,
        session_id=get_session_id()
    )
    if 'filter_status' in session:
        filter_status = FilterStatus.parse_obj(session['filter_status'])
    else:
        filter_status = FilterStatus(filters={})
    return FilterService(
        database_session=database_session,
        filter_status=filter_status,
        session_service=session_service
    )


def store_filter_status_in_session(filter_service: FilterService):
    session['filter_status'] = filter_service.dict()


_entity_service = None


def get_entity_service():
    global _entity_service
    if _entity_service is None:
        database_session = get_db_session()
        _entity_service = EntityService(database_session)
    return _entity_service


def get_data_service():
    database_session = get_db_session()
    filter_service = get_filter_service()
    return DataService(database_session, filter_service)


def get_scatter_plot_service():
    database_session = get_db_session()
    filter_service = get_filter_service()
    return ScatterPlotService(database_session, filter_service)


def get_barchart_service():
    database_session = get_db_session()
    filter_service = get_filter_service()
    return BarChartService(database_session, filter_service)


def get_histogram_service():
    database_session = get_db_session()
    filter_service = get_filter_service()
    return HistogramService(database_session, filter_service)


def get_boxplot_service():
    database_session = get_db_session()
    filter_service = get_filter_service()
    histogram_service = get_histogram_service()
    return BoxplotService(database_session, filter_service, histogram_service)


def get_heatmap_service():
    db_session = get_db_session()
    filter_service = get_filter_service()
    return HeatmapService(db_session, filter_service)


def get_basic_stats_service():
    db_session = get_db_session()
    filter_service = get_filter_service()
    return BasicStatisticsService(db_session, filter_service)


_measurement_service = None


def get_measurement_service():
    global _measurement_service
    if _measurement_service is None:  # noqa
        _measurement_service = MeasurementService(db_session=get_db_session())
    return _measurement_service  # noqa
