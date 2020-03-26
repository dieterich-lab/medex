from flask import Blueprint, render_template, request
import numpy as np
import modules.load_data_postgre as ps

histogram_page = Blueprint('histogram', __name__,
                           template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    
    # connection and load data from database
    from webserver import get_db2
    rdb = get_db2()
    all_numeric_entities = ps.get_numeric_entities(rdb)
    all_categorical_entities = ps.get_categorical_entities(rdb)

    return render_template('histogram.html',
                           categorical_entities=all_categorical_entities,
                           numeric_entities=all_numeric_entities)


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():
    # connection with database and load name of entities
    from webserver import get_db2
    rdb = get_db2()
    all_numeric_entities = ps.get_numeric_entities(rdb)
    all_categorical_entities = ps.get_categorical_entities(rdb)


    # get selected entities
    entity = request.form.get('entity')
    group_by = request.form.get('group_by')
    number_of_bins = request.form.get('number_of_bins')

    # handling errors and load data from database
    error = None
    if not entity or not group_by or entity == "Choose entity" or group_by == "Choose entity":
        error = "Please select entity and group_by"

    # get joined numerical and categorical values
    if not error:
        data = ps.get_values([entity,group_by],rdb)
        if len(data.index) == 0:
            error = "This two entities don't have common values"


    if error:
        return render_template('histogram.html',
                               categorical_entities=all_categorical_entities,
                               numeric_entities=all_numeric_entities,
                               selected_entity=entity,
                               group_by=group_by,
                               error=error, )




    min_val = data[entity].min()
    max_val = data[entity].max()
    count = data[group_by].count()
    adjusted_bins = (max_val - min_val)

    # handling errors if number of bins is less then 2
    if number_of_bins.isdigit() and int(number_of_bins) > 2:
        int_number_of_bins = int(number_of_bins)
        bin_numbers = (adjusted_bins / int_number_of_bins)
    elif number_of_bins == "":
        bin_numbers = (adjusted_bins / 20)
    else:
        error = "You have entered non-integer or negetive value. Please use positive integer"
        return render_template('histogram.html',
                                categorical_entities=all_categorical_entities,
                                numeric_entities=all_numeric_entities,
                                error=error)


    groups = set(data[group_by].values.tolist())
    plot_series = []
    table_data={}
    for group in groups:
        df = data.loc[data[group_by] == group]
        values = df[entity].values.tolist()
        if number_of_bins.isdigit():
            hist=np.histogram(values, bins=int(number_of_bins),range = (min_val,max_val))
        else:
            hist = np.histogram(values, bins=20, range=(min_val, max_val))
        table_data[group]={}
        table_data[group]['count'] =hist[0]
        table_data[group]['bin'] = hist[1]
        if (values):
            plot_series.append({
                'x'       : values,
                'type'    : "histogram",
                'opacity' : 0.5,
                'name'    : group,
                'xbins'   : {
                    'end': max_val,
                    'size': bin_numbers,
                    'start': min_val
                    }
                })

    return render_template('histogram.html',
                           categorical_entities=all_categorical_entities,
                           numeric_entities=all_numeric_entities,
                           selected_entity=entity,
                           group_by=group_by,
                           group =groups,
                           table_data=table_data,
                           plot_series=plot_series,
                           min_val=min_val,
                           max_val=max_val,
                           number_of_bins=number_of_bins,
                           count=count
                           )
