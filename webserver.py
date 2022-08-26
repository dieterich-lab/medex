from flask import Flask, send_file, request, redirect, session, g, jsonify, send_from_directory
from modules.import_scheduler import Scheduler
from modules.database_sessions import DatabaseSessionFactory
import modules.load_data_to_select as ps
from modules.get_data_to_table_browser import get_data_download
import url_handlers.filtering as filtering
from modules.filtering import get_case_ids
from flask_cors import CORS
from db import connect_db, close_db
import requests
import os
import io


# create the application object
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)

with app.app_context():
    connect_db()
    rdb = g.db


@app.teardown_appcontext
def teardown_db(exception):
    close_db()


factory = DatabaseSessionFactory(rdb)


def check_for_env(key: str, default=None, cast=None):
    if key in os.environ:
        if cast:
            return cast(os.environ.get(key))
        return os.environ.get(key)
    return default


# date and hours to import data
day_of_week = check_for_env('IMPORT_DAY_OF_WEEK', default='mon-sun')
hour = check_for_env('IMPORT_HOUR', default=5)
minute = check_for_env('IMPORT_MINUTE', default=5)


# Import data using function scheduler from package modules
if os.environ.get('IMPORT_DISABLED') is None:
    scheduler = Scheduler(rdb, day_of_week=day_of_week, hour=hour, minute=minute)
    scheduler.start()
    scheduler.stop()


# get all numeric and categorical entities from database
Name_ID, measurement_name = ps.get_header(rdb)
size_num_tab, size_date_tab, size_cat_tab = ps.get_database_information(rdb)
start_date, end_date = ps.get_date(rdb)
all_patient = ps.patient(rdb)
all_entities, all_num_entities, all_cat_entities, all_date_entities, length = ps.get_entities(rdb)
df_min_max = ps.min_max_value_numeric_entities(rdb)
all_subcategory_entities = ps.get_subcategories_from_categorical_entities(rdb)
all_measurement, block_measurement = ps.get_measurement(rdb)

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
    print(session.get('session_id'))
    if session.get('session_id') is None:
        session['session_id'] = os.urandom(10)
        factory.get_session(session.get('session_id'))
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
                categorical_filter_results=session.get('filtering')['filter_cat'],
                numerical_filter_results=session.get('filtering')['filter_num'],
                limit_offset=session.get('limit_offset')
                )


# import a Blueprint
from url_handlers.data import data_page
from url_handlers.basic_stats import basic_stats_page
from url_handlers.histogram import histogram_page
from url_handlers.boxplot import boxplot_page
from url_handlers.scatter_plot import scatter_plot_page
from url_handlers.barchart import barchart_page
from url_handlers.heatmap import heatmap_plot_page
from url_handlers.logout import logout_page
from url_handlers.tutorial import tutorial_page

# register blueprints here:\
app.register_blueprint(data_page)
app.register_blueprint(logout_page)
app.register_blueprint(tutorial_page)
app.register_blueprint(basic_stats_page)
app.register_blueprint(histogram_page)
app.register_blueprint(boxplot_page)
app.register_blueprint(scatter_plot_page)
app.register_blueprint(barchart_page)
app.register_blueprint(heatmap_plot_page)


@app.route('/_session', methods=['GET'])
def get_cases():
    session_id = request.args.get('sessionid')
    session_id_json = {"session_id": "{}".format(session_id)}
    cases_get = requests.post(EXPRESS_MEDEX_MEDDUSA_URL + '/result/cases/get', json=session_id_json)
    case_ids = cases_get.json()
    session_db = factory.get_session(session.get('session_id'))
    filtering.add_case_id(case_ids, session_db)
    session['filtering'] = session.get('filtering')
    return redirect('/')


# Direct to Data browser website during opening the program.
@app.route('/', methods=['GET'])
def login_get():
    return redirect('/data')


@app.route('/filtering', methods=['POST', 'GET'])
def filter_data():
    session_db = factory.get_session(session.get('session_id'))
    results = {}
    if request.is_json:
        filters = request.get_json()
        if 'clean' in filters[0]:
            results = filtering.clean_all_filter(session_db)
        elif 'clean_one_filter' in filters[0]:
            results = filtering.clean_one_filter(filters, session_db)
        elif 'cat' in filters[0]:
            results = filtering.add_categorical_filter(filters, session_db)
        elif "num" in filters[0]:
            results = filtering. add_numerical_filter(filters, session_db)
        session['filtering'] = session.get('filtering')
    return jsonify(results)


@app.route("/download/<path:filename>", methods=['GET', 'POST'])
def download(filename):
    session_db = factory.get_session(session.get('session_id'))
    if filename == 'basic_stats_data.csv':
        csv = session.get('basic_stats_table')
    elif filename == 'table_browser_data.csv':
        print(session.get('date_filter'))
        print(session.get('filtering'))
        print(session.get('table_browser'))
        string = create_string()
        csv = string
    elif filename == 'case_ids.csv':
        csv = get_case_ids(session_db)
    else:
        csv = ''
    # Create a bytes buffer from the string buffer
    buf_str = io.StringIO(csv)
    buf_byt = io.BytesIO(buf_str.read().encode("utf-8"))
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     attachment_filename=filename)


def create_string():
    string = 'date range:' + str(session.get('date_filter')[3]) + ' ' + str(session.get('date_filter')[4]) + '\n' + \
             'Filters:' + '\n' + 'categorical ' + str(session.get('filtering')['filter_cat']) + '\n' + \
             'numerical' + str(session.get('filtering')['filter_num']) + '\n' +\
             'selected values:' + '\n' + \
             'Visits' + str(session.get('table_browser')[1]) + '\n' + \
             'entities' + str(session.get('table_browser')[0]) + '\n' + \
             'Table' + str(session.get('table_browser')[2])
    return string


def main():
    return app
