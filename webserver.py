import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from medex.controller.database_info import database_info_controller
from medex.services.database import get_database_url, init_db
from medex.services.scheduler import Scheduler
from medex.services.importer import get_importer

from medex.controller.measurement import measurement_controller
from medex.controller.filter import filter_controller
from medex.controller.entity import entity_controller
from medex.controller.data import data_controller
from medex.controller.basic_stats import basic_stats_controller
from medex.controller.scatter_plot import scatter_plot_controller
from medex.controller.barchart import barchart_controller
from medex.controller.histogram import histogram_controller
from medex.controller.boxplot import boxplot_controller
from medex.controller.heatmap import heatmap_controller
from medex.controller.tutorial import tutorial_controller
from medex.controller.root import root_controller

# create the application object
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    init_db(db.engine, lambda: db.session)
    get_importer().setup_database()

Scheduler(app).start()

app.register_blueprint(root_controller)
app.register_blueprint(database_info_controller, url_prefix='/database_info')
app.register_blueprint(measurement_controller, url_prefix='/measurement')
app.register_blueprint(filter_controller, url_prefix='/filter')
app.register_blueprint(entity_controller, url_prefix='/entity')
app.register_blueprint(data_controller, url_prefix='/filtered_data')
app.register_blueprint(basic_stats_controller, url_prefix='/basic_stats')
app.register_blueprint(scatter_plot_controller, url_prefix='/scatter_plot')
app.register_blueprint(barchart_controller, url_prefix='/barchart')
app.register_blueprint(histogram_controller, url_prefix='/histogram')
app.register_blueprint(boxplot_controller, url_prefix='/boxplot')
app.register_blueprint(heatmap_controller, url_prefix='/heatmap')
app.register_blueprint(tutorial_controller, url_prefix='/tutorial')


def main():
    return app
