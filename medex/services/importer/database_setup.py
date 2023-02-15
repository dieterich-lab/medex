from os import stat
from os.path import exists
from subprocess import run

from sqlalchemy import text
from sqlalchemy.orm import Session

from modules.models import Base
from medex.services.config import Config


class DatabaseSchemaUpdateFailed(Exception):
    pass


class DatabaseSetup:
    def __init__(self, db_engine, db_session: Session, config: Config):
        self._db_engine = db_engine
        self._db_session = db_session
        self._config = config
        self._is_import_required = None
        self._db_engine_connection = None

    def do_it(self) -> None:
        self._is_import_required = False
        self._connect_to_db_engine()
        self._check_if_legacy_setup()
        self._check_if_data_files_updated()
        if self._is_import_required:
            self._reset_database()
            self._configure_database()
        self._update_database_schema()

    def _connect_to_db_engine(self):
        self._db_engine_connection = self._db_engine.connect().execution_options(isolation_level="AUTOCOMMIT")

    def _check_if_legacy_setup(self):
        if not self._db_engine_connection.dialect.has_table(self._db_engine_connection, 'alembic_version'):
            print('Database is legacy (no table alembic_version) - forcing data import.')
            self._is_import_required = True

    def _check_if_data_files_updated(self):
        config = self._config
        import_marker_path = config.import_marker_path
        if not exists(import_marker_path):
            print(f"File '{import_marker_path}' does not exist - forcing data import.")
            self._is_import_required = True
            return
        marker_mtime = stat(import_marker_path).st_mtime
        for path in [
            config.header_path,
            config.entities_path,
            config.dataset_path,
         ]:
            if exists(path) and stat(path).st_mtime >= marker_mtime:
                print(f"File '{path}' was modified after last import - forcing data import.")
                self._is_import_required = True

    def _reset_database(self):
        print('Resetting database - dropping all tables ...')
        Base.metadata.drop_all(self._db_engine)

    def _configure_database(self):
        for command in [
            "ALTER SYSTEM SET work_mem='2GB'",
            "ALTER SYSTEM SET max_parallel_workers_per_gather=7",
        ]:
            self._db_engine_connection.execute(text(command))

    def _update_database_schema(self):
        cmd = ['alembic', 'upgrade', 'head']
        cmd_str = ' '.join(cmd)
        print('Ensure that database schema is up-to date:')
        print(f"Running {cmd_str} ...")
        process = run(cmd, cwd=self._config.base_directory)
        return_status = process.returncode
        if return_status != 0:
            raise DatabaseSchemaUpdateFailed(f"The command '{cmd_str}' exited with status {return_status}")
        print('Database schema is up-to-date now.')

    def is_import_required(self) -> bool:
        if self._is_import_required is None:
            raise Exception("Internal error: Don't call is_import_required() before do_it()!")
        else:
            return self._is_import_required
