from flask import Blueprint, render_template, request,session
import modules.load_data_postgre as ps
import url_handlers.filtering as filtering
from webserver import rdb,  all_measurement, data, measurement_name, block, df_min_max
import pandas as pd

basic_stats_page = Blueprint('basic_stats', __name__, template_folder='basic_stats')


@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():
    start_date, end_date = filtering.date()
    numerical_filter = filtering.check_for_numerical_filter_get()
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           name=measurement_name,
                           measurement_name=measurement_name,
                           start_date=start_date,
                           end_date=end_date,
                           measurement_filter=session.get('measurement_filter'),
                           filter=categorical_filter,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max)


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():

    # get filter
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    if 'basic_stats' in request.form:
        """ calculation for numeric values"""

        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities_multiple')

        if block == 'none':
            measurement1 = all_measurement.values
        else:
            measurement1 = request.form.getlist('measurement_numeric')

        # handling errors and load data from database
        df = pd.DataFrame()
        error = None
        if not measurement1:
            error = "Please select number of {}".format(measurement_name)
        elif len(numeric_entities) == 0:
            error = "Please select numeric entities"
        elif numeric_entities:
            df, error = ps.get_basic_stats(numeric_entities, measurement1, case_ids, categorical_filter,
                                           categorical_names, name, from1, to1, measurement_filter, date, rdb)

        # calculation basic stats
        if not 'count NaN' in request.form: df = df.drop(['count NaN'], axis=1)
        if not 'count' in request.form: df = df.drop(['count'], axis=1)
        if not 'mean' in request.form: df = df.drop(['mean'], axis=1)
        if not 'min' in request.form: df = df.drop(['min'], axis=1)
        if not 'max' in request.form: df = df.drop(['max'], axis=1)
        if not 'std_dev' in request.form: df = df.drop(['stddev'], axis=1)
        if not 'std_err' in request.form: df = df.drop(['stderr'], axis=1)
        if not 'median' in request.form: df = df.drop(['median'], axis=1)

        df = df.set_index(['Key', 'measurement'])
        data.csv = df.to_csv()
        result = df.to_dict()
        if error:
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   name=measurement_name,
                                   block=block,
                                   measurement_name=measurement_name,
                                   all_measurement=all_measurement,
                                   numeric_entities=numeric_entities,
                                   measurement_numeric=measurement1,
                                   measurement_filter=measurement_filter,
                                   start_date=start_date,
                                   end_date=end_date,
                                   filter=categorical_filter_zip,
                                   numerical_filter=numerical_filter,
                                   df_min_max=df_min_max,
                                   error=error)

        if any(df.keys()):
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   name=measurement_name,
                                   measurement_name=measurement_name,
                                   all_measurement=all_measurement,
                                   numeric_entities=numeric_entities,
                                   basic_stats=result,
                                   measurement_numeric=measurement1,
                                   measurement_filter=measurement_filter,
                                   first_value=list(result.keys())[0],
                                   start_date=start_date,
                                   end_date=end_date,
                                   filter=categorical_filter_zip,
                                   numerical_filter=numerical_filter,
                                   df_min_max=df_min_max
                                   )

    if 'basic_stats_c' in request.form:
        """ calculation for categorical values"""

        # list selected data by client
        categorical_entities = request.form.getlist('categorical_entities')
        if block == 'none':
            measurement = all_measurement.values
        else:
            measurement = request.form.getlist('measurement_categorical')

        # handling errors and load data from database
        df = pd.DataFrame()

        if len(measurement) == 0:
            error = "Please select number of {}".format(measurement_name)
        elif len(categorical_entities) == 0:
            error = "Please select entities"
        else:
            df, error = ps.get_cat_basic_stats(categorical_entities, measurement, case_ids,
                                                           categorical_filter, categorical_names, name, from1,
                                                           to1, measurement_filter, date, rdb)
            if not error:
                if len(df.index) == 0:
                    error = "The selected entities (" + ", ".join(categorical_entities) + ") do not contain any values. "

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   name=measurement_name,
                                   block=block,
                                   measurement_name=measurement_name,
                                   all_measurement=all_measurement,
                                   categorical_entities=categorical_entities,
                                   measurement_categorical=measurement,
                                   measurement_filter=measurement_filter,
                                   start_date=start_date,
                                   end_date=end_date,
                                   filter=categorical_filter_zip,
                                   numerical_filter=numerical_filter,
                                   df_min_max=df_min_max,
                                   error=error)
        df = df.set_index(['Key', 'measurement'])
        basic_stats_c = df.to_dict()

        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               name=measurement_name,
                               block=block,
                               measurement_name=measurement_name,
                               all_measurement=all_measurement,
                               categorical_entities=categorical_entities,
                               measurement_categorical=measurement,
                               measurement_filter=measurement_filter,
                               basic_stats_c=basic_stats_c,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               df_min_max=df_min_max)



