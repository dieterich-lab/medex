from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, measurement_name, Name_ID, block, df_min_max, data
import pandas as pd
import textwrap
import time

information_page = Blueprint('information', __name__, template_folder='templates')


@information_page.route('/information', methods=['GET'])
def get_statistics():
    return render_template('information.html')


@information_page.route('/information', methods=['POST'])
def post_statistics():
    return render_template('information.html')