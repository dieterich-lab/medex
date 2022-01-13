from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, Name_ID, measurement_name, block, df_min_max, data
import pandas as pd
import textwrap

histogram_page = Blueprint('histogram', __name__, template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    number_of_bins = 20
    start_date, end_date = filtering.date()
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    numerical_filter = filtering.check_for_numerical_filter_get()
    return render_template('histogram.html',
                           number_of_bins=number_of_bins,
                           start_date=start_date,
                           end_date=end_date,
                           measurement_filter=session.get('measurement_filter'),
                           filter=categorical_filter,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max
                           )


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():
    # get filters
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # show/hide selector for visits
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    # get selected entities
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')

    # handling errors and load data from database
    df = pd.DataFrame()
    if measurement == "Search entity":
        error = "Please select number of {}".format(measurement_name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        df_filtering = ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1,
                                    measurement_filter, rdb)
        data.Name_ID_filter = df_filtering
        filter = data.Name_ID_filter
        df, error = ps.get_histogram_box_plot(numeric_entities, categorical_entities, subcategory_entities, measurement,
                                              date, filter, rdb)
        #numeric_entities_unit, error = ps.get_unit(numeric_entities, rdb)
        df = filtering.checking_for_block(block, df, Name_ID, measurement_name)

    if error:
        return render_template('histogram.html',
                               number_of_bins=number_of_bins,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement=measurement,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               df_min_max=df_min_max,
                               error=error)

    # handling errors if number of bins is less then 2
    if number_of_bins.isdigit() and int(number_of_bins) > 2:
        bin_numbers = int(number_of_bins)
    elif number_of_bins == "":
        bin_numbers = 20
    else:
        error = "You have entered non-integer or negative value. Please use positive integer"
        return render_template('histogram.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               number_of_bins=number_of_bins,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement=measurement,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               df_min_max=df_min_max,
                               error=error)


    if block == 'none':
        fig = px.histogram(df, x=numeric_entities, color=categorical_entities,barmode='overlay', nbins=bin_numbers,
                           opacity=0.7, template="plotly_white")
    else:
        fig = px.histogram(df, x=numeric_entities, facet_row=measurement_name, color=categorical_entities,
                           barmode='overlay', nbins=bin_numbers, opacity=0.7, template="plotly_white")

    legend = textwrap.wrap(categorical_entities, width=20)
    fig.update_layout(
        font=dict(size=16),
        legend_title='<br>'.join(legend),
        height=1000,
        title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig = fig.to_html()

    return render_template('histogram.html',
                           number_of_bins=number_of_bins,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement=measurement,
                           measurement_filter=measurement_filter,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max,
                           plot=fig,
                           )
