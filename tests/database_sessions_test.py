from pytest import fixture
from modules.database_sessions import DatabaseSessionFactory
from unittest.mock import patch
import time
from unittest import mock


_session_count = 0


@fixture
def session(mocker):
    def our_session(engine):
        global _session_count
        _session_count += 1
        return 'XXX_' + str(_session_count)

    mocker.patch('modules.database_sessions.Session', our_session)


def test_session_create(session):
    factory = DatabaseSessionFactory(None)
    assert factory.get_session('a') == 'XXX_1'
    assert factory.get_session('b') == 'XXX_2'
    assert factory.get_session('a') == 'XXX_1'
    with patch('time.sleep', return_value=None) as patched_time_sleep:
        print(factory.sessions_by_id)



