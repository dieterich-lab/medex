from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb,all_numeric_entities, all_categorical_entities,all_subcategory_entities,all_visit
histogram_page = Blueprint('histogram', __name__,
                           template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():

    return render_template('histogram.html',
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit)


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():

    # get selected entities
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')
    visit = request.form.getlist('visit')

    # handling errors and load data from database
    error = None
    if visit == "Search entity":
        error = "Please select number of visit"
    elif numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    elif not error:
        data, error = ps.get_num_cat_values(numeric_entities,categorical_entities,subcategory_entities,visit,rdb)
        if not error:
            data = data.dropna()
            if len(data.index) == 0:
                error = "This two entities don't have common values"
        else: (None, error)

    if error:
        return render_template('histogram.html',
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               visit=visit,
                               all_visit=all_visit,
                               error=error)




    # handling errors if number of bins is less then 2
    if number_of_bins.isdigit() and int(number_of_bins) > 2:
        bin_numbers = int(number_of_bins)
    elif number_of_bins == "":
        bin_numbers = 20
    else:
        error = "You have entered non-integer or negative value. Please use positive integer"
        return render_template('histogram.html',
                                all_categorical_entities=all_categorical_entities,
                                all_numeric_entities=all_numeric_entities,
                                all_subcategory_entities=all_subcategory_entities,
                                all_visit=all_visit,
                                numeric_entities=numeric_entities,
                                categorical_entities=categorical_entities,
                                subcategory_entities=subcategory_entities,
                                visit=visit,
                                error=error)

    fig =px.histogram(data, x=numeric_entities,facet_row='Visit', color=categorical_entities,barmode='overlay',nbins=bin_numbers,opacity=0.7,template="plotly_white")

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
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           selected_entity=numeric_entities,
                           group_by=categorical_entities,
                           plot=fig,
                           number_of_bins=number_of_bins,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           visit=visit,
                           )
