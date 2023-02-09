from os.path import exists

from medex.services.database import get_db_session, get_db_engine
from medex.services.entity import EntityService
from medex.services.config import Config, get_config
from medex.services.importer.database_setup import DatabaseSetup
from medex.services.importer.dataset import DatasetImporter
from medex.services.importer.entitity import EntityImporter
from medex.services.importer.header import HeaderImporter


class Importer:
    def __init__(
            self,
            setup: DatabaseSetup,
            header_importer: HeaderImporter,
            config: Config,
            entity_importer: EntityImporter = None,
            dataset_importer: DatasetImporter = None,
    ):
        self._setup = setup
        self._header_importer = header_importer
        self._entity_importer = entity_importer
        self._dataset_importer = dataset_importer
        self._config = config

    def setup_database(self):
        self._setup.do_it()
        if self._setup.is_import_required():
            self._do_import_preflight_check()
            config = self._config
            print(f"Loading headers from {config.header_path} ...")
            self._header_importer.setup_header_names()
            print(f"Loading entities from {config.entities_path} ...")
            self._entity_importer.import_all()
            print(f"Loading data from {config.dataset_path} ...")
            self._dataset_importer.import_all()
            print('Populating patient table ...')
            self._dataset_importer.populate_patient_table()
            print('Optimizing tables ...')
            self._dataset_importer.optimize_tables()
        print('Database setup completed.')

    def _do_import_preflight_check(self):
        config = self._config
        if self._entity_importer is None:
            raise Exception(f"The file '{config.entities_path}' is missing - aborting.")
        if self._dataset_importer is None:
            raise Exception(f"The file '{config.dataset_path}' is missing - aborting.")


def get_importer():
    config = get_config()
    db_session = get_db_session()
    db_engine = get_db_engine()

    return Importer(
        setup=DatabaseSetup(db_session=db_session, db_engine=db_engine, config=config),
        header_importer=_get_header_importer(db_session, config),
        entity_importer=_get_entity_importer(db_session, config),
        dataset_importer=_get_dataset_importer(db_session, config),
        config=config
    )


def _get_header_importer(db_session, config):
    header_file_handle = None
    if exists(config.header_path):
        header_file_handle = open(config.header_path, 'r', encoding='utf-8')
    return HeaderImporter(
        file_handle=header_file_handle,
        source_name=config.header_path,
        db_session=db_session
    )


def _get_entity_importer(db_session, config):
    if not exists(config.entities_path):
        return None
    return EntityImporter(
        file_handle=open(config.entities_path, 'r', encoding='utf-8'),
        source_name=config.entities_path,
        db_session=db_session
    )


def _get_dataset_importer(db_session, config):
    if not exists(config.dataset_path):
        return None
    return DatasetImporter(
        file_handle=open(config.dataset_path, 'r', encoding='utf-8'),
        source_name=config.dataset_path,
        entity_service=EntityService(database_session=db_session),
        db_session=db_session,
    )
