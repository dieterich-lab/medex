import pytest

from medex.dto.filter import FilterStatus
from medex.services.filter import FilterService
from medex.services.session import SessionService


MY_SESSION_ID = 'my_session_id'


class SessionServiceMock(SessionService):
    def __init__(self):  # noqa
        pass

    def touch(self):
        pass

    def get_id(self):
        return MY_SESSION_ID


@pytest.fixture
def session_service():
    yield SessionServiceMock()


@pytest.fixture
def filter_status():
    return FilterStatus(filters=[], measurement='baseline')


@pytest.fixture
def filter_service(db_session, filter_status, session_service):
    yield FilterService(
        database_session=db_session,
        filter_status=filter_status,
        session_service=session_service
    )
