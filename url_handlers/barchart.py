from flask import Blueprint, render_template, request, session

from medex.controller.helpers import get_filter_service
from medex.services.database import get_db_session
from modules.get_data_to_barchart import get_bar_chart
import plotly.express as px
from url_handlers.filtering import check_for_date_filter_post, check_for_limit_offset
from url_handlers.utility import _is_valid_entity
from webserver import all_measurement, measurement_name, block_measurement, start_date, end_date
import pandas as pd
import textwrap

barchart_page = Blueprint('barchart', __name__, template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    return render_template('barchart.html')


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():
    # get request values
    if block_measurement == 'none':
        measurement = [all_measurement[0]]
    else:
        measurement = request.form.getlist('measurement')
    group_by_entity = request.form.get('categorical_entities')
    categories = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = check_for_limit_offset()

    df = pd.DataFrame()
    # handling errors and load data from database
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif not _is_valid_entity(group_by_entity):
        error = "Please select 'group by' entity"
    elif not categories:
        error = "Please select subcategory"
    else:
        session_db = get_db_session()
        filter_service = get_filter_service()
        df, error = get_bar_chart([group_by_entity, categories], measurement, date_filter, limit_filter, filter_service,
                                  session_db)
    if error:
        return render_template('barchart.html',
                               measurement=measurement,
                               categorical_entities=group_by_entity,
                               subcategory_entities=categories,
                               how_to_plot=how_to_plot,
                               error=error
                               )

    df['%'] = 100 * df['count'] / df.groupby('measurement')['count'].transform('sum')
    legend = textwrap.wrap(group_by_entity, width=20)

    # Plot figure and convert to an HTML string representation
    if how_to_plot == 'count':
        y = 'count'
    else:
        y = '%'
    if block_measurement == 'none':
        fig = px.bar(df, x=group_by_entity, y=y, barmode='group', template="plotly_white")
    else:
        fig = px.bar(df, x='measurement', y=y, color=group_by_entity, barmode='group', template="plotly_white")

    fig.update_layout(font=dict(size=16),
                      legend_title='<br>'.join(legend),
                      title={'text': group_by_entity,
                             'x': 0.5,
                             'xanchor': 'center'})
    fig = fig.to_html()
    return render_template('barchart.html',
                           measurement=measurement,
                           categorical_entities=group_by_entity,
                           subcategory_entities=categories,
                           how_to_plot=how_to_plot,
                           plot=fig,
                           )
