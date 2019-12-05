from flask import Blueprint, render_template, request

import data_warehouse.redis_rwh as rwh

basic_stats_page = Blueprint('basic_stats', __name__,
                             template_folder='basic_stats')


@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_only_entities)


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    if 'basic_stats' in request.form:
        numeric_entities = request.form.getlist('numeric_entities')
        if not numeric_entities:
            error_message = "Please select numeric entities"
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_only_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_n_entities=numeric_entities,
                                   error=error_message)

        numeric_df = rwh.get_joined_numeric_values(numeric_entities, rdb)
        # to avoid key error
        numeric_df = numeric_df[numeric_df.columns.intersection(numeric_entities)]
        basic_stats = { }
        if 'counts' in request.form:
            counts = numeric_df.count()
            basic_stats['counts'] = counts
        if 'mean' in request.form:
            mean = numeric_df.mean().round(decimals=2)
            basic_stats['mean'] = mean
        if 'min' in request.form:
            min = numeric_df.min()
            basic_stats['min'] = min
        if 'max' in request.form:
            max = numeric_df.max()
            basic_stats['max'] = max
        if 'std_dev' in request.form:
            std_dev = numeric_df.std().round(decimals=2)
            basic_stats['std_dev'] = std_dev
        if 'std_err' in request.form:
            std_err = numeric_df.sem().round(decimals=2)
            basic_stats['std_err'] = std_err
        if 'median' in request.form:
            basic_stats['median'] = numeric_df.median().round(decimals=2)

        if not any(basic_stats.keys()):
            error_message = "You must select at least some statistics"
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_only_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_n_entities=numeric_entities,
                                   basic_stats=basic_stats,
                                   error=error_message)

        if any(basic_stats.keys()):
            any_present = numeric_df.shape[0]
            all_present = numeric_df.dropna().shape[0]
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_only_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_n_entities=numeric_entities,
                                   basic_stats=basic_stats,
                                   any_present=any_present,
                                   all_present=all_present)

    if 'basic_stats_c' in request.form:
        categorical_entities = request.form.getlist('categorical_entities')
        if not categorical_entities:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   all_categorical_entities=all_categorical_only_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_c_entities=categorical_entities,
                                   error="Please select entities")

        categorical_df = rwh.get_joined_categorical_values(categorical_entities, rdb)
        basic_stats_c = { }
        for entity in categorical_entities:
            basic_stats_c[entity] = { }
            # if entity in categorical_df.columns:
            count = categorical_df[categorical_df.columns.intersection([entity])].count()[entity]
            # else:
            #     count = 0
            basic_stats_c[entity]['count'] = count

        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               all_categorical_entities=all_categorical_only_entities,
                               all_numeric_entities=all_numeric_entities,
                               selected_c_entities=categorical_entities,
                               basic_stats_c=basic_stats_c)
