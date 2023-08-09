from os import unlink, stat
from os.path import dirname, join, exists
from pytest import fixture
from sqlalchemy import select, func

from medex.services.config import Config, set_config
from medex.database_schema import NumericalValueTable, CategoricalValueTable, PatientTable

# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session
from medex.services.importer import get_importer


@fixture
def config():
    my_config = Config(import_directory=join(dirname(__file__), 'data'))
    set_config(my_config)
    yield my_config


@fixture
def marker(config):
    yield
    if exists(config.import_marker_path):
        unlink(config.import_marker_path)


def test_importer(db_session, config, marker):
    importer = get_importer()
    importer.setup_database()

    rs_num = db_session.execute(select(func.count(NumericalValueTable.id).label('count'))).first()
    numerical_values = rs_num.count
    rs_cat = db_session.execute(select(func.count(CategoricalValueTable.id).label('count'))).first()
    categorical_values = rs_cat.count
    assert numerical_values + categorical_values == 2000

    rs_papient = db_session.execute(select(func.count(PatientTable.case_id).label('count'))).first()
    patient_entries = rs_papient.count
    assert patient_entries == 200

    assert exists(config.import_marker_path)
    mtime_of_marker_file = stat(config.import_marker_path).st_mtime

    importer = get_importer()
    importer.setup_database()

    assert exists(config.import_marker_path)
    new_mtime_of_marker_file = stat(config.import_marker_path).st_mtime
    assert new_mtime_of_marker_file == mtime_of_marker_file
