# import the Flask class from the flask module
from flask import Flask, g, redirect
import psycopg2.extras


# Urls in the 'url_handlers' directory (one file for each new url)
# import a Blueprint
from url_handlers.basic_stats import basic_stats_page
from url_handlers.histogram import histogram_page
from url_handlers.boxplot import boxplot_page
from url_handlers.scatter_plot import scatter_plot_page
from url_handlers.barchart import barchart_page
from url_handlers.heatmap import heatmap_plot_page
from url_handlers.clustering_pl import clustering_plot_page
from url_handlers.coplots_pl import coplots_plot_page
from url_handlers.logout import logout_page

import os

from modules.import_scheduler import Scheduler
# create the application object
app = Flask(__name__)

# register blueprints here:
app.register_blueprint(logout_page)
app.register_blueprint(basic_stats_page)
app.register_blueprint(histogram_page)
app.register_blueprint(boxplot_page)
app.register_blueprint(scatter_plot_page)
app.register_blueprint(barchart_page)
app.register_blueprint(heatmap_plot_page)
app.register_blueprint(clustering_plot_page)
app.register_blueprint(coplots_plot_page)

# Set this connection URL in an environment variable, and then load it into your application configuration using
# os.environ, like this
user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DB']
port = os.environ['POSTGRES_PORT']
DATABASE_URL=f'postgresql://{user}:{password}@{host}:{port}/{database}'

# Connection with database
def connect_db():
    """ connects to our redis database """

#    app = os.environ["DATABASE_URL"] #this you need if you use Database_URL not everything separately

    db = getattr(g, '_database', None)
    if db is None:
#        db = psycopg2.connect(app)
        db = psycopg2.connect(DATABASE_URL)
    return db



""" Direct to Basic Stats website during opening the program."""
@app.route('/', methods=['GET'])
def login():
    return redirect('/basic_stats')



# Import data to redis
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
    scheduler = Scheduler(day_of_week=day_of_week, hour=hour, minute=minute)
    scheduler.start()
    scheduler.stop()

def main():
    return app