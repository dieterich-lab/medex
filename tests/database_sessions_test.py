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
    mocker.patch('modules.database_sessions._cleanup', return_value=True)


@fixture
def sleepless(monkeypatch):
    def sleep(seconds):
        pass
    monkeypatch.setattr(time, 'sleep', sleep)


def test_session_create(session):
    factory = DatabaseSessionFactory(None)
    assert factory.get_session('a') == 'XXX_1'
    assert factory.get_session('b') == 'XXX_2'
    assert factory.get_session('a') == 'XXX_1'
    print(factory.sessions_by_id)


def test_cleanup(sleepless):
    factory = DatabaseSessionFactory(None)
    print(factory.sessions_by_id)

