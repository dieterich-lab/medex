import os
import sys
from configparser import ConfigParser
from datetime import datetime

from modules import models, load_data_to_database as ld, cluster_analyze as ca


class ImportSettings:
    """
    Class which create file dev_import necessary to import data.
    Inside the file we have two unique cods for files dataset and entities.
    The codes change every time we change anything in the files dataset and entities.
    If the codes has been changed the program loads new data.
    More about th code : https://www.computerhope.com/unix/sha512sum.htm
    """
    def __init__(self):
        if 'FLASK_DEBUG' in os.environ and os.environ['FLASK_DEBUG'] == '1':
            self.path = './import/dev_import.ini'
        else:
            self.path = "./import/import.ini"
        self.config = ConfigParser()
        self.config.read(self.path)
        if 'hashes' not in self.config.sections():
            self.create()

    def create(self):
        self.config.add_section('hashes')
        self.config.set('hashes', 'entity', "")
        self.config.set('hashes', 'dataset', "")
        self.config.set('hashes', 'date', "")

    def get_hash(self, path):
        return os.popen(f"sha512sum {path}").read().split(' ')[0]

    def update(self, entities_path, dataset_path):
        self.config['hashes']['entity'] = self.get_hash(entities_path)
        self.config['hashes']['dataset'] = self.get_hash(dataset_path)
        self.config['hashes']['date'] = str(datetime.now())

    def save(self):
        with open(self.path, 'w+') as cnfFile:
            self.config.write(cnfFile)

    def is_entity_changed(self, path):
        return self.config['hashes']['entity'] != self.get_hash(path)

    def is_dataset_changed(self, path):
        return self.config['hashes']['dataset'] != self.get_hash(path)

    def is_empty(self):
        if self.config['hashes']['dataset'] and self.config['hashes']['entity']:
            return False
        return True


def start_import():
    """ Import data from entities and dataset files"""

    settings = ImportSettings()
    print('starting import', datetime.now().strftime('%H:%M:%S'))
    dataset_path = './import/dataset.csv'
    entities_path = './import/entities.csv'
    header_path = './import/header.csv'

    if not os.path.isfile(dataset_path) or not os.path.isfile(entities_path):
        models.check_if_tables_exists()
        return print("Could not import to database either or entities.csv and dataset.csv is missing", file=sys.stderr)
    elif not settings.is_dataset_changed(dataset_path) and not settings.is_entity_changed(entities_path):
        models.check_if_tables_exists()
        return print("Data set not changed", file=sys.stderr)
    else:
        if not os.path.isfile(header_path):
            header = ['Name_ID', 'Case_ID', 'measurement']
        else:
            with open(header_path, 'r') as in_file:
                for row in in_file:
                    header = row.replace("\n", "").split(",")
                header = header[0:3]

        print("Start create tables")
        models.drop_tables()
        models.create_tables()
        print("Start load data ")
        ld.load_header(header)
        ld.load_data(entities_path, dataset_path, header)
        ld.patient_table()
        print("Start cluster_table ")
        ca.cluster_table()
        ca.analyze_table()
        ca.alter_system()

        settings.update(dataset_path=dataset_path, entities_path=entities_path)
        settings.save()
        print("End load data")
