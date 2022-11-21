from flask import Blueprint, render_template, request, session

from medex.controller.helpers import get_filter_service
from medex.services.database import get_db_session
from modules.get_data_to_scatter_plot import get_scatter_plot
from webserver import all_measurement, measurement_name, block_measurement, start_date, end_date
from url_handlers.filtering import check_for_date_filter_post, check_for_limit_offset
import pandas as pd
import textwrap
import plotly.graph_objects as go

scatter_plot_page = Blueprint('scatter_plot', __name__, template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():
    return render_template('scatter_plot.html')


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():
    filter_service = get_filter_service()
    # get request values
    if block_measurement == 'none':
        measurement = (all_measurement[0], all_measurement[0])
    else:
        measurement = (request.form.get('x_measurement'), request.form.get('y_measurement'))

    add_group_by = request.form.get('add_group_by') is not None
    axis = (str(request.form.get('x_axis')), str(request.form.get('y_axis')))
    categorical_entities = (request.form.get('categorical_entities'), request.form.getlist('subcategory_entities'))
    how_to_plot = request.form.get('how_to_plot')
    log = (request.form.get('log_x'), request.form.get('log_y'))

    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = check_for_limit_offset()

    # handling errors and load data from database
    df = pd.DataFrame()
    if measurement[0] == "Search entity" or measurement[1] == "Search entity":
        error = "Please select number of {}".format(measurement_name)
    elif axis[0] == "Search entity" or axis[1] == "Search entity":
        error = "Please select x_axis and y_axis"
    elif axis[0] == axis[1] and measurement[0] == measurement[1]:
        error = "You can't compare the same entity"
    elif how_to_plot == 'log' and not log[0] and not log[1]:
        error = "Please select type of log"
    elif add_group_by and categorical_entities[0] == "Search entity":
        error = "Please select a categorical value to group by"
    elif not categorical_entities[1] and add_group_by:
        error = "Please select subcategory"
    else:
        session_db = get_db_session()
        df, error = get_scatter_plot(add_group_by, axis, measurement, categorical_entities, date_filter, limit_filter,
                                     filter_service, session_db)

    if error:
        return render_template('scatter_plot.html',
                               categorical_entities=categorical_entities[0],
                               subcategory=categorical_entities[1],
                               add_group_by=add_group_by,
                               x_axis=axis[0],
                               y_axis=axis[1],
                               x_measurement=measurement[0],
                               y_measurement=measurement[1],
                               error=error)

    # Plot figure and convert to an HTML string representation
    number_of_points = len(df.index)
    x_axis, y_axis = axis[0] + '_' + measurement[0], axis[1] + '_' + measurement[1]

    # create figure
    fig = go.Figure()
    if add_group_by:
        for i in categorical_entities[1]:
            df_new = df[df[categorical_entities[0]] == i]
            fig.add_trace(go.Scattergl(x=df_new[x_axis], y=df_new[y_axis], mode='markers', name=i))
    else:
        fig.add_trace(
            go.Scattergl(x=df[x_axis], y=df[y_axis], mode='markers', marker=dict(line=dict(width=1,
                                                                                           color='DarkSlateGrey'))))
    # title for figure
    if block_measurement == 'none':
        x_axis, y_axis = axis[0], axis[1]
        split_text = textwrap.wrap("Compare values of <b>" + axis[0] + "</b> and <b>" + axis[1] +
                                   "<br> Number of Points: " + str(number_of_points))

    else:
        split_text = textwrap.wrap("Compare values of <b>" + axis[0] + "</b> : " + measurement_name + " <b>" +
                                   measurement[0] + "</b> and <b>" + axis[1] + "</b> : " + measurement_name + " <b>" +
                                   measurement[1] + "</b>" + "<br> Number of Points: " + str(number_of_points),
                                   width=100)

    x_axis = textwrap.wrap(x_axis)
    y_axis = textwrap.wrap(y_axis, width=40)
    legend = textwrap.wrap(categorical_entities[0], width=20)

    fig.update_layout(
        template="plotly_white",
        legend_title='<br>'.join(legend),
        font=dict(size=16),
        xaxis_title='<br>'.join(x_axis),
        yaxis_title='<br>'.join(y_axis),
        title={'text': '<br>'.join(split_text), 'x': 0.5, 'xanchor': 'center', })

    if log[0] == 'log_x':
        fig.update_xaxes(type="log")
    if log[1] == 'log_y':
        fig.update_yaxes(type="log")

    fig = fig.to_html()
    return render_template('scatter_plot.html',
                           categorical_entities=categorical_entities[0],
                           subcategory=categorical_entities[1],
                           add_group_by=add_group_by,
                           x_axis=axis[0],
                           y_axis=axis[1],
                           x_measurement=measurement[0],
                           y_measurement=measurement[1],
                           log=log,
                           how_to_plot=how_to_plot,
                           plot=fig)
