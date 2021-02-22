from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb, all_numeric_entities_sc, all_categorical_entities_sc, all_measurement,\
    len_numeric, size_categorical, size_numeric, len_categorical, all_subcategory_entities, database, measurement_name,\
    Name_ID, block, data

boxplot_page = Blueprint('boxplot', __name__,
                         template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():
    categorical_filter = data.categorical_filter
    categorical_names = data.categorical_names
    number_filter = 0
    if categorical_filter:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_filter, categorical_names)
    return render_template('boxplot.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_numeric_entities=all_numeric_entities_sc,
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


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():
    id_filter = data.id_filter

    if 'example1' in request.form:
        numeric_entities = 'Adriamycin.FDR'
        categorical_entities = 'Podocyte.Enriched.Transcript'
        subcategory_entities = all_subcategory_entities[categorical_entities]
        how_to_plot='linear'
    elif 'example2' in request.form:
        numeric_entities = 'Wt1.2factor.FDR'
        categorical_entities = 'Podocyte.Enriched.Transcript'
        subcategory_entities = all_subcategory_entities[categorical_entities]
        how_to_plot='linear'
    else:
        numeric_entities = request.form.get('numeric_entities')
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
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    # handling errors and load data from database
    error = None
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    if not error:
        df, error = ps.get_num_cat_values(numeric_entities, categorical_entities, subcategory_entities, measurement,
                                          categorical_filter, categorical_names, id_filter, rdb)
        if not error:
            df = df.dropna()
            if len(df.index) == 0:
                error = "This two entities don't have common values"
    if categorical_filter is not None:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)
    if error:
        return render_template('boxplot.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               error=error,
                               all_categorical_entities=all_categorical_entities_sc,
                               all_numeric_entities=all_numeric_entities_sc,
                               all_subcategory_entities=all_subcategory_entities,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement1=measurement,
                               all_measurement=all_measurement,
                               filter=categorical_filter,
                               number_filter=number_filter,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                               how_to_plot=how_to_plot
                               )

    df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})
    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'linear':
            fig = px.box(df, x=categorical_entities, y=numeric_entities, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(df, x=categorical_entities, y=numeric_entities, color=categorical_entities, template="plotly_white", log_y=True)
    else:
        if how_to_plot == 'linear':
            fig = px.box(df, x=measurement_name, y=numeric_entities, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(df, x=measurement_name, y=numeric_entities, color=categorical_entities, template="plotly_white", log_y=True)
    fig.update_layout(font=dict(size=16))
    fig = fig.to_html()


    return render_template('boxplot.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_numeric_entities=all_numeric_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement1=measurement,
                           filter=categorical_filter,
                           number_filter=number_filter,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           how_to_plot=how_to_plot,
                           plot=fig)
