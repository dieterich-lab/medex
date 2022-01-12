from flask import Blueprint, render_template, request,session
import plotly.express as px
import modules.load_data_postgre as ps
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, Name_ID, measurement_name, block, df_min_max, data
import pandas as pd
import textwrap

scatter_plot_page = Blueprint('scatter_plot', __name__, template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():
    start_date, end_date = filtering.date()
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    numerical_filter = filtering.check_for_numerical_filter_get()
    return render_template('scatter_plot.html',
                           start_date=start_date,
                           end_date=end_date,
                           measurement_filter=session.get('measurement_filter'),
                           filter=categorical_filter,
                           numerical_filter=numerical_filter)


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():
    # get filter
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter= filtering.check_for_filter_post()
    numerical_filter, numerical_filter_name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # show/hide selector for visits
    if block == 'none':
        x_measurement = all_measurement.values[0]
        y_measurement = all_measurement.values[0]
    else:
        x_measurement = request.form.get('x_measurement')
        y_measurement = request.form.get('y_measurement')

    # get selected entities
    add_group_by = request.form.get('add_group_by') is not None
    y_axis = request.form.get('y_axis')
    x_axis = request.form.get('x_axis')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    log_x = request.form.get('log_x')
    log_y = request.form.get('log_y')

    # handling errors and load data from database
    df = pd.DataFrame()
    if x_measurement == "Search entity" or y_axis == "Search entity":
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
                                        x_measurement, y_measurement, date, rdb)

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
                               df_min_max=df_min_max,
                               error=error,
                               )

    # Plot figure and convert to an HTML string representation
    df = filtering.checking_for_block(block, df, Name_ID, measurement_name)
    fig = {}
    if how_to_plot == 'linear':
        if add_group_by :
            df['hover_mouse'] = df[Name_ID]
            fig = px.scatter(df, x=x_axis, y=y_axis, color=categorical_entities,
                             hover_name='hover_mouse', template="plotly_white",trendline="ols")
        else:
            df['hover_mouse'] = df[Name_ID]
            fig = px.scatter(df, x=x_axis, y=y_axis,hover_name ='hover_mouse', template="plotly_white",
                             trendline="ols")

    else:
        if log_x == 'log_x' and log_y == 'log_y':
            if add_group_by:
                df['hover_mouse'] = df[Name_ID]
                fig = px.scatter(df, x=x_axis, y=y_axis, color=categorical_entities,
                                 hover_name='hover_mouse', template="plotly_white", trendline="ols", log_x=True,
                                 log_y=True)

            else:
                df['hover_mouse'] = df[Name_ID]
                fig = px.scatter(df, x=x_axis, y=y_axis, hover_name='hover_mouse', template="plotly_white",
                                 trendline="ols", log_x=True, log_y=True)
        elif log_x == 'log_x':
            if add_group_by:
                df['hover_mouse'] = df[Name_ID]
                fig = px.scatter(df, x=x_axis, y=y_axis, color=categorical_entities, hover_name='hover_mouse',
                                 template="plotly_white", trendline="ols", log_x=True)

            else:
                df['hover_mouse'] = df[Name_ID]
                fig = px.scatter(df, x=x_axis, y=y_axis, hover_name='hover_mouse', template="plotly_white",
                                 trendline="ols", log_x=True)
        elif log_y == 'log_y':
            if add_group_by:
                df['hover_mouse'] = df[Name_ID]
                fig = px.scatter(df, x=x_axis, y=y_axis, color=categorical_entities, hover_name='hover_mouse',
                                 template="plotly_white", trendline="ols",  log_y=True)

            else:
                df['hover_mouse'] = df[Name_ID]
                fig = px.scatter(df, x=x_axis, y=y_axis, hover_name='hover_mouse', template="plotly_white",
                                 trendline="ols", log_y=True)

    if block == 'none':
        fig.update_layout(
            font=dict(size=16),
            title={
                'text': "Compare values of <b>" + x_axis + "</b> and <b>" + y_axis,
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
    else:
        split_text = textwrap.wrap("Compare values of <b>" + x_axis + "</b> : " + measurement_name + " <b>" +
                                   x_measurement + "</b> and <b>" + y_axis + "</b> : " + measurement_name + " <b>" +
                                   y_measurement + "</b> ", width=100)
        xaxis = textwrap.wrap(x_axis + "</b> ")
        yaxis = textwrap.wrap(y_axis, width=40)
        legend = textwrap.wrap(categorical_entities, width=20)
        fig.update_layout(
            height=600,
            legend_title='<br>'.join(legend),
            font=dict(size=16),
            xaxis_title='<br>'.join(xaxis),
            yaxis_title='<br>'.join(yaxis),
            title={
                'text': '<br>'.join(split_text),
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})

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
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max,
                           plot=fig
                           )


















