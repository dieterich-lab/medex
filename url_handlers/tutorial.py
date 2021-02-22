from flask import Blueprint, render_template
from webserver import all_categorical_entities, all_subcategory_entities, measurement_name,\
    block, all_numeric_entities, all_measurement, database, size_numeric, len_numeric, len_categorical, data,\
    size_categorical

tutorial_page = Blueprint('tutorial', __name__, template_folder='tepmlates')


@tutorial_page.route('/tutorial', methods=['GET', 'POST'])
def logout():
    categorical_filter = data.categorical_filter
    categorical_names = data.categorical_names
    number_filter = 0
    if categorical_filter != None:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)
    return render_template('tutorial.html',
                           name='{} number'.format(measurement_name),
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
                           filter=categorical_filter,
                           number_filter=number_filter)
