from flask import Flask
from medex.services.database import get_db_session
from medex.services.session import SessionService
from apscheduler.schedulers.background import BackgroundScheduler
import tzlocal


def expire_old_sessions(app: Flask):
    with app.app_context():
        SessionService.expire_old_sessions(get_db_session())


class Scheduler:
    def __init__(self, app: Flask):
        self._background_scheduler = BackgroundScheduler(timezone=str(tzlocal.get_localzone()))
        self._background_scheduler.add_job(expire_old_sessions, 'interval', [app], minutes=30)

    def start(self):
        self._background_scheduler.start()

    def stop(self):
        print('exit scheduler')
        self._background_scheduler.shutdown()
