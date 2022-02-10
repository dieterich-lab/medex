from flask import Blueprint, render_template, request,session
import modules.load_data_postgre as ps
import url_handlers.filtering as filtering
from webserver import rdb,  all_measurement, data, measurement_name, block, df_min_max
import pandas as pd
import time

basic_stats_page = Blueprint('basic_stats', __name__, template_folder='basic_stats')


@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():
    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           name=measurement_name,
                           measurement_name=measurement_name)


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():

    # get filter
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter
    limit_selected = request.form.get('limit_yes')
    data.limit_selected = limit_selected
    limit = request.form.get('limit')
    offset = request.form.get('offset')
    data.limit = limit
    data.offset = offset

    # get request values
    add = request.form.get('Add')
    clean = request.form.get('clean')
    if clean is not None or add is not None:
        if add is not None:
            update_list = list(add.split(","))
            update = add
        elif clean is not None:
            update = '0,0'
            update_list = list(update.split(","))

        data.update_filter = update
        ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1, measurement_filter, update_list,rdb)
        return render_template('basic_stats/basic_stats.html',
                               numeric_tab=True,
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               filter=categorical_filter_zip,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               df_min_max=df_min_max
                               )

    if 'basic_stats' in request.form:
        """ calculation for numeric values"""

        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities_multiple')
        measurement1 = request.form.getlist('measurement_numeric')

        # handling errors and load data from database
        update = data.update_filter
        df = pd.DataFrame()
        error = None
        if not measurement1:
            error = "Please select number of {}".format(measurement_name)
        elif not numeric_entities :
            error = "Please select numeric entities"
        elif numeric_entities:
            df, error = ps.get_basic_stats(numeric_entities, measurement1, date, limit_selected, limit, offset, update, rdb)

            start_time = time.time()
            # calculation basic stats
            if not 'count NaN' in request.form: df = df.drop(['count NaN'], axis=1)
            if not 'count' in request.form: df = df.drop(['count'], axis=1)
            if not 'mean' in request.form: df = df.drop(['mean'], axis=1)
            if not 'min' in request.form: df = df.drop(['min'], axis=1)
            if not 'max' in request.form: df = df.drop(['max'], axis=1)
            if not 'std_dev' in request.form: df = df.drop(['stddev'], axis=1)
            if not 'std_err' in request.form: df = df.drop(['stderr'], axis=1)
            if not 'median' in request.form: df = df.drop(['median'], axis=1)
            n = df.shape[1]
            if n == 2:
                error = "Please select at least one basic statistic"
            else:
                df = df.set_index(['Key', 'measurement'])
                data.csv = df.to_csv()
                result = df.to_dict()
            print("--- %s seconds data ---" % (time.time() - start_time))
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
                                   categorical_filter=categorical_names,
                                   numerical_filter_name =name,
                                   filter=categorical_filter_zip,
                                   numerical_filter=numerical_filter,
                                   df_min_max=df_min_max,
                                   val=update,
                                   limit_yes=data.limit_selected,
                                   limit=data.limit,
                                   offset=data.offset,
                                   error=error)
        else:
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
                                   categorical_filter=categorical_names,
                                   numerical_filter_name =name,
                                   filter=categorical_filter_zip,
                                   numerical_filter=numerical_filter,
                                   df_min_max=df_min_max,
                                   val=update,
                                   limit_yes=data.limit_selected,
                                   limit=data.limit,
                                   offset=data.offset,
                                   )

    if 'basic_stats_c' in request.form:
        """ calculation for categorical values"""

        # list selected data by client
        categorical_entities = request.form.getlist('categorical_entities')
        measurement = request.form.getlist('measurement_categorical')

        # handling errors and load data from database
        update = data.update_filter
        df = pd.DataFrame()

        if not measurement:
            error = "Please select number of {}".format(measurement_name)
        elif not categorical_entities:
            error = "Please select entities"
        else:
            df, error = ps.get_cat_basic_stats(categorical_entities, measurement, date, limit_selected, limit, offset, update, rdb)

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
                                   categorical_filter=categorical_filter,
                                   filter=categorical_filter_zip,
                                   numerical_filter=numerical_filter,
                                   df_min_max=df_min_max,
                                   val=update,
                                   limit_yes=data.limit_selected,
                                   limit=data.limit,
                                   offset=data.offset,
                                   error=error)
        df = df.set_index(['Key', 'measurement'])
        basic_stats_c = df.to_dict()
        data.csv = df.to_csv()

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
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               df_min_max=df_min_max)

    if 'basic_stats_d' in request.form:
        """ calculation for date values"""

        # list selected data by client
        date_entities = request.form.getlist('date_entities')
        measurement_d = request.form.getlist('measurement_date')

        # handling errors and load data from database
        update = data.update_filter
        df = pd.DataFrame()

        if not measurement_d:
            error = "Please select number of {}".format(measurement_name)
        elif not date_entities:
            error = "Please select entities"
        else:

            df, error = ps.get_date_basic_stats(date_entities, measurement_d, date, limit_selected, limit, offset, update, rdb)

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   date_tab=True,
                                   name=measurement_name,
                                   block=block,
                                   measurement_name=measurement_name,
                                   all_measurement=all_measurement,
                                   date_entities=date_entities,
                                   measurement_date=measurement_d,
                                   measurement_filter=measurement_filter,
                                   start_date=start_date,
                                   end_date=end_date,
                                   filter=categorical_filter_zip,
                                   numerical_filter=numerical_filter,
                                   df_min_max=df_min_max,
                                   val=update,
                                   limit_yes=data.limit_selected,
                                   limit=data.limit,
                                   offset=data.offset,
                                   error=error)
        df = df.set_index(['Key', 'measurement'])
        basic_stats_d = df.to_dict()
        data.csv = df.to_csv()

        return render_template('basic_stats/basic_stats.html',
                               date_tab=True,
                               name=measurement_name,
                               block=block,
                               measurement_name=measurement_name,
                               all_measurement=all_measurement,
                               date_entities=date_entities,
                               measurement_date=measurement_d,
                               measurement_filter=measurement_filter,
                               basic_stats_d=basic_stats_d,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               val=update,
                               limit_yes=data.limit_selected,
                               limit=data.limit,
                               offset=data.offset,
                               df_min_max=df_min_max)


