from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, measurement_name, Name_ID, block, df_min_max, data
import pandas as pd
import textwrap

barchart_page = Blueprint('barchart', __name__, template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    return render_template('barchart.html')


@barchart_page.route('/barchart', methods=['POST'])
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
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    df = pd.DataFrame()
    # handling errors and load data from database
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        # select data from database
        df_filtering = ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1,
                                    measurement_filter, rdb)
        data.Name_ID_filter = df_filtering
        filter = data.Name_ID_filter
        df, error = ps.get_bar_chart(categorical_entities, subcategory_entities, measurement, date, filter, rdb)
    if error:
        return render_template('barchart.html',
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               measurement=measurement,
                               measurement_filter=measurement_filter,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               how_to_plot=how_to_plot,
                               error=error
                               )

    df['%'] = 100*df['count']/df.groupby('measurement')['count'].transform('sum')
    legend = textwrap.wrap(categorical_entities, width=20)
    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'count':
            fig = px.bar(df, x=categorical_entities, y="count", barmode='group', template="plotly_white")
        else:
            fig = px.bar(df, x=categorical_entities, y="%", barmode='group', template="plotly_white")
    else:
        if how_to_plot == 'count':
            fig = px.bar(df, x='measurement', y="count", color=categorical_entities, barmode='group',
                         template="plotly_white")
        else:
            fig = px.bar(df, x='measurement', y="%", color=categorical_entities, barmode='group',
                         template="plotly_white")

    fig.update_layout(font=dict(size=16),
                      legend_title='<br>'.join(legend),)
    fig = fig.to_html()

    return render_template('barchart.html',
                           measurement=measurement,
                           measurement_filter=measurement_filter,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           how_to_plot=how_to_plot,
                           plot=fig,
                           )
