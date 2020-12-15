# import the Flask class from the flask module
from flask import Flask, redirect, session, send_file, render_template, Response, request, url_for
from modules.import_scheduler import Scheduler
from url_handlers.models import TableBuilder
import modules.load_data_postgre as ps
from db import connect_db
import pandas as pd
import os
import io


# create the application object
app = Flask(__name__)

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
    scheduler = Scheduler(rdb,day_of_week=day_of_week, hour=hour, minute=minute)
    scheduler.start()
    scheduler.stop()


# get all numeric and categorical entities from database
name2, name = ps.get_header(rdb)['Name_ID'][0], ps.get_header(rdb)['measurement'][0]
all_numeric_entities, size_n = ps.get_numeric_entities(rdb)
all_categorical_entities, all_subcategory_entities, size_c, entity = ps.get_categorical_entities(rdb)
all_entities = all_numeric_entities .append(all_categorical_entities, ignore_index=True, sort=False)
all_entities = all_entities.to_dict('index')
all_numeric_entities = all_numeric_entities.to_dict('index')
all_categorical_entities = all_categorical_entities.to_dict('index')
all_measurement = ps.get_measurement(rdb)

if len(all_measurement) < 2:
    block = 'none'
else:
    block = 'block'


database_name = os.environ['POSTGRES_DB']
database='{} data'.format(database_name)
len_numeric = 'number of numerical entities: ' + str(len(all_numeric_entities))
size_numeric = 'the size of the numeric table: ' + str(size_n) + ' rows'
len_categorical = 'number of categorical entities: ' + str(len(all_categorical_entities))
size_categorical = 'the size of the categorical table: ' + str(size_c)+' rows'



# data store for download and so I need work on this and check !!!
class DataStore():
    csv = None
    dict = None
    table_schema = None
    table_browser_entites = None
    data_x_axis= None

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
from url_handlers.clustering_pl import clustering_plot_page
from url_handlers.coplots_pl import coplots_plot_page
from url_handlers.logout import logout_page

# register blueprints here:
app.register_blueprint(data_page)
app.register_blueprint(logout_page)
app.register_blueprint(basic_stats_page)
app.register_blueprint(histogram_page)
app.register_blueprint(boxplot_page)
app.register_blueprint(scatter_plot_page)
app.register_blueprint(barchart_page)
app.register_blueprint(heatmap_plot_page)
app.register_blueprint(clustering_plot_page)
app.register_blueprint(coplots_plot_page)


# Direct to Data browser website during opening the program.
@app.route('/', methods=['GET'])
def login():
    # get selected entities
    entities = entity['Key'].tolist()
    what_table = 'long'

    if len(entities) == 0:
        error = "Please select entities"
    else:
        df, error = ps.get_data(entities, what_table, rdb)
    # handling errors and load data from database

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               entities=entities)

    if block == 'none':
        df = df.drop(columns=['measurement'])
    else:
        df = df.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})

    column = df.columns.tolist()

    data.csv = df.to_csv(index=False)
    data.dict = df.to_dict("records")


    dictOfcolumn=[]
    table_schema=[]
    [dictOfcolumn.append({'data': column[i]}) for i in range(0, len(column))]
    [table_schema.append({'data_name': column[i],'column_name': column[i],"default": "","order": 1,"searchable": True}) for i in range(0, len(column))]
    data.table_schema = table_schema

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           entities=entities,
                           name=column,
                           what_table=what_table,
                           column=dictOfcolumn)


@app.route('/', methods=['POST'])
def login2():
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')

    if len(entities) == 0 :
        error = "Please select entities"
    else:
       df, error = ps.get_data(entities,what_table, rdb)
    # handling errors and load data from database

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               entities=entities)

    if block == 'none':
        df = df.drop(columns=['measurement'])
    else:
        df = df.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})

    data.csv = df.to_csv(index=False)
    column = df.columns.tolist()

    column_change_name=[]
    [column_change_name.append(i.replace('.','_')) for i in column]
    df.columns = column_change_name

    data.dict = df.to_dict("records")
    dictOfcolumn=[]
    table_schema=[]
    [dictOfcolumn.append({'data': column_change_name[i]}) for i in range(0, len(column_change_name))]
    [table_schema.append({'data_name': column_change_name[i],'column_name': column_change_name[i],"default": "","order": 1,"searchable": True}) for i in range(0, len(column_change_name))]
    data.table_schema = table_schema

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           entities=entities,
                           name=column,
                           what_table=what_table,
                           column=dictOfcolumn
                           )


@app.route("/download", methods=['GET', 'POST'])
def download():

    csv=data.csv

    # Create a string buffer
    buf_str = io.StringIO(csv)

    # Create a bytes buffer from the string buffer
    buf_byt = io.BytesIO(buf_str.read().encode("utf-8"))

    # Return the CSV data as an attachment
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     attachment_filename="data.csv")


def main():

    return app
