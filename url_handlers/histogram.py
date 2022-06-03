from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, Name_ID, measurement_name, block_measurement, df_min_max, data
import pandas as pd
import textwrap
import time

histogram_page = Blueprint('histogram', __name__, template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    number_of_bins = 20
    return render_template('histogram.html',
                           number_of_bins=number_of_bins)


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():
    # get filters
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = session.get('case_ids')
    categorical_filter, categorical_names, categorical_filter_zip, = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    limit_selected = request.form.get('limit_yes')
    data.limit_selected = limit_selected
    limit = request.form.get('limit')
    offset = request.form.get('offset')
    data.limit = limit
    data.offset = offset

    # get request values
    add = request.form.get('Add')
    clean = request.form.get('clean')
    if block == 'none':
        measurement = all_measurement[0]
    else:
        measurement = request.form.getlist('measurement')
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')

    if clean is not None or add is not None:
        if add is not None:
            update_list = list(add.split(","))
            update = add
        elif clean is not None:
            update = '0,0'
            update_list = list(update.split(","))

        data.update_filter = update
        ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1, update_list,rdb)
        return render_template('histogram.html',
                               number_of_bins=number_of_bins,
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               start_date=start_date,
                               end_date=end_date,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               filter=categorical_filter_zip,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               measurement=measurement,
                               df_min_max=df_min_max,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               )

    # handling errors and load data from database
    update = data.update_filter + ',' + case_ids
    df = pd.DataFrame()
    if measurement == "Search entity":
        error = "Please select number of {}".format(measurement_name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        df, error = ps.get_histogram_box_plot(numeric_entities, categorical_entities, subcategory_entities, measurement,
                                              date, limit_selected, limit, offset, update, rdb)
        df = filtering.checking_for_block(block, df, Name_ID, measurement_name)

    if error:
        return render_template('histogram.html',
                               number_of_bins=number_of_bins,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement=measurement,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               df_min_max=df_min_max,
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
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
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               df_min_max=df_min_max,
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
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
            'text': '<b>' + numeric_entities + '</b> by <b>' + categorical_entities + '</b>',
            'x': 0.5,
            'xanchor': 'center'})
    fig = fig.to_html()
    return render_template('histogram.html',
                           number_of_bins=number_of_bins,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement=measurement,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           categorical_filter=categorical_names,
                           numerical_filter_name=name,
                           df_min_max=df_min_max,
                           val=update,
                           limit_yes=data.limit_selected,
                           limit=data.limit,
                           offset=data.offset,
                           plot=fig,
                           )
