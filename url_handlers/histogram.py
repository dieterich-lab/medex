from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import data, rdb, all_numeric_entities_sc, all_categorical_entities_sc, all_measurement,\
    len_numeric, size_categorical, size_numeric, len_categorical, all_subcategory_entities, database, Name_ID,\
    measurement_name, block

histogram_page = Blueprint('histogram', __name__,
                           template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    number_of_bins = 20
    categorical_filter = data.categorical_filter
    categorical_names = data.categorical_names
    number_filter = 0
    if categorical_filter:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)
    return render_template('histogram.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           number_of_bins=number_of_bins,
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
                           number_filter=number_filter
                           )


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():
    id_filter = data.id_filter
    # get selected entities
    if 'example3' in request.form:
        numeric_entities = 'Adriamycin.FDR'
        categorical_entities = 'Podocyte.Enriched.Transcript'
        subcategory_entities = all_subcategory_entities[categorical_entities]
    elif 'example4' in request.form:
        numeric_entities = 'Wt1.2factor.FDR'
        categorical_entities = 'Podocyte.Enriched.Transcript'
        subcategory_entities = all_subcategory_entities[categorical_entities]
    elif 'example1' in request.form:
        numeric_entities = 'Adriamycin.log2FC'
        categorical_entities = 'Podocyte.Enriched.Transcript'
        subcategory_entities = all_subcategory_entities[categorical_entities]
    elif 'example2' in request.form:
        numeric_entities = 'Wt1.2factor.log2FC'
        categorical_entities = 'Podocyte.Enriched.Transcript'
        subcategory_entities = all_subcategory_entities[categorical_entities]
    else:
        numeric_entities = request.form.get('numeric_entities')
        categorical_entities = request.form.get('categorical_entities')
        subcategory_entities = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')
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
    if measurement == "Search entity":
        error = "Please select number of {}".format(measurement_name)
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    elif not error:
        df, error = ps.get_num_cat_values(numeric_entities,categorical_entities,subcategory_entities,measurement,categorical_filter,categorical_names,id_filter, rdb)
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})
        if not error:
            df = df.dropna()
            if len(df.index) == 0:
                error = "This two entities don't have common values"

    if categorical_filter:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)
    if error:
        return render_template('histogram.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               number_of_bins=number_of_bins,
                               all_categorical_entities=all_categorical_entities_sc,
                               all_numeric_entities=all_numeric_entities_sc,
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
                               filter=categorical_filter,
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
                               name='{}'.format(measurement_name),
                               block=block,
                               all_categorical_entities=all_categorical_entities_sc,
                               number_of_bins=number_of_bins,
                               all_numeric_entities=all_numeric_entities_sc,
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
                               filter=categorical_filter,
                               number_filter=number_filter,
                               error=error)

    if block == 'none':
        fig = px.histogram(df, x=numeric_entities, color=categorical_entities,barmode='overlay',nbins=bin_numbers,opacity=0.7,template="plotly_white")
    else:
        fig = px.histogram(df, x=numeric_entities, facet_row=measurement_name, color=categorical_entities, barmode='overlay',
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
                           all_categorical_entities=all_categorical_entities_sc,
                           all_numeric_entities=all_numeric_entities_sc,
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
                           filter=categorical_filter,
                           number_filter=number_filter,
                           plot=fig,
                           )
