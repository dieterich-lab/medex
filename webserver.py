import os
from flask import Flask, redirect, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import modules.load_data_to_select as ps
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
from medex.controller.logout import logout_controller

# create the application object
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    init_db(db.engine, lambda: db.session)


def check_for_env(key: str, default=None, cast=None):
    if key in os.environ:
        if cast:
            return cast(os.environ.get(key))
        return os.environ.get(key)
    return default


with app.app_context():
    get_importer().setup_database()

if os.environ.get('IMPORT_DISABLED') is None:
    scheduler = Scheduler(app)
    scheduler.start()

# get all numeric and categorical entities from database
with app.app_context():
    Name_ID, measurement_name = ps.get_header()
    size_num_tab, size_date_tab, size_cat_tab = ps.get_database_information()
    start_date, end_date = ps.get_date()
    number_of_patients = ps.get_number_of_patients()
    length = ps.get_entities()

# change this
try:
    EXPRESS_MEDEX_MEDDUSA_URL = os.environ['EXPRESS_MEDEX_MEDDUSA_URL']
    MEDDUSA_URL = os.environ['MEDDUSA_URL']
    Meddusa = 'block'
except (Exception,):
    EXPRESS_MEDEX_MEDDUSA_URL = 'http://localhost:3500'
    MEDDUSA_URL = 'http://localhost:3000'
    Meddusa = 'block'


# favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='vnd.microsoft.icon')


# information about database
@app.context_processor
def data_information():
    database = '{} data'.format(os.environ['POSTGRES_DB'])
    len_numeric = 'number of numerical entities: ' + length[0]
    size_numeric = 'the size of the numeric table: ' + str(size_num_tab) + ' rows'
    len_categorical = 'number of categorical entities: ' + length[1]
    size_categorical = 'the size of the categorical table: ' + str(size_cat_tab) + ' rows'
    number_of_patients_str = 'Number of all patients: ' + str(number_of_patients)

    return dict(database_information=(database, len_numeric, size_numeric, len_categorical, size_categorical,
                                      number_of_patients_str),
                meddusa=(Meddusa, MEDDUSA_URL),
                )


# information about database
@app.context_processor
def message_count():
    if 'filtering' not in session:
        session['filtering'] = {'filter_update': '0', 'case_id': 'No', 'filter_num': {}, 'filter_cat': {}}

    if start_date == end_date:
        date_block = 'none'
    else:
        date_block = 'block'

    if session.get('limit_offset') is None:
        session['limit_offset'] = (10000, 0, False)
    if session.get('date_filter') is None:
        session['date_filter'] = (start_date, end_date, 0)

    return dict(date_block=date_block,
                date=session.get('date_filter'),
                limit_offset=session.get('limit_offset')
                )


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
app.register_blueprint(logout_controller, url_prefix='/logout')


# Direct to Data browser website during opening the program.
@app.route('/', methods=['GET'])
def login_get():
    return redirect('/filtered_data')


def main():
    return app
