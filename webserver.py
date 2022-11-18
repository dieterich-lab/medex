from flask import Flask, send_file, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from medex.controller.helpers import get_filter_service
from modules.import_scheduler import Scheduler, start_import
from medex.services.database import get_db_session, get_database_url, init_db
import modules.load_data_to_select as ps
from modules.get_data_to_table_browser import get_data_download
import url_handlers.filtering as filtering
from flask_cors import CORS
import requests
import os
import io
from medex.controller.filter import filter_controller

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
    start_import()

# ToDo: Do we need an App Context for scheduled runs of "start_import" too?

# date and hours to import data
day_of_week = check_for_env('IMPORT_DAY_OF_WEEK', default='mon-sun')
hour = check_for_env('IMPORT_HOUR', default=5)
minute = check_for_env('IMPORT_MINUTE', default=5)

# Import data using function scheduler from package modules
if os.environ.get('IMPORT_DISABLED') is None:
    scheduler = Scheduler(day_of_week=day_of_week, hour=hour, minute=minute)
    scheduler.start()
    scheduler.stop()

# get all numeric and categorical entities from database
Name_ID, measurement_name = ps.get_header()
size_num_tab, size_date_tab, size_cat_tab = ps.get_database_information()
start_date, end_date = ps.get_date()
all_patient = ps.patient()
all_entities, all_num_entities, all_cat_entities, all_date_entities, length = ps.get_entities()
df_min_max = ps.min_max_value_numeric_entities()
all_subcategory_entities = ps.get_subcategories_from_categorical_entities()
all_measurement, block_measurement = ps.get_measurement()

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

    return dict(database_information=(database, len_numeric, size_numeric, len_categorical, size_categorical),
                entities=(all_num_entities, all_cat_entities, all_subcategory_entities, all_date_entities),
                measurement_tuple=(all_measurement, '{}:'.format(measurement_name), block_measurement),
                df_min_max=df_min_max,
                meddusa=(Meddusa, MEDDUSA_URL),
                )


# information about database
@app.context_processor
def message_count():
    if 'filtering' not in session:
        session['filtering'] = {'filter_update': '0', 'case_id': 'No', 'filter_num': {}, 'filter_cat': {}}

    if session.get('filtering')['case_id'] == 'No':
        case_display = 'none'
    else:
        case_display = 'block'

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
                case_display=case_display,
                filter_update=session.get('filtering')['filter_update'],
                limit_offset=session.get('limit_offset')
                )


from url_handlers.data import data_page
from url_handlers.basic_stats import basic_stats_page
from url_handlers.histogram import histogram_page
from url_handlers.boxplot import boxplot_page
from url_handlers.scatter_plot import scatter_plot_page
from url_handlers.barchart import barchart_page
from url_handlers.heatmap import heatmap_plot_page
from url_handlers.logout import logout_page
from url_handlers.tutorial import tutorial_page

app.register_blueprint(data_page)
app.register_blueprint(logout_page)
app.register_blueprint(tutorial_page)
app.register_blueprint(basic_stats_page)
app.register_blueprint(histogram_page)
app.register_blueprint(boxplot_page)
app.register_blueprint(scatter_plot_page)
app.register_blueprint(barchart_page)
app.register_blueprint(heatmap_plot_page)
app.register_blueprint(filter_controller, url_prefix='/filter')


@app.route('/_session', methods=['GET'])
def get_cases():
    session_id = request.args.get('sessionid')
    session_id_json = {"session_id": "{}".format(session_id)}
    cases_get = requests.post(EXPRESS_MEDEX_MEDDUSA_URL + '/result/cases/get', json=session_id_json)
    case_ids = cases_get.json()
    session_db = get_db_session()
    filtering.add_case_id(case_ids, session_db)
    session['filtering'] = session.get('filtering')
    return redirect('/')


# Direct to Data browser website during opening the program.
@app.route('/', methods=['GET'])
def login_get():
    return redirect('/data')


@app.route("/download/<path:filename>", methods=['GET', 'POST'])
def download(filename):
    session_db = get_db_session()
    filter_service = get_filter_service()
    if filename == 'basic_stats_data.csv':
        csv = session.get('basic_stats_table')
    elif filename == 'table_browser_data.csv':
        update_filter = session.get('filtering')
        table_browser = session.get('table_browser')
        date_filter = session.get('date_filter')
        csv = get_data_download(table_browser, date_filter, filter_service, session_db)
    # elif filename == 'case_ids.csv':
    #     csv = get_case_ids(session_db)
    else:
        csv = ''
    # Create a bytes buffer from the string buffer
    buf_str = io.StringIO(csv)
    buf_byt = io.BytesIO(buf_str.read().encode("utf-8"))
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name=filename)


def main():
    return app
