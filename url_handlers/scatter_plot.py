from flask import Blueprint, render_template, request,session
import plotly.express as px
import modules.load_data_postgre as ps
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, Name_ID, measurement_name, block, df_min_max, data
import pandas as pd
import textwrap
import plotly.graph_objects as go
import numpy as np
import time


scatter_plot_page = Blueprint('scatter_plot', __name__, template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():
    return render_template('scatter_plot.html')


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():
    # get filter
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter= filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter
    limit_selected = request.form.get('limit_yes')
    data.limit_selected = limit_selected
    limit = request.form.get('limit')
    offset = request.form.get('offset')
    data.limit = limit
    data.offset = offset

    # get request values
    add = request.form.get('Add')
    clean = request.form.get('clean')
    x_measurement = request.form.get('x_measurement')
    y_measurement = request.form.get('y_measurement')
    add_group_by = request.form.get('add_group_by') is not None
    y_axis = request.form.get('y_axis')
    x_axis = request.form.get('x_axis')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    log_x = request.form.get('log_x')
    log_y = request.form.get('log_y')

    if clean is not None or add is not None:
        if add is not None:
            update_list = list(add.split(","))
            update = add
        elif clean is not None:
            update = '0,0'
            update_list = list(update.split(","))
        data.update_filter = update
        ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1, measurement_filter, update_list,rdb)
        return render_template('scatter_plot.html',
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               filter=categorical_filter_zip,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               df_min_max=df_min_max,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               add_group_by=add_group_by,
                               x_axis=x_axis,
                               y_axis=y_axis,
                               x_measurement=x_measurement,
                               y_measurement=y_measurement,
                               )

    # handling errors and load data from database
    update = data.update_filter
    df = pd.DataFrame()
    if x_measurement == "Search entity" or y_measurement == "Search entity":
        error = "Please select number of {}".format(measurement_name)
    elif x_axis == "Search entity" or y_axis == "Search entity":
        error = "Please select x_axis and y_axis"
    elif x_axis == y_axis and x_measurement == y_measurement:
        error = "You can't compare the same entity"
    elif how_to_plot == 'log' and not log_x and not log_y:
        error = "Please select type of log"
    elif add_group_by and categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities and add_group_by:
        error = "Please select subcategory"
    else:

        df, error = ps.get_scatter_plot(add_group_by, categorical_entities, subcategory_entities, x_axis, y_axis,
                                        x_measurement, y_measurement, date, limit_selected, limit, offset, update, rdb)

    if error:
        return render_template('scatter_plot.html',
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               add_group_by=add_group_by,
                               x_axis=x_axis,
                               y_axis=y_axis,
                               x_measurement=x_measurement,
                               y_measurement=y_measurement,
                               measurement_filter=measurement_filter,
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
                               error=error,
                               )

    # Plot figure and convert to an HTML string representation
    start_time = time.time()
    df = filtering.checking_for_block(block, df, Name_ID, measurement_name)
    x_axis_m = x_axis + '_' + x_measurement
    y_axis_m = y_axis + '_' + y_measurement

    fig = go.Figure()
    if add_group_by:
        for i in subcategory_entities:
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
                y =df[y_axis_m],
                mode='markers',
                marker=dict(
                    line=dict(
                        width=1,
                        color='DarkSlateGrey')
                )
            )
        )
    if block == 'none':
        fig.update_layout(
            font=dict(size=16),
            title={
                'text': "Compare values of <b>" + x_axis + "</b> and <b>" + y_axis,
                'x': 0.5,
                'xanchor': 'center', })
    else:
        split_text = textwrap.wrap("Compare values of <b>" + x_axis + "</b> : " + measurement_name + " <b>" +
                                   x_measurement + "</b> and <b>" + y_axis + "</b> : " + measurement_name + " <b>" +
                                   y_measurement + "</b> ", width=100)
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
    if log_x == 'log_x':
        fig.update_xaxes(type="log")
    if log_y == 'log_y':
        fig.update_yaxes(type="log")

    fig = fig.to_html()
    return render_template('scatter_plot.html',
                           subcategory_entities=subcategory_entities,
                           categorical_entities=categorical_entities,
                           add_group_by=add_group_by,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           log_x=log_x,
                           log_y=log_y,
                           how_to_plot=how_to_plot,
                           x_measurement=x_measurement,
                           y_measurement=y_measurement,
                           measurement_filter=measurement_filter,
                           categorical_filter=categorical_names,
                           numerical_filter_name=name,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max,
                           val=update,
                           limit_yes=data.limit_selected,
                           limit=data.limit,
                           offset=data.offset,
                           plot=fig
                           )


















