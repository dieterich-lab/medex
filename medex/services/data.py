from medex.services.session import SessionService


class DataService:
    def __init__(
            self,
            database_session,
            session_service: SessionService
    ):
        self._database_session = database_session
        self._session_service = session_service
        self._session_id = session_service.get_id()
