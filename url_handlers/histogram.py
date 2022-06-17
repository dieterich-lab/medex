from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import all_measurement, measurement_name, block_measurement, factory
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
        measurement = all_measurement[0]
    else:
        measurement = request.form.getlist('measurement')
    entities = (request.form.get('numeric_entities'), request.form.get('categorical_entities'),
                request.form.getlist('subcategory_entities'))
    number_of_bins = request.form.get('number_of_bins')

    # get_filter
    date_filter = session.get('date_filter')
    limit_filter = filtering.check_for_limit_offset()
    update_filter = session.get('filter_update')

    # handling errors and load data from database
    df = pd.DataFrame()
    if measurement == "Search entity":
        error = "Please select number of {}".format(measurement_name)
    elif entities[0] == "Search entity" or entities[1] == "Search entity":
        error = "Please select entity"
    elif not entities[2]:
        error = "Please select subcategory"
    else:
        session_db = factory.get_session(session.get('session_id'))
        df, error = ps.get_histogram_box_plot(entities, measurement, date_filter, limit_filter, update_filter,
                                              session_db)

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
                               numeric_entities=entities[0],
                               categorical_entities=entities[1],
                               subcategory_entities=entities[2],
                               error=error)

    if block_measurement == 'none':
        fig = px.histogram(df, x=entities[0], color=entities[1], barmode='overlay', nbins=bin_numbers,
                           opacity=0.7, template="plotly_white")
    else:
        fig = px.histogram(df, x=entities[0], facet_row='measurement', color=entities[1],
                           barmode='overlay', nbins=bin_numbers, opacity=0.7, template="plotly_white")

    legend = textwrap.wrap(entities[1], width=20)
    fig.update_layout(
        font=dict(size=16),
        legend_title='<br>'.join(legend),
        height=1000,
        title={'text': '<b>' + entities[0] + '</b> by <b>' + entities[1] + '</b>',
               'x': 0.5,
               'xanchor': 'center'})
    fig = fig.to_html()
    return render_template('histogram.html',
                           number_of_bins=number_of_bins,
                           measurement=measurement,
                           numeric_entities=entities[0],
                           categorical_entities=entities[1],
                           subcategory_entities=entities[2],
                           plot=fig,
                           )
