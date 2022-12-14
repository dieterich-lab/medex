from flask import Blueprint, render_template, request, session

from medex.controller.helpers import get_filter_service
from medex.services.database import get_db_session
from modules.get_data_to_histogrm import get_histogram_box_plot
import plotly.express as px
import plotly.graph_objects as go
from url_handlers.filtering import check_for_date_filter_post, check_for_limit_offset
from url_handlers.utility import _is_valid_entity
from webserver import block_measurement, all_measurement, start_date, end_date
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
    numerical_entity = request.form.get('numeric_entities')
    group_by_entity = request.form.get('categorical_entities')
    categories = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = check_for_limit_offset()

    # handling errors and load data from database
    df = pd.DataFrame()
    if not measurement:
        error = "Please select number of visit"
    elif not _is_valid_entity(numerical_entity):
        error = "Please select numerical entity"
    elif not _is_valid_entity(group_by_entity):
        error = "Please select 'group by' entity"
    elif not categories:
        error = "Please select subcategory"
    else:
        session_db = get_db_session()
        filter_service = get_filter_service()
        df, error = get_histogram_box_plot([numerical_entity, group_by_entity, categories], measurement, date_filter,
                                           limit_filter, filter_service, session_db)

    if error:
        return render_template('boxplot.html',
                               error=error,
                               how_to_plot=how_to_plot,
                               measurement=measurement,
                               numeric_entities=numerical_entity,
                               categorical_entities=group_by_entity,
                               subcategory_entities=categories)

    # Plot figure and convert to an HTML string representation
    if block_measurement == 'none':
        table = df.groupby([group_by_entity]).size().reset_index(name='counts')
        fig_table = go.Figure(data=[go.Table(header=dict(values=list(table[group_by_entity].values)),
                                             cells=dict(values=table['counts'].transpose().values.tolist()))])
        if how_to_plot == 'linear':
            fig = px.box(df, x=group_by_entity, y=numerical_entity, color=group_by_entity,
                         template="plotly_white")
        else:
            fig = px.box(df, x=group_by_entity, y=numerical_entity, color=group_by_entity,
                         template="plotly_white", log_y=True)
    else:
        table = df.groupby(['measurement', group_by_entity]).size().reset_index(name='counts')
        table = table.pivot(index='measurement', columns=group_by_entity, values='counts').reset_index()
        fig_table = go.Figure(data=[go.Table(header=dict(values=list(table.columns)),
                                             cells=dict(values=table.transpose().values.tolist()))
                                    ])
        if how_to_plot == 'linear':
            fig = px.box(df, x='measurement', y=numerical_entity, color=group_by_entity,
                         template="plotly_white")
        else:
            fig = px.box(df, x='measurement', y=numerical_entity, color=group_by_entity,
                         template="plotly_white", log_y=True)

    legend = textwrap.wrap(group_by_entity, width=20)
    fig.update_layout(font=dict(size=16),
                      legend_title='<br>'.join(legend),
                      title={
                          'text': '<b>' + numerical_entity + '</b> by <b>' + group_by_entity + '</b>',
                          'x': 0.5,
                          'xanchor': 'center', }
                      )
    height = 30 + len(table) * 30
    fig_table.update_layout(height=height, margin=dict(r=5, l=5, t=5, b=5))
    fig_table = fig_table.to_html()
    fig = fig.to_html()

    return render_template('boxplot.html',
                           measurement=measurement,
                           numeric_entities=numerical_entity,
                           categorical_entities=group_by_entity,
                           subcategory_entities=categories,
                           how_to_plot=how_to_plot,
                           table=fig_table,
                           plot=fig)
