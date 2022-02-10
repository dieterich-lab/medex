from flask import Blueprint, render_template, request, session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, measurement_name, Name_ID, block, df_min_max, data
import pandas as pd
import textwrap
import time

barchart_page = Blueprint('barchart', __name__, template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    return render_template('barchart.html')


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():

    # get filters
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
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
    update = request.form.get('update')
    measurement = request.form.getlist('measurement')
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
        ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1, measurement_filter, update_list,rdb)
        return render_template('barchart.html',
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
                               measurement=measurement,
                               df_min_max=df_min_max,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               how_to_plot=how_to_plot,
                               )

    update = data.update_filter
    df = pd.DataFrame()
    # handling errors and load data from database
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        df, error = ps.get_bar_chart(categorical_entities, subcategory_entities, measurement, date, limit_selected, limit, offset, update, rdb)
    if error:
        return render_template('barchart.html',
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               measurement_filter=measurement_filter,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               measurement=measurement,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               how_to_plot=how_to_plot,
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               error=error
                               )

    start_time = time.time()
    df['%'] = 100*df['count']/df.groupby('measurement')['count'].transform('sum')
    legend = textwrap.wrap(categorical_entities, width=20)
    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'count':
            fig = px.bar(df, x=categorical_entities, y="count", barmode='group', template="plotly_white")
        else:
            fig = px.bar(df, x=categorical_entities, y="%", barmode='group', template="plotly_white")
    else:
        if how_to_plot == 'count':
            fig = px.bar(df, x='measurement', y="count", color=categorical_entities, barmode='group',
                         template="plotly_white")
        else:
            fig = px.bar(df, x='measurement', y="%", color=categorical_entities, barmode='group',
                         template="plotly_white")

    fig.update_layout(font=dict(size=16),
                      legend_title='<br>'.join(legend),
                      title={'text' : categorical_entities,
                             'x': 0.5,
                             'xanchor': 'center'})
    fig = fig.to_html()
    print("--- %s seconds data ---" % (time.time() - start_time))
    return render_template('barchart.html',
                           measurement=measurement,
                           measurement_filter=measurement_filter,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           categorical_filter=categorical_names,
                           numerical_filter_name=name,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           how_to_plot=how_to_plot,
                           val=update,
                           limit_yes=data.limit_selected,
                           limit=data.limit,
                           offset=data.offset,
                           plot=fig,
                           )
