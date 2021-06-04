from flask import Blueprint, render_template, request,session
from webserver import all_patient, all_categorical_entities_sc, all_subcategory_entities, all_numeric_entities,all_entities

sidebar_page = Blueprint('sidebar', __name__, template_folder='templates')

"""
@sidebar_page.route('/data', methods=['GET'])
def get_statistics():
    return render_template('data.html',
                           all_patient=all_patient,
                           all_entities=all_entities,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           all_numerical_entities=all_numeric_entities
                           )



@sidebar_page.route('/data', methods=['POST'])
def data_post_statistics():


    # get data from  html form
    id_filter = request.form.getlist('id_filter')
    categorical_filter = request.form.get('categorical_entities')
    subcategory_filter = request.form.getlist('subcategory_entities')
    numerical_filter = request.form.getlist('numerical_filter')
    filter = request.form.getlist('filter')
    session['id_filter'] = id_filter
    session['categorical_filter'] = categorical_filter
    session['subcategory_filter'] = subcategory_filter
    session['numerical_filter'] = numerical_filter

    if categorical_filter is not None:
        number_filter = len(categorical_filter)
        categorical_filter = zip(subcategory_filter, categorical_filter)
    return render_template('data.html',
                           all_patient=all_patient,
                           all_entities=all_entities,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           all_numeric_entities=all_numeric_entities,
                           id_filter=id_filter,
                           categorical_entities=categorical_filter,
                           subcategory_entities=subcategory_filter,
                           numerical_filter=numerical_filter,
                           filter=categorical_filter,
                           )
                           
"""
"""
@sidebar_page.route('/barchart', methods=['POST'])
def post_statistics():

    # get data from  html form
    id_filter = request.form.getlist('id_filter')
    categorical_filter = request.form.get('categorical_entities')
    subcategory_filter = request.form.getlist('subcategory_entities')
    numerical_filter = request.form.getlist('numerical_filter')
    filter = request.form.getlist('filter')
    session['id_filter'] = id_filter
    session['categorical_filter'] = categorical_filter
    session['subcategory_filter'] = subcategory_filter
    session['numerical_filter'] = numerical_filter
    categorical_filter = zip(categorical_filter, subcategory_filter)
    return render_template('barchart.html',
                           all_patient=all_patient,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           all_numeric_entities=all_numeric_entities,
                           id_filter=id_filter,
                           categorical_entities=categorical_filter,
                           subcategory_entities=subcategory_filter,
                           numerical_filter=numerical_filter,
                           filter=categorical_filter)

"""