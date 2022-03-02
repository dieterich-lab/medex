from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, df_min_max, data, block, Name_ID, all_measurement, measurement_name
import pandas as pd
import textwrap
import time

boxplot_page = Blueprint('boxplot', __name__,template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():
    return render_template('boxplot.html')


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():

    # get filters
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = session.get('case_ids')
    categorical_filter, categorical_names, categorical_filter_zip, = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    limit_selected = request.form.get('limit_yes')
    data.limit_selected = limit_selected
    limit = request.form.get('limit')
    offset = request.form.get('offset')
    data.limit = limit
    data.offset = offset

    # get request values
    add = request.form.get('Add')
    clean = request.form.get('clean')
    if block == 'none':
        measurement = all_measurement[0]
    else:
        measurement = request.form.getlist('measurement')
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    if clean is not None or add is not None:
        if add is not None:
            update_list = list(add.split(","))
            update = add
        elif clean is not None:
            update = '0,0'
            update_list = list(update.split(","))
        data.update_filter = update
        ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1, update_list,rdb)
        return render_template('boxplot.html',
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               start_date=start_date,
                               end_date=end_date,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               filter=categorical_filter_zip,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               measurement=measurement,
                               df_min_max=df_min_max,
                               how_to_plot=how_to_plot,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               )

    # handling errors and load data from database
    update = data.update_filter + ',' + case_ids
    df = pd.DataFrame()
    if measurement == "Search entity":
        error = "Please select number of measurement"
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        df, error = ps.get_histogram_box_plot(numeric_entities, categorical_entities, subcategory_entities, measurement,
                                              date, limit_selected, limit, offset, update, rdb)
        df = filtering.checking_for_block(block, df, Name_ID, measurement_name)

    if error:
        return render_template('boxplot.html',
                               error=error,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement=measurement,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               how_to_plot=how_to_plot,
                               df_min_max=df_min_max,
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               )

    # Plot figure and convert to an HTML string representation
    if block == 'none':
        table = df.groupby([categorical_entities]).size().reset_index(name='counts')
        print(table)
    else:
        table = df.groupby([measurement_name,categorical_entities]).size().reset_index(name='counts')
        table = table.pivot(index=measurement_name, columns = categorical_entities,values='counts').reset_index()

    import plotly.graph_objects as go

    fig_table = go.Figure(data=[go.Table(header=dict(values=list(table[categorical_entities].values)),
                                   cells=dict(values=table['counts'].transpose().values.tolist()))
                          ])

    #len()
    if block == 'none':
        if how_to_plot == 'linear':
            fig = px.box(df, x=categorical_entities, y=numeric_entities, color=categorical_entities,
                         template="plotly_white")
        else:
            fig = px.box(df, x=categorical_entities, y=numeric_entities, color=categorical_entities,
                         template="plotly_white", log_y=True)
    else:
        if how_to_plot == 'linear':
            fig = px.box(df, x=measurement_name, y=numeric_entities, color=categorical_entities,
                         template="plotly_white")
        else:
            fig = px.box(df, x=measurement_name, y=numeric_entities, color=categorical_entities,
                         template="plotly_white", log_y=True)

    legend = textwrap.wrap(categorical_entities, width=20)
    fig.update_layout(font=dict(size=16),
                      legend_title='<br>'.join(legend),
                      title={
                          'text': '<b>' + numeric_entities + '</b> by <b>' + categorical_entities + '</b>',
                          'x': 0.5,
                          'xanchor': 'center', }
                      )
    height = 30 + len(table) * 30
    fig_table.update_layout(height=height, margin=dict(r=5, l=5, t=5, b=5))
    fig_table = fig_table.to_html()
    fig = fig.to_html()

    return render_template('boxplot.html',
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement=measurement,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           categorical_filter=categorical_names,
                           numerical_filter_name=name,
                           how_to_plot=how_to_plot,
                           df_min_max=df_min_max,
                           val=update,
                           limit_yes=data.limit_selected,
                           limit=data.limit,
                           offset=data.offset,
                           table=fig_table,
                           plot=fig)
