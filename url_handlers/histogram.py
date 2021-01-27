from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import data, rdb, all_numeric_entities, all_categorical_entities,all_measurement,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,all_subcategory_entities,database,name,name2,block
histogram_page = Blueprint('histogram', __name__,
                           template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    number_of_bins = 20
    filter = data.filter_store
    cat = data.cat
    number_filter = 0
    if filter != None:
        number_filter = len(filter)
        filter = zip(cat, filter)
    return render_template('histogram.html',
                           name='{} number'.format(name),
                           block=block,
                           number_of_bins=number_of_bins,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           filter=filter,
                           number_filter=number_filter
                           )


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():
    if 'filter_c' in request.form:
        filter = request.form.getlist('filter')
        cat = request.form.getlist('cat')
        data.filter_store = filter
        data.cat = cat
        number_filter = 0
        if filter != None:
            number_filter = len(filter)
            filter = zip(cat, filter)
        return render_template('data.html',
                               all_entities=all_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities,
                               filter=filter,
                               number_filter=number_filter,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                               )
    # get selected entities
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')

    subcategory_entities = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')
    #if 'filter' in request.form or 'all_categorical_filter' in request.form:
    #    filter = request.form.getlist('filter')
    #    cat = request.form.getlist('cat')
    #    data.filter_store = filter
    #    data.cat = cat
    #    number_filter = 0
    filter = data.filter_store
    cat = data.cat
    number_filter = 0

    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    # handling errors and load data from database
    error = None
    if measurement == "Search entity":
        error = "Please select number of {}".format(name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    elif not error:
        datu, error = ps.get_num_cat_values(numeric_entities,categorical_entities,subcategory_entities,measurement,filter,cat, rdb)
        datu = datu.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})
        if not error:
            datu = datu.dropna()
            if len(datu.index) == 0:
                error = "This two entities don't have common values"
        else: (None, error)
    if filter != None:
        number_filter = len(filter)
        filter = zip(cat, filter)
    if error:
        return render_template('histogram.html',
                               name='{} number'.format(name),
                               block=block,
                               number_of_bins=number_of_bins,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               measurement=measurement,
                               all_measurement=all_measurement,
                               filter=filter,
                               number_filter=number_filter,
                               error=error)


    # handling errors if number of bins is less then 2
    if number_of_bins.isdigit() and int(number_of_bins) > 2:
        bin_numbers = int(number_of_bins)
    elif number_of_bins == "":
        bin_numbers = 20
    else:
        error = "You have entered non-integer or negative value. Please use positive integer"
        return render_template('histogram.html',
                               name='{} number'.format(name),
                               block=block,
                                all_categorical_entities=all_categorical_entities,
                               number_of_bins=number_of_bins,
                                all_numeric_entities=all_numeric_entities,
                                all_subcategory_entities=all_subcategory_entities,
                                all_measurement=all_measurement,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                                numeric_entities=numeric_entities,
                                categorical_entities=categorical_entities,
                                subcategory_entities=subcategory_entities,
                                measurement=measurement,
                               filter=filter,
                               number_filter=number_filter,
                                error=error)

    if block == 'none':
        fig = px.histogram(datu, x=numeric_entities, color=categorical_entities,barmode='overlay',nbins=bin_numbers,opacity=0.7,template="plotly_white")
    else:
        fig = px.histogram(datu, x=numeric_entities, facet_row=name, color=categorical_entities, barmode='overlay',
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

    return render_template('histogram.html',
                           name='{} number'.format(name),
                           block=block,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           number_of_bins=number_of_bins,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           measurement=measurement,
                           filter=filter,
                           number_filter=number_filter,
                           plot=fig,
                           )
