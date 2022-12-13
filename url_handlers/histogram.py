from flask import Blueprint, render_template, request, session

from medex.controller.helpers import get_filter_service
from medex.services.database import get_db_session
from modules.get_data_to_histogrm import get_histogram_box_plot
import plotly.express as px
from url_handlers.filtering import check_for_date_filter_post, check_for_limit_offset
from url_handlers.utility import _is_valid_entity
from webserver import all_measurement, measurement_name, block_measurement, start_date, end_date
import pandas as pd
import textwrap

histogram_page = Blueprint('histogram', __name__, template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    number_of_bins = 20
    return render_template('histogram.html',
                           number_of_bins=number_of_bins)


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():

    # get request values
    if block_measurement == 'none':
        measurement = [all_measurement[0]]
    else:
        measurement = request.form.getlist('measurement')
    numerical_entity = request.form.get('numeric_entities')
    group_by_entity = request.form.get('categorical_entities')
    categories = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')

    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = check_for_limit_offset()

    # handling errors and load data from database
    df = pd.DataFrame()
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif not _is_valid_entity(numerical_entity):
        error = "Please select numeric entity"
    elif not _is_valid_entity(group_by_entity):
        error = "Please select 'group by' entity"
    elif not categories:
        error = "Please select subcategory"
    else:
        session_db = get_db_session()
        filter_service = get_filter_service()
        df, error = get_histogram_box_plot([numerical_entity, group_by_entity, categories], measurement, date_filter, limit_filter, filter_service, session_db)

    # handling errors if number of bins is less then 2
    bin_numbers = 20
    if number_of_bins.isdigit() and int(number_of_bins) > 2:
        bin_numbers = int(number_of_bins)
    elif number_of_bins == "":
        bin_numbers = 20
    else:
        error = "You have entered non-integer or negative value. Please use positive integer"

    if error:
        return render_template('histogram.html',
                               number_of_bins=number_of_bins,
                               measurement=measurement,
                               numeric_entities=numerical_entity,
                               categorical_entities=group_by_entity,
                               subcategory_entities=categories,
                               error=error)

    if block_measurement == 'none':
        fig = px.histogram(df, x=numerical_entity, color=group_by_entity, barmode='overlay', nbins=bin_numbers,
                           opacity=0.7, template="plotly_white")
    else:
        fig = px.histogram(df, x=numerical_entity, facet_row='measurement', color=group_by_entity,
                           barmode='overlay', nbins=bin_numbers, opacity=0.7, template="plotly_white")

    legend = textwrap.wrap(group_by_entity, width=20)
    fig.update_layout(
        font=dict(size=16),
        legend_title='<br>'.join(legend),
        height=1000,
        title={'text': '<b>' + numerical_entity + '</b> by <b>' + group_by_entity + '</b>',
               'x': 0.5,
               'xanchor': 'center'})
    fig = fig.to_html()
    return render_template('histogram.html',
                           number_of_bins=number_of_bins,
                           measurement=measurement,
                           numeric_entities=numerical_entity,
                           categorical_entities=group_by_entity,
                           subcategory_entities=categories,
                           plot=fig,
                           )


