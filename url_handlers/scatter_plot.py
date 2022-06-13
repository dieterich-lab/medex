from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
from webserver import all_measurement, measurement_name, block_measurement,session_db
import pandas as pd
import textwrap
import plotly.graph_objects as go

scatter_plot_page = Blueprint('scatter_plot', __name__, template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():
    return render_template('scatter_plot.html')


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():

    # get request values
    if block_measurement == 'none':
        measurement = (all_measurement[0], all_measurement[0])
    else:
        measurement = (request.form.get('x_measurement'), request.form.get('y_measurement'))

    add_group_by = request.form.get('add_group_by') is not None
    axis = (str(request.form.get('x_axis')), str(request.form.get('y_axis')))
    cc = (request.form.get("id_numerical_filter"),request.form.get("id_numerical_filter"))
    print(cc)
    x_axis, y_axis = request.form.get('x_axis'), request.form.get('y_axis')
    axis = (x_axis, y_axis)
    print(axis)
    categorical_entities = (request.form.get('categorical_entities'), request.form.getlist('subcategory_entities'))
    how_to_plot = request.form.get('how_to_plot')
    log = (request.form.get('log_x'), request.form.get('log_y'))

    # get_filter
    date_filter = session.get('date_filter')
    limit_filter = session.get('limit_offset')
    update_filter = session.get('filter_update')
    print(update_filter)

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
        print(add_group_by, axis, measurement, categorical_entities, date_filter,
        limit_filter, update_filter)
        df, error = ps.get_scatter_plot(add_group_by, axis, measurement, categorical_entities, date_filter,
                                        limit_filter, update_filter, session_db)
    if error:
        return render_template('scatter_plot.html',
                               categorical_entities=categorical_entities,
                               add_group_by=add_group_by,
                               axis=axis,
                               measurement=measurement,
                               error=error)

    # Plot figure and convert to an HTML string representation
    x_axis_m = axis[0] + '_' + measurement[0]
    y_axis_m = axis[1] + '_' + measurement[1]
    number_of_points = len(df.index)
    fig = go.Figure()
    if add_group_by:
        for i in categorical_entities[1]:
            dfu = df[df[categorical_entities] == i]
            x = dfu[x_axis_m]
            y = dfu[y_axis_m]
            fig.add_trace(
                go.Scattergl(
                    x=x,
                    y=y,
                    mode='markers',
                    name=i,
                )
            )
    else:
        fig.add_trace(
            go.Scattergl(
                x=df[x_axis_m],
                y=df[y_axis_m],
                mode='markers',
                marker=dict(
                    line=dict(
                        width=1,
                        color='DarkSlateGrey')
                )
            )
        )
    if block_measurement == 'none':
        split_text = textwrap.wrap("Compare values of <b>" + axis[0] + "</b> and <b>" + axis[1] +
                                   "<br> Number of Points: " + str(number_of_points))

    else:
        split_text = textwrap.wrap("Compare values of <b>" + axis[0] + "</b> : " + measurement_name + " <b>" +
                                   measurement[0] + "</b> and <b>" + axis[1] + "</b> : " + measurement_name + " <b>" +
                                   measurement[1] + "</b>" + "<br> Number of Points: " + str(number_of_points),
                                   width=100)
    xaxis = textwrap.wrap(x_axis_m)
    yaxis = textwrap.wrap(y_axis_m, width=40)
    legend = textwrap.wrap(categorical_entities, width=20)

    fig.update_layout(
        template="plotly_white",
        legend_title='<br>'.join(legend),
        font=dict(size=16),
        xaxis_title='<br>'.join(xaxis),
        yaxis_title='<br>'.join(yaxis),
        title={
            'text': '<br>'.join(split_text),
            'x': 0.5,
            'xanchor': 'center', })
    if log[0] == 'log_x':
        fig.update_xaxes(type="log")
    if log[1] == 'log_y':
        fig.update_yaxes(type="log")

    fig = fig.to_html()
    return render_template('scatter_plot.html',
                           categorical_entities=categorical_entities,
                           add_group_by=add_group_by,
                           axis=axis,
                           log=log,
                           how_to_plot=how_to_plot,
                           measurement=measurement,
                           plot=fig
                           )
