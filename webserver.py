# import the Flask class from the flask module
from flask import Flask, send_file, request, redirect, session
import requests
from modules.import_scheduler import Scheduler
from url_handlers.models import TableBuilder
import modules.load_data_postgre as ps
from flask_cors import CORS
from db import connect_db
import pandas as pd
import os
import io
from flask import send_from_directory

# create the application object
app = Flask(__name__)

CORS(app)

app.secret_key = os.urandom(24)
with app.app_context():
    rdb = connect_db()

# data store for filters and download
class DataStore():

    case_ids = []
    table_case_ids = None

    # for table browser server side
    table_schema = None
    table_browser_column = None
    dict = None
    table_browser_entities = None
    table_browser_what_table = None
    table_browser_column2 = None

    year = None
    new_table = pd.DataFrame()
    new_table_dict = None
    new_table_schema = None

    # for download
    csv = None
    csv_new_table = None




table_builder = TableBuilder()
data = DataStore()

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
start_date, end_date = ps.get_date(rdb)
all_patient = ps.patient(rdb)
all_entities = ps.get_entities(rdb)
size_numerical_table, all_numeric_entities, df_min_max = ps.get_numeric_entities(rdb)
size_timestamp_table, all_timestamp_entities = ps.get_timestamp_entities(rdb)
size_categorical_table, all_categorical_entities, all_subcategory_entities = ps.get_categorical_entities(rdb)
all_entities = all_entities.to_dict('index')
all_numeric_entities = all_numeric_entities.to_dict('index')
all_categorical_entities = all_categorical_entities.to_dict('index')
all_timestamp_entities = all_timestamp_entities.to_dict('index')
df_min_max = df_min_max.to_dict('index')
all_measurement = ps.get_measurement(rdb)


# show all hide measurement selector when was only one measurement for all entities
if len(all_measurement) < 2:
    block = 'none'
else:
    block = 'block'





# favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='vnd.microsoft.icon')


# information about database
@app.context_processor
def message_count():
    case = session.get('case_ids')
    if case != None :
        case_display = 'block'
    else:
        data.case_ids = []
        case_display = 'none'
    new_column = session.get('new_column')
    if new_column != None:
        data.case_ids = []
    database_name = os.environ['POSTGRES_DB']
    database = '{} data'.format(database_name)
    if all_numeric_entities:
        len_numeric = 'number of numerical entities: ' + str(len(all_numeric_entities))
        size_numeric = 'the size of the numeric table: ' + str(size_numerical_table) + ' rows'
        len_categorical = 'number of categorical entities: ' + str(len(all_categorical_entities))
        size_categorical = 'the size of the categorical table: ' + str(size_categorical_table) + ' rows'
    else:
        len_numeric = 'number of numerical entities: 0'
        size_numeric = 'the size of the numeric table: 0 rows'
        len_categorical = 'number of categorical entities: 0'
        size_categorical = 'the size of the categorical table: 0 rows'

    return dict(database=database,
                len_numeric=len_numeric,
                size_numeric=size_numeric,
                len_categorical=len_categorical,
                size_categorical=size_categorical,
                all_numeric_entities=all_numeric_entities,
                all_numeric_entities2=session.get('new_column'),
                all_categorical_entities=all_categorical_entities,
                all_subcategory_entities=all_subcategory_entities,
                all_timestamp_entities=all_timestamp_entities,
                all_measurement=all_measurement,
                df_min_max=df_min_max,
                start_date=start_date,
                end_date=end_date,
                name='{}'.format(measurement_name),
                block=block,
                case_display=case_display)


# Urls in the 'url_handlers' directory (one file for each new url)
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
from url_handlers.calculator import calculator_page

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
app.register_blueprint(calculator_page)


# Direct to Data browser website during opening the program.
@app.route('/', methods=['GET'])
def login_get():
    # get selected entities
    session['start_date'] = start_date
    session['end_date'] = end_date
    session['measurement_filter'] = '1'
    session['new_column'] = []
    return redirect('/data')


try:
    EXPRESS_MEDEX_MEDDUSA_URL = os.environ['EXPRESS_MEDEX_MEDDUSA_URL']
except Exception:
    EXPRESS_MEDEX_MEDDUSA_URL = 'http://localhost:3500/result/cases/get'


@app.route('/_session', methods=['GET'])
def get_cases():
    session_id = request.args.get('sessionid')
    session_id_json = {"session_id": "{}".format(session_id)}
    cases_get = requests.post(EXPRESS_MEDEX_MEDDUSA_URL, json=session_id_json)
    case_ids = cases_get.json()
    data.case_ids = case_ids['cases_ids']
    data.table_case_ids = pd.DataFrame(case_ids['cases_ids'], columns=["Case_ID"]).to_csv(index=False)
    session['case_ids'] = 'Yes'
    return redirect('/')


@app.route("/download/<path:filename>", methods=['GET', 'POST'])
def download(filename):
    if filename == 'data.csv':
        csv = data.csv
    elif filename == 'case_ids.csv':
        csv = data.table_case_ids
    # Create a string buffer
    buf_str = io.StringIO(csv)

    # Create a bytes buffer from the string buffer
    buf_byt = io.BytesIO(buf_str.read().encode("utf-8"))
    # Return the CSV data as an attachment
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     attachment_filename=filename)


def main():
    return app
