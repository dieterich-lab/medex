from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_visit


basic_stats_page = Blueprint('basic_stats', __name__,
                             template_folder='basic_stats')


@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():
    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_visit=all_visit)


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():

    if 'basic_stats' in request.form:
        """ calculation for numeric values"""

        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities')
        visit1 = request.form.getlist('visit1')
        if 'Select all' in visit1: visit1.remove('Select all')

        # handling errors and load data from database
        error = None
        if not visit1:
            error = "Please select number of visit"
        elif len(numeric_entities) == 0:
            error = "Please select numeric entities"
        elif numeric_entities:
            n, error = ps.number(rdb) if not error else (None, error)
            numeric_df,error = ps.get_values2(numeric_entities,visit1, rdb)
            if not error:
                if len(numeric_df.index) == 0:
                    error = "The selected entities (" + ", ".join(numeric_entities) + ") do not contain any values. "
            else: (None, error)

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_visit=all_visit,
                                   numeric_entities=numeric_entities,
                                   visit1=visit1,
                                   error=error)

        # calculation basic stats
        error_message = None
        numeric_df = numeric_df.drop(columns=['Patient_ID'])
        new_numeric_entities=numeric_df.columns.tolist()
        new_numeric_entities.remove('Visit')
        numeric_entities_not_measured =set(numeric_entities).difference(set(new_numeric_entities))
        if len(numeric_entities_not_measured) > 0:
            error_message = "{} not measure during visit".format(numeric_entities_not_measured)
        numeric_entities = new_numeric_entities
        entities = numeric_entities + ['Visit']

        numeric_df = numeric_df[entities]

        basic_stats = {}
        if 'counts' in request.form:
            counts = numeric_df.groupby('Visit').count()

            basic_stats['counts'] = counts
        if 'counts NaN' in request.form:
            counts = numeric_df.groupby('Visit').count()

            basic_stats['counts NaN'] = int(n)-counts
        if 'mean' in request.form:
            mean = numeric_df.groupby('Visit').mean().round(decimals=2)

            basic_stats['mean'] = mean
        if 'min' in request.form:
            min = numeric_df.groupby('Visit').min()

            basic_stats['min'] = min
        if 'max' in request.form:
            max = numeric_df.groupby('Visit').max()

            basic_stats['max'] = max
        if 'std_dev' in request.form:
            std_dev = numeric_df.groupby('Visit').std().round(decimals=2)

            basic_stats['std_dev'] = std_dev
        if 'std_err' in request.form:
            std_err = numeric_df.groupby('Visit').sem().round(decimals=2)

            basic_stats['std_err'] = std_err
        if 'median' in request.form:
            median = numeric_df.groupby('Visit').median().round(decimals=2)
            basic_stats['median'] = median

        if not any(basic_stats.keys()):
            error_message = "You must select at least some statistics"
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_visit=all_visit,
                                   numeric_entities=numeric_entities,
                                   visit1=visit1,
                                   basic_stats=basic_stats,
                                   error=error_message)


        if any(basic_stats.keys()):
            any_present = numeric_df.shape[0]
            all_present = numeric_df.dropna().shape[0]
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_visit=all_visit,
                                   numeric_entities=numeric_entities,
                                   basic_stats=basic_stats,
                                   visit1=visit1,
                                   any_present=any_present,
                                   all_present=all_present,
                                   error=error_message)

    if 'basic_stats_c' in request.form:
        """ calculation for categorical values"""

        # list selected data by client
        categorical_entities = request.form.getlist('categorical_entities')
        visit = request.form.getlist('visit')
        if 'Select all' in visit: visit1.remove('Select all')
        # handling errors and load data from database
        error = None
        if len(visit) == 0:
            error = "Please select number of visit"
        elif len(categorical_entities) == 0:
            error = "Please select entities"
        else:
            n, error = ps.number(rdb) if not error else (None, error)
            categorical_df,error = ps.get_cat_values_basic_stas2(categorical_entities,visit, rdb)
            if not error:
                if len(categorical_df.index) == 0:
                    error = "The selected entities (" + ", ".join(categorical_df) + ") do not contain any values. "
            else: (None, error)

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_visit=all_visit,
                                   categorical_entities=categorical_entities,
                                   visit2=visit,
                                   error=error)
        error_message = None
        new_categorical_entities = categorical_df.columns.tolist()

        categorical_entities_not_measured =set(categorical_entities).difference(set(new_categorical_entities))
        if len(categorical_entities_not_measured ) > 0:
            error_message = "{} not measure during visit".format(categorical_entities_not_measured)
        categorical_entities=new_categorical_entities

        basic_stats_c = {}
        basic_stats_c['count'] = categorical_df
        basic_stats_c['count NaN'] = int(n) - categorical_df
        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_visit=all_visit,
                               categorical_entities=categorical_entities,
                               visit2=visit,
                               basic_stats_c=basic_stats_c,
                               error=error_message)


