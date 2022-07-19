from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
from url_handlers.filtering import check_for_date_filter_post, check_for_limit_offset
from webserver import all_measurement, measurement_name, block_measurement, factory, start_date, end_date
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
        measurement = all_measurement[0]
    else:
        measurement = request.form.getlist('measurement')
    categorical_entities = (request.form.get('categorical_entities'), request.form.getlist('subcategory_entities'))
    how_to_plot = request.form.get('how_to_plot')

    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = check_for_limit_offset()
    update_filter = session.get('filtering')

    df = pd.DataFrame()
    # handling errors and load data from database
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif categorical_entities[0] == "Search entity":
        error = "Please select a categorical value to group by"
    elif not categorical_entities[1]:
        error = "Please select subcategory"
    else:
        session_db = factory.get_session(session.get('session_id'))
        df, error = ps.get_bar_chart(categorical_entities, measurement, date_filter, limit_filter, update_filter,
                                     session_db)
    if error:
        return render_template('barchart.html',
                               measurement=measurement,
                               categorical_entities=categorical_entities[0],
                               subcategory_entities=categorical_entities[1],
                               how_to_plot=how_to_plot,
                               error=error
                               )

    df['%'] = 100 * df['count'] / df.groupby('measurement')['count'].transform('sum')
    legend = textwrap.wrap(categorical_entities[0], width=20)

    # Plot figure and convert to an HTML string representation
    if how_to_plot == 'count':
        y = 'count'
    else:
        y = '%'
    if block_measurement == 'none':
        fig = px.bar(df, x=categorical_entities[0], y=y, barmode='group', template="plotly_white")
    else:
        fig = px.bar(df, x='measurement', y=y, color=categorical_entities[0], barmode='group', template="plotly_white")

    fig.update_layout(font=dict(size=16),
                      legend_title='<br>'.join(legend),
                      title={'text': categorical_entities[0],
                             'x': 0.5,
                             'xanchor': 'center'})
    fig = fig.to_html()
    return render_template('barchart.html',
                           measurement=measurement,
                           categorical_entities=categorical_entities[0],
                           subcategory_entities=categorical_entities[1],
                           how_to_plot=how_to_plot,
                           plot=fig,
                           )
