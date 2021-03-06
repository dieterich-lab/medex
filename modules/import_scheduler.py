from modules import import_dataset as id
from configparser import ConfigParser
import os
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler



class ImportSettings():
    """
    Class which create file dev_import necessary to import data.
    Inside the file we have two unique cods for files dataset and entities.
    The codes change every time we change anything in the files dataset and entites.
    If the codes has been changed the program loads new data.
    More about th code : https://www.computerhope.com/unix/sha512sum.htm
    """
    def __init__(self):
        if os.environ['FLASK_ENV'] == 'production':
            self.path = "./import/import.ini"
        else:
            self.path = './import/dev_import.ini'
        self.config = ConfigParser()
        self.config.read(self.path)
        if 'hashes' not in self.config.sections():
            self.create()

    def create(self):
        self.config.add_section('hashes')
        self.config.set('hashes', 'entity', "")
        self.config.set('hashes', 'dataset', "")
        self.config.set('hashes', 'date', "")

    def update(self, entities_path, dataset_path):
        self.config['hashes']['entity'] = self.get_hash(entities_path)
        self.config['hashes']['dataset'] = self.get_hash(dataset_path)
        self.config['hashes']['date'] = str(datetime.now())

    def save(self):
        with open(self.path, 'w+') as cnfFile:
            self.config.write(cnfFile)

    def get_hash(self, path):
        return os.popen(f"sha512sum {path}").read() \
            .split(' ')[0]

    # Check that data in enities and dataset was changed
    def is_entity_changed(self, path):
        hash = self.get_hash(path)
        return self.config['hashes']['entity'] != hash

    def is_dataset_changed(self, path):
        hash = self.get_hash(path)
        return self.config['hashes']['dataset'] != hash

    def is_empty(self):
        if self.config['hashes']['dataset'] and self.config['hashes']['entity']:
            return False
        return True


def start_import():
    """ Import data from entities and dataset files"""

    settings = ImportSettings()
    print('starting import', datetime.now().strftime('%H:%M:%S'))
    dataset = './import/dataset.csv'
    entities = './import/entities.csv'

    if not os.path.isfile(dataset) or not os.path.isfile(entities):
        return print("Could not import to database either or both entities and dataset is missing", file=sys.stderr)

    if not settings.is_dataset_changed(dataset) and not settings.is_entity_changed(entities):
        return print("Data set not changed", file=sys.stderr)

    numeric_entities, categorical_entities = id.import_entity_types(entities)

    id.import_dataset(os.environ['REDIS_URL'], dataset, numeric_entities, categorical_entities)
    settings.update(dataset_path=dataset, entities_path=entities)
    settings.save()


class Scheduler():
    """
    BackgroundScheduler runs in a thread inside existing application.
    Importing data check the data. Import data every day at 05.05 if the program see any changes.
    """
    def __init__(self, day_of_week, hour, minute):
        self.bgs = BackgroundScheduler()
        start_import()
        self.bgs.add_job(start_import, 'cron', day_of_week=day_of_week, hour=hour, minute=minute)

    def start(self):
        self.bgs.start()

    def stop(self):
        print('exit scheduler')
        self.bgs.shutdown()
