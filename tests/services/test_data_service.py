import pytest

from medex.dto.data import SortOrder, SortItem, SortDirection
from medex.services.data import DataService
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
from tests.mocks.filter_service import FilterServiceMock


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_data_servie_simple(db_session, filter_service_mock):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock
    )
    actual_result = service.get_filtered_data_flat(
        entities=['diabetes'],
        measurements=['baseline'],
    )
    assert actual_result == []

