from flask import Blueprint, render_template, request,session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, Name_ID, measurement_name, block, df_min_max, data
import pandas as pd

histogram_page = Blueprint('histogram', __name__, template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    number_of_bins = 20
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    numerical_filter = filtering.check_for_numerical_filter_get()
    return render_template('histogram.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           number_of_bins=number_of_bins,
                           all_measurement=all_measurement,
                           start_date=session.get('start_date'),
                           end_date=session.get('end_date'),
                           measurement_filter=session.get('measurement_filter'),
                           filter=categorical_filter,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max
                           )


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():
    # get filters
    start_date, end_date,date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter,numerical_filter_name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # get selected entities
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')

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

        #get cat values only
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
            df.columns = [Name_ID,measurement_name, numeric_entities_unit, categorical_entities]
        else:
            numeric_entities_unit = numeric_entities
        if not error:
            df = df.dropna()
            if len(df.index) == 0:
                error = "This two entities don't have common values"

    if error:
        return render_template('histogram.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               number_of_bins=number_of_bins,
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
                               df_min_max=df_min_max,
                               error=error)


    # handling errors if number of bins is less then 2
    if number_of_bins.isdigit() and int(number_of_bins) > 2:
        bin_numbers = int(number_of_bins)
    elif number_of_bins == "":
        bin_numbers = 20
    else:
        error = "You have entered non-integer or negative value. Please use positive integer"
        return render_template('histogram.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               number_of_bins=number_of_bins,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement=measurement,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               df_min_max=df_min_max,
                               error=error)

    if block == 'none':
        fig = px.histogram(df, x=numeric_entities_unit, color=categorical_entities,barmode='overlay',nbins=bin_numbers,opacity=0.7,template="plotly_white")
    else:
        fig = px.histogram(df, x=numeric_entities_unit, facet_row=measurement_name, color=categorical_entities, barmode='overlay',
                           nbins=bin_numbers, opacity=0.7, template="plotly_white")

    fig.update_layout(
        font=dict(size=16),
        height=800,
        title={
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    fig = fig.to_html()

    #df=df[df[categorical_entities] == 'no']
    #counts, bins = np.histogram(df[numeric_entities], bins=21)
    #bins = 0.5 * (bins[:-1] + bins[1:])
    #df = pd.DataFrame({"bins": bins[1:], "counts": counts})
    #df=pd.cut(df['bins'], bins=bins, labels=bins[1:])
    #print(df)
    #df = pd.cut(df['visitors'],bins=bins)
    #agg=
    #figu = px.bar(df,x='bins', y='counts', labels={'x': 'total_bill', 'y': 'count'},hover_data={'bins':True})
    #figu.show()
    #print(counts,bins)
    return render_template('histogram.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           all_measurement=all_measurement,
                           number_of_bins=number_of_bins,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement=measurement,
                           measurement_filter=measurement_filter,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max,
                           plot=fig,
                           )
