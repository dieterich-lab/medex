from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb, all_categorical_entities_sc, all_measurement, len_numeric, size_categorical, size_numeric,\
    len_categorical, all_subcategory_entities, database, measurement_name, Name_ID, block, data

barchart_page = Blueprint('barchart', __name__, template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    # get filter from data store
    categorical_filter = data.categorical_filter
    categorical_names = data.categorical_names
    number_filter = 0
    if categorical_filter:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)
    return render_template('barchart.html',
                           numeric_tab=True,
                           block=block,
                           name='{}'.format(measurement_name),
                           all_categorical_entities=all_categorical_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           filter=categorical_filter,
                           number_filter=number_filter,
                           )


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():

    id_filter = data.id_filter
    # get data from  html form
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')
    if 'example1' in request.form:
        categorical_entities = 'Podocyte.Enriched.Transcript'
        subcategory_entities = all_subcategory_entities[categorical_entities]
    else:
        categorical_entities = request.form.get('categorical_entities')
        subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    if 'filter' in request.form or 'all_categorical_filter' in request.form:
        categorical_filter = request.form.getlist('filter')
        categorical_names = request.form.getlist('cat')
        data.categorical_filter = categorical_filter
        data.categorical_names = categorical_names

    categorical_filter = data.categorical_filter
    categorical_names = data.categorical_names
    number_filter = 0
    # handling errors and load data from database
    categorical_df = []
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        categorical_df, error = ps.get_cat_values_barchart(categorical_entities, subcategory_entities, measurement,
                                                           categorical_filter, categorical_names, id_filter, rdb)
        categorical_df = categorical_df.rename(columns={"Name_ID": "{}".format(Name_ID),
                                                        "measurement": "{}".format(measurement_name)})
        if not error:
            categorical_df.dropna()

    if categorical_filter:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)

    if error:
        return render_template('barchart.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               all_categorical_entities=all_categorical_entities_sc,
                               all_subcategory_entities=all_subcategory_entities,
                               all_measurement=all_measurement,
                               measurement2=measurement,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               filter=categorical_filter,
                               number_filter=number_filter,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                               how_to_plot=how_to_plot,
                               error=error
                               )

    categorical_df['%'] = 100*categorical_df['count']/categorical_df.groupby(measurement_name)['count'].transform('sum')

    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'count':
            fig = px.bar(categorical_df, x=categorical_entities, y="count", barmode='group', template="plotly_white")
        else:
            fig = px.bar(categorical_df, x=categorical_entities, y="%", barmode='group', template="plotly_white")
    else:
        if how_to_plot == 'count':
            fig = px.bar(categorical_df, x=measurement_name, y="count", color=categorical_entities, barmode='group',
                         template="plotly_white")
        else:
            fig = px.bar(categorical_df, x=measurement_name, y="%", color=categorical_entities, barmode='group',
                         template="plotly_white")

    fig.update_layout(font=dict(size=16))
    fig = fig.to_html()

    return render_template('barchart.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           measurement2=measurement,
                           all_measurement=all_measurement,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           filter=categorical_filter,
                           number_filter=number_filter,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           how_to_plot=how_to_plot,
                           plot=fig
                           )
