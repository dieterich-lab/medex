from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities

basic_stats_page = Blueprint('basic_stats', __name__,
                             template_folder='basic_stats')


@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():
    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities)


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():

    if 'basic_stats' in request.form:
        """ calculation for numeric values"""

        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities')

        # handling errors and load data from database
        error = None
        if numeric_entities:
            n, error = ps.number(rdb) if not error else (None, error)
            numeric_df,error = ps.get_values(numeric_entities, rdb)
            if not error:
                if len(numeric_df.index) == 0:
                    error = "The selected entities (" + ", ".join(numeric_entities) + ") do not contain any values. "
            else: (None, error)
        else:
            error = "Please select numeric entities"

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_n_entities=numeric_entities,
                                   error=error)

        # calculation basic stats
        numeric_df = numeric_df[numeric_entities]
        basic_stats = { }
        if 'counts' in request.form:
            counts = numeric_df.count()
            basic_stats['counts'] = counts
        if 'counts NaN' in request.form:
            counts = numeric_df.count()
            basic_stats['counts NaN'] = int(n)-counts
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
                                    all_categorical_entities=all_categorical_entities,
                                    all_numeric_entities=all_numeric_entities,
                                    selected_n_entities=numeric_entities,
                                    basic_stats=basic_stats,
                                    error=error_message)

        if any(basic_stats.keys()):
            any_present = numeric_df.shape[0]
            all_present = numeric_df.dropna().shape[0]
            return render_template('basic_stats/basic_stats.html',
                                    numeric_tab=True,
                                    all_categorical_entities=all_categorical_entities,
                                    all_numeric_entities=all_numeric_entities,
                                    selected_n_entities=numeric_entities,
                                    basic_stats=basic_stats,
                                    any_present=any_present,
                                    all_present=all_present)

    if 'basic_stats_c' in request.form:
        """ calculation for categorical values"""

        # list selected data by client
        categorical_entities = request.form.getlist('categorical_entities')

        # handling errors and load data from database
        error = None
        if categorical_entities:
            n, error = ps.number(rdb) if not error else (None, error)
            categorical_df,error = ps.get_cat_values_basic_stas(categorical_entities, rdb)
            if not error:
                if len(categorical_df.index) == 0:
                    error = "The selected entities (" + ", ".join(categorical_df) + ") do not contain any values. "
            else: (None, error)
        else:
            error = "Please select entities"
        if error:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_c_entities=categorical_entities,
                                   error=error)

        basic_stats_c = { }
        for entity in categorical_entities:
            basic_stats_c[entity] = { }
            basic_stats_c[entity]['count'] = categorical_df[entity]['count']
            basic_stats_c[entity]['count NaN'] = int(n) - categorical_df[entity]['count']

        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               selected_c_entities=categorical_entities,
                               basic_stats_c=basic_stats_c)


