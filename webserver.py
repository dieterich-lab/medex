# import the Flask class from the flask module
from flask import Flask, send_file, render_template, request,redirect,session
import requests
from modules.import_scheduler import Scheduler
from url_handlers.models import TableBuilder
import modules.load_data_postgre as ps
from flask_cors import CORS
from db import connect_db
import url_handlers.filtering as filtering
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
try:
    Name_ID, measurement_name = ps.get_header(rdb)['Name_ID'][0], ps.get_header(rdb)['measurement'][0]
except:
    Name_ID, measurement_name='Name_ID', 'measurement'
all_entities, show = ps.get_entities(rdb)
all_patient = ps.patient(rdb)
size_numerical_table, all_numeric_entities,df_min_max  = ps.get_numeric_entities(rdb)
size_categorical_table, all_categorical_entities, all_subcategory_entities = ps.get_categorical_entities(rdb)
all_entities = all_entities.to_dict('index')
all_numeric_entities = all_numeric_entities.to_dict('index')
all_categorical_entities = all_categorical_entities.to_dict('index')
df_min_max = df_min_max.to_dict('index')
all_measurement = ps.get_measurement(rdb)
start_date, end_date,date = ps.get_date(rdb)


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
    database_name = os.environ['POSTGRES_DB']
    database = '{} data'.format(database_name)
    len_numeric = 'number of numerical entities: ' + str(len(all_numeric_entities))
    size_numeric = 'the size of the numeric table: ' + str(size_numerical_table) + ' rows'
    len_categorical = 'number of categorical entities: ' + str(len(all_categorical_entities))
    size_categorical = 'the size of the categorical table: ' + str(size_categorical_table) + ' rows'

    return dict(database=database,len_numeric=len_numeric,size_numeric=size_numeric,len_categorical=len_categorical,
                size_categorical=size_categorical,start_date=start_date,end_date=end_date)

# data store for filters and download
class DataStore():

    # for filter
    id_filter = []
    categorical_filter = ''
    categorical_names = []

    # for table browser server side
    table_schema = None
    table_browser_column = None
    dict = None
    table_browser_entities = None
    table_browser_what_table = None

    # for download
    csv = None
    patient_id = None
    table_browser_column2 = None


table_builder = TableBuilder()
data = DataStore()

# Urls in the 'url_handlers' directory (one file for each new url)
# import a Blueprint
from url_handlers.data import data_page
from url_handlers.basic_stats import basic_stats_page
from url_handlers.histogram import histogram_page
from url_handlers.boxplot import boxplot_page
from url_handlers.scatter_plot import scatter_plot_page
from url_handlers.barchart import barchart_page
from url_handlers.heatmap import heatmap_plot_page
from url_handlers.coplots_pl import coplots_plot_page
from url_handlers.logout import logout_page
from url_handlers.tutorial import tutorial_page
from url_handlers.sidebar import sidebar_page

# register blueprints here:\
app.register_blueprint(sidebar_page)
app.register_blueprint(data_page)
app.register_blueprint(logout_page)
app.register_blueprint(tutorial_page)
app.register_blueprint(basic_stats_page)
app.register_blueprint(histogram_page)
app.register_blueprint(boxplot_page)
app.register_blueprint(scatter_plot_page)
app.register_blueprint(barchart_page)
app.register_blueprint(heatmap_plot_page)
app.register_blueprint(coplots_plot_page)


