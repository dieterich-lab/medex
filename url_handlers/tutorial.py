from flask import Blueprint, render_template
from webserver import all_subcategory_entities,all_categorical_entities,all_subcategory_entities,name,block,all_numeric_entities,all_measurement,database,size_numeric,len_numeric,len_categorical,data,size_categorical

tutorial_page = Blueprint('tutorial', __name__, template_folder='tepmlates')

@tutorial_page.route('/tutorial', methods=['GET', 'POST'])
def logout():
    filter = data.filter_store
    cat = data.cat
    number_filter = 0
    if filter != None:
        number_filter = len(filter)
        filter = zip(cat, filter)
    return render_template('tutorial.html',
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
                           filter=filter,
                           number_filter=number_filter)