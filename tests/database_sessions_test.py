from pytest import fixture
from freezegun import freeze_time

_session_count = 0


@fixture
def session(mocker):
    def our_session(engine):
        global _session_count
        _session_count += 1
        return 'XXX_' + str(_session_count)

    mocker.patch('modules.database_sessions.Session', our_session)
    global _session_count
    _session_count = 0


def test_session_create(session):
    factory = DatabaseSessionFactory(None)
    assert factory.get_session('a') == 'XXX_1'
    assert factory.get_session('b') == 'XXX_2'
    assert factory.get_session('a') == 'XXX_1'
    print(factory.sessions_by_id)
    assert factory.get_session('a') == 'XXX_1'
    print(factory.sessions_by_id)


def test_session_no_cleanup(session):
    factory = DatabaseSessionFactory(None)
    with freeze_time("1990-10-12 15:00:00"):
        assert factory.get_session('a') == 'XXX_1'
    with freeze_time("1990-10-12 15:29:00"):
        assert factory.get_session('b') == 'XXX_2'
        assert factory.get_session('a') == 'XXX_1'


def test_session_cleanup(session):
    factory = DatabaseSessionFactory(None)
    with freeze_time("1990-10-12 15:00:00"):
        assert factory.get_session('a') == 'XXX_1'
    with freeze_time("1990-10-12 15:31:00"):
        assert factory.get_session('b') == 'XXX_2'
        assert factory.get_session('a') == 'XXX_3'