# Direct to Data browser website during opening the program.
@app.route('/', methods=['GET'])
def login_get():
    # get selected entities

    session['start_date'] = start_date
    session['end_date'] = end_date

    entities = show['Key'].tolist()
    what_table = 'long'
    categorical_filter = ''
    categorical_names = []
    id_filter = data.id_filter
    df, error = ps.get_data(entities, what_table, categorical_filter, categorical_names, id_filter,date, rdb)
    if not df.empty:
        if block == 'none':
            df = df.drop(columns=['measurement'])
            df = df.rename(columns={"Name_ID": "{}".format(measurement_name)})
        else:
            df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})

    data.csv = df.to_csv(index=False)

    column = df.columns.tolist()
    column_change_name = []
    column_dict = []
    table_schema = []

    [column_change_name.append(i.replace('.', '_')) for i in column]
    df.columns = column_change_name

    data.dict = df.to_dict("records")
    [column_dict.append({'data': column_change_name[i]}) for i in range(0, len(column_change_name))]
    [table_schema.append({'data_name': column_change_name[i], 'column_name': column_change_name[i], "default": "",
                          "order": 1, "searchable": True}) for i in range(0, len(column_change_name))]
    data.table_schema = table_schema
    data.table_browser_column = column
    data.table_browser_what_table = what_table
    data.table_browser_column2 = column_dict

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_numeric_entities=all_numeric_entities,
                           start_date=session.get('start_date'),
                           end_date=session.get('end_date'),
                           entities=entities,
                           name=column,
                           what_table=what_table,
                           column=column_dict,
                           df_min_max=df_min_max
                           )



@app.route('/', methods=['POST'])
def login_post():

    # get selected entities
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')

    # get filter

    start_date,end_date,date = filtering.check_for_date_filter_post()
    id_filter = data.id_filter
    categorical_filter, categorical_names, categorical_filter_zip = filtering.check_for_filter_post()

    # errors
    if len(entities) == 0:
        error = "Please select entities"
    else:
       df, error = ps.get_data(entities, what_table, categorical_filter, categorical_names, id_filter,date, rdb)

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities,
                               start_date=start_date,
                               end_date=end_date,
                               entities=entities,
                               filter=categorical_filter_zip,
                               df_min_max=df_min_max
                               )

    df = filtering.checking_for_block(block, df, Name_ID, measurement_name)

    data.table_browser_entities = entities
    data.csv = df.to_csv(index=False)
    column = df.columns.tolist()

    column_change_name = []
    [column_change_name.append(i.replace('.','_')) for i in column]
    df.columns = column_change_name

    data.dict = df.to_dict("records")
    dict_of_column = []
    table_schema = []

    [dict_of_column.append({'data': column_change_name[i]}) for i in range(0, len(column_change_name))]
    [table_schema.append({'data_name': column_change_name[i], 'column_name': column_change_name[i], "default": "",
                          "order": 1, "searchable": True}) for i in range(0, len(column_change_name))]

    data.table_schema = table_schema
    data.table_browser_column = column
    data.table_browser_what_table = what_table
    data.table_browser_column2 = dict_of_column

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities,
                           entities=entities,
                           name=column,
                           start_date=start_date,
                           end_date=end_date,
                           what_table=what_table,
                           column=dict_of_column,
                           filter=categorical_filter_zip,
                           df_min_max=df_min_max
                           )


try:
    EXPRESS_MEDEX_MEDDUSA_URL = os.environ['EXPRESS_MEDEX_MEDDUSA_URL']
except Exception:
    EXPRESS_MEDEX_MEDDUSA_URL='http://localhost:3500/result/cases/get'


@app.route('/_session', methods=['GET'])
def get_cases():
    session_id = request.args.get('sessionid')
    session_id_json = {"session_id": "{}".format(session_id)}
    cases_get = requests.post(EXPRESS_MEDEX_MEDDUSA_URL, json=session_id_json)
    cases_ids = cases_get.json()
    data.id_filter = cases_ids['cases_ids']
    data.patient_id = pd.DataFrame(cases_ids['cases_ids'], columns=["Case_ID"]).to_csv(index=False)

    return redirect('/data')


@app.route("/download/<path:filename>", methods=['GET', 'POST'])
def download(filename):
    if filename == 'data.csv':
        csv = data.csv
    elif filename == 'patient_id.csv':
        csv = data.patient_id
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
