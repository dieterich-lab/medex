from flask import Blueprint, render_template, request, jsonify, session
from flask import Markup
import numpy as np
import plotly.express as px
import pandas as pd
import modules.load_data_postgre as ps



scatter_plot_page = Blueprint('scatter_plot', __name__,
                       template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():
    from webserver import all_numeric_entities,all_categorical_entities

    return render_template('scatter_plot.html',
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               all_categorical_entities=all_categorical_entities)


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():
    # connection with database and load name of entities
    from webserver import rdb,all_numeric_entities,all_categorical_entities


    # list selected data
    y_axis = request.form.get('y_axis')
    x_axis = request.form.get('x_axis')
    category = request.form.get('category')
    how_to_plot = request.form.get('how_to_plot')
    add_group_by = request.form.get('add_group_by') is not None


    # handling errors and load data from database
    error = None
    if not x_axis or not y_axis or x_axis == "Search entity" or y_axis == "Search entity":
        error = "Please select x_axis and y_axis"
    elif x_axis == y_axis:
        error = "You can't compare the same entity"
    else :
        numeric_df = ps.get_values([x_axis, y_axis], rdb).dropna() if not error else (None, error)
        if len(numeric_df[x_axis]) == 0:
            error = "Category {} is empty".format(x_axis)
        elif len(numeric_df[y_axis]) == 0:
            error = "Category {} is empty".format(y_axis)
        elif len(numeric_df.index) == 0:
            error = "This two entities don't have common values"
        elif add_group_by and category == "Search entity":
            error = "Please select a categorical value to group by"
        elif add_group_by and category:
            numerical_df = ps.get_values([x_axis, y_axis], rdb) if not error else (None, error)
            df = ps.get_cat_values([category], rdb) if not error else (None, error)
            categorical_df = numerical_df.merge(df, on ="Patient_ID").dropna()
            if len(categorical_df[category]) == 0:
                error = "Category {} is empty".format(category)



    if error:
        return render_template('scatter_plot.html',
                                error=error,
                                numeric_tab=True,
                                x_axis=x_axis,
                                y_axis=y_axis,
                                category=category,
                                all_numeric_entities=all_numeric_entities,
                                all_categorical_entities=all_categorical_entities,
                                add_group_by=add_group_by)

    if how_to_plot == 'linear':
        if add_group_by :
            fig = px.scatter(categorical_df, x=x_axis, y=y_axis,color = category, hover_name='Patient_ID', template="plotly_white",
                                 trendline="ols")


        else:
            numeric_df = numeric_df[['Patient_ID',x_axis, y_axis]]
            fig = px.scatter(numeric_df,x=x_axis, y=y_axis,hover_name = 'Patient_ID', template = "plotly_white",trendline="ols")

    else:
        if add_group_by:
            fig = px.scatter(categorical_df, x=x_axis, y=y_axis, color=category, hover_name='Patient_ID',
                             template="plotly_white",trendline="ols",log_x=True, log_y=True)


        else:
            numeric_df = numeric_df[['Patient_ID', x_axis, y_axis]]
            fig = px.scatter(numeric_df, x=x_axis, y=y_axis, hover_name='Patient_ID', template="plotly_white",
                             trendline="ols",log_x=True, log_y=True)


    fig.update_layout(
        title={
            'text': "Compare values of <b>" + x_axis + "</b> and <b>" + y_axis + "</b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig = fig.to_html()
    return render_template('scatter_plot.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities,
                           plot= fig,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           category=category,
                           add_group_by=add_group_by)


















