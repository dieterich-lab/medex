from flask import Blueprint, render_template, request, session

from medex.controller.helpers import get_session_id
from modules.get_data_to_histogrm import get_histogram_box_plot
import plotly.express as px
import plotly.graph_objects as go
from url_handlers.filtering import check_for_date_filter_post, check_for_limit_offset
from webserver import block_measurement, all_measurement, factory, start_date, end_date
import pandas as pd
import textwrap


boxplot_page = Blueprint('boxplot', __name__, template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():
    return render_template('boxplot.html')


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():
    
    # get request values
    if block_measurement == 'none':
        measurement = [all_measurement[0]]
    else:
        measurement = request.form.getlist('measurement')
    entities = (request.form.get('numeric_entities'), request.form.get('categorical_entities'),
                request.form.getlist('subcategory_entities'))
    how_to_plot = request.form.get('how_to_plot')

    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = check_for_limit_offset()
    update_filter = session.get('filtering')

    # handling errors and load data from database
    df = pd.DataFrame()
    if measurement == "Search entity":
        error = "Please select number of measurement"
    elif entities[0] == "Search entity" or entities[1] == "Search entity":
        error = "Please select entity"
    elif not entities[2]:
        error = "Please select subcategory"
    else:
        session_db = factory.get_session(get_session_id())
        df, error = get_histogram_box_plot(entities, measurement, date_filter, limit_filter, update_filter, session_db)

    if error:
        return render_template('boxplot.html',
                               error=error,
                               how_to_plot=how_to_plot,
                               measurement=measurement,
                               numeric_entities=entities[0],
                               categorical_entities=entities[1],
                               subcategory_entities=entities[2])

    # Plot figure and convert to an HTML string representation
    if block_measurement == 'none':
        table = df.groupby([entities[1]]).size().reset_index(name='counts')
        fig_table = go.Figure(data=[go.Table(header=dict(values=list(table[entities[1]].values)),
                                             cells=dict(values=table['counts'].transpose().values.tolist()))])
        if how_to_plot == 'linear':
            fig = px.box(df, x=entities[1], y=entities[0], color=entities[1],
                         template="plotly_white")
        else:
            fig = px.box(df, x=entities[1], y=entities[0], color=entities[1],
                         template="plotly_white", log_y=True)
    else:
        table = df.groupby(['measurement', entities[1]]).size().reset_index(name='counts')
        table = table.pivot(index='measurement', columns=entities[1], values='counts').reset_index()
        fig_table = go.Figure(data=[go.Table(header=dict(values=list(table.columns)),
                                             cells=dict(values=table.transpose().values.tolist()))
                                    ])
        if how_to_plot == 'linear':
            fig = px.box(df, x='measurement', y=entities[0], color=entities[1],
                         template="plotly_white")
        else:
            fig = px.box(df, x='measurement', y=entities[0], color=entities[1],
                         template="plotly_white", log_y=True)

    legend = textwrap.wrap(entities[1], width=20)
    fig.update_layout(font=dict(size=16),
                      legend_title='<br>'.join(legend),
                      title={
                          'text': '<b>' + entities[0] + '</b> by <b>' + entities[1] + '</b>',
                          'x': 0.5,
                          'xanchor': 'center', }
                      )
    height = 30 + len(table) * 30
    fig_table.update_layout(height=height, margin=dict(r=5, l=5, t=5, b=5))
    fig_table = fig_table.to_html()
    fig = fig.to_html()

    return render_template('boxplot.html',
                           measurement=measurement,
                           numeric_entities=entities[0],
                           categorical_entities=entities[1],
                           subcategory_entities=entities[2],
                           how_to_plot=how_to_plot,
                           table=fig_table,
                           plot=fig)
