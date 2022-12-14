import os
from flask import session

from medex.dto.filter import FilterStatus
from medex.services.database import get_db_session
from medex.services.filter import FilterService
from medex.services.session import SessionService


_default_measurement = None


def init_controller_helper(default_measurement):
    global _default_measurement
    _default_measurement = default_measurement


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
        filter_status = FilterStatus(filters={}, measurement=_default_measurement)
    return FilterService(
        database_session=database_session,
        filter_status=filter_status,
        session_service=session_service
    )


def store_filter_status_in_session(filter_service: FilterService):
    session['filter_status'] = filter_service.dict()
