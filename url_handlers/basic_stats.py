from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps


basic_stats_page = Blueprint('basic_stats', __name__,
                             template_folder='basic_stats')



@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():

    # connection and load data from database
    from webserver import connect_db,rdb,all_numeric_entities,all_categorical_entities


    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities)


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():
    # connection with database and load name of entities
    from webserver import rdb,all_numeric_entities,all_categorical_entities




    if 'basic_stats' in request.form:
        """ calculation for numeric values"""

        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities')

        # handling errors and load data from database
        error = None
        if numeric_entities:
            numeric_df = ps.get_values(numeric_entities, rdb)
            error = "The selected entities (" + ", ".join(numeric_entities) + ") do not contain any values. " if error else None
        else:
            error = "Please select numeric entities"
        if error:
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_n_entities=numeric_entities,
                                   error=error)

        """calculation basic stats (maybe should I do this in SQL)"""
        # to avoid key error
#        numeric_df = numeric_df[numeric_df.columns.intersection(numeric_entities)]
        print(numeric_df)
        basic_stats = { }
        if 'counts' in request.form:
            counts = numeric_df.count()
            basic_stats['counts'] = counts
        if 'counts NaN' in request.form:
            counts = numeric_df.count()
            basic_stats['counts NaN'] = len(numeric_df.index)-counts
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
            categorical_df = ps.get_cat_values(categorical_entities, rdb)
            error = "No data based on the selected entities ( " + ", ".join(categorical_entities) + " ) " if error else None
        else:
            error = "Please select entities"
        if error:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   selected_c_entities=categorical_entities,
                                   error=error)


        """calculation basic stats (maybe should I do this in SQL)"""
        basic_stats_c = { }
        for entity in categorical_entities:
            basic_stats_c[entity] = { }
            # if entity in categorical_df.columns:
            count = categorical_df[categorical_df.columns.intersection([entity])].count()[entity]
            basic_stats_c[entity]['count'] = count
            basic_stats_c[entity]['count NaN'] = len(categorical_df.index) - count

        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               selected_c_entities=categorical_entities,
                               basic_stats_c=basic_stats_c)


