from flask import Blueprint, render_template, request,session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, measurement_name,Name_ID, block, df_min_max,data
import pandas as pd

boxplot_page = Blueprint('boxplot', __name__,
                         template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    numerical_filter = filtering.check_for_numerical_filter_get()
    return render_template('boxplot.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_measurement=all_measurement,
                           start_date=session.get('start_date'),
                           end_date=session.get('end_date'),
                           measurement_filter=session.get('measurement_filter'),
                           filter=categorical_filter,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max
                           )


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():
    # get filters
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter= filtering.check_for_filter_post()
    numerical_filter,numerical_filter_name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    # handling errors and load data from database
    error = None
    if measurement == "Search entity":
        error = "Please select number of {}".format(measurement_name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    elif not error:
        df, error = ps.get_num_cat_values(numeric_entities, categorical_entities, subcategory_entities, measurement, case_ids,
                                          categorical_filter, categorical_names, numerical_filter_name, from1, to1,
                                          measurement_filter, date, rdb)
        numeric_entities_unit, error = ps.get_unit(numeric_entities, rdb)
        new_column = session.get('new_column')
        if new_column and (numeric_entities in new_column):
            df = data.new_table
            df = df[['Name_ID', 'measurement', numeric_entities]]
            df_cat, error = ps.get_cat_values_histogram(categorical_entities, subcategory_entities, measurement,
                                          case_ids, categorical_filter, categorical_names, numerical_filter_name,
                                          from1, to1, measurement_filter, date, rdb)
            df = pd.merge(df, df_cat, on=["Name_ID", "measurement"])

        df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})

        if numeric_entities_unit:
            numeric_entities_unit = numeric_entities + ' (' + numeric_entities_unit + ')'
            df.columns = [Name_ID, measurement_name, numeric_entities_unit, categorical_entities]
        else:
            numeric_entities_unit = numeric_entities
        if not error:
            df = df.dropna()
            if len(df.index) == 0:
                error = "This two entities don't have common values"

    if error:
        return render_template('boxplot.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               error=error,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement=measurement,
                               measurement_filter=measurement_filter,
                               all_measurement=all_measurement,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               how_to_plot=how_to_plot,
                               df_min_max=df_min_max
                               )

    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'linear':
            fig = px.box(df, x=categorical_entities, y=numeric_entities_unit, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(df, x=categorical_entities, y=numeric_entities_unit, color=categorical_entities, template="plotly_white", log_y=True)
    else:
        if how_to_plot == 'linear':
            fig = px.box(df, x=measurement_name, y=numeric_entities_unit, color=categorical_entities, template="plotly_white")
        else:
            fig = px.box(df, x=measurement_name, y=numeric_entities_unit, color=categorical_entities, template="plotly_white", log_y=True)
    fig.update_layout(font=dict(size=16))
    fig = fig.to_html()

    return render_template('boxplot.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_measurement=all_measurement,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement=measurement,
                           measurement_filter=measurement_filter,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           how_to_plot=how_to_plot,
                           df_min_max=df_min_max,
                           plot=fig)