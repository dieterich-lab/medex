from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps

histogram_page = Blueprint('histogram', __name__,
                           template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    from webserver import rdb,all_numeric_entities, all_categorical_entities,all_subcategory_entities
    return render_template('histogram.html',
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities)


@histogram_page.route('/histogram', methods=['POST'])
def post_statistics():
    from webserver import rdb,all_numeric_entities, all_categorical_entities,all_subcategory_entities
    # get selected entities
    numeric_entities = request.form.get('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    number_of_bins = request.form.get('number_of_bins')

    # handling errors and load data from database
    error = None
    if numeric_entities == "Search entity" or categorical_entities == "Search entity":
        error = "Please select entity"
    elif not subcategory_entities:
        error = "Please select subcategory"
    elif not error:
        data, error = ps.get_num_cat_values(numeric_entities,categorical_entities,subcategory_entities,rdb)
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
                               selected_entity=numeric_entities,
                               group_by=categorical_entities,
                               error=error)



    # get min and max value in data for adjusting bins in histogram
    min_val = data[numeric_entities].min()
    max_val = data[numeric_entities].max()
    count = data[categorical_entities].count()
    adjusted_bins = (max_val - min_val)

    # handling errors if number of bins is less then 2
    if number_of_bins.isdigit() and int(number_of_bins) > 2:
        int_number_of_bins = int(number_of_bins)
        bin_numbers = (adjusted_bins / int_number_of_bins)
    elif number_of_bins == "":
        bin_numbers = (adjusted_bins / 20)
    else:
        error = "You have entered non-integer or negative value. Please use positive integer"
        return render_template('histogram.html',
                                all_categorical_entities=all_categorical_entities,
                                all_numeric_entities=all_numeric_entities,
                                all_subcategory_entities=all_subcategory_entities,
                                error=error)



    # create histogram
    groups = set(data[categorical_entities].values.tolist())
    plot_series = []
    for group in groups:
        df = data.loc[data[categorical_entities] == group]
        values = df[numeric_entities].values.tolist()
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
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           selected_entity=numeric_entities,
                           group_by=categorical_entities,
                           group =groups,
                           plot_series=plot_series,
                           min_val=min_val,
                           max_val=max_val,
                           number_of_bins=number_of_bins,
                           count=count,
                           all_subcategory_entities=all_subcategory_entities
                           )
