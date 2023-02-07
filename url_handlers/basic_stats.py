from flask import Blueprint, render_template, request, session

from medex.controller.helpers import get_filter_service
from medex.services.database import get_db_session
from modules.get_data_to_basic_stats import get_num_basic_stats, get_cat_date_basic_stats
import url_handlers.filtering as filtering
from url_handlers.filtering import check_for_date_filter_post
from webserver import all_measurement, measurement_name, block_measurement, start_date, end_date
import pandas as pd

basic_stats_page = Blueprint('basic_stats', __name__, template_folder='basic_stats')


@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():
    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           name=measurement_name,
                           measurement_name=measurement_name)


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():
    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = filtering.check_for_limit_offset()
    filter_service = get_filter_service()
    session_db = get_db_session()

    if 'basic_stats' in request.form:
        """ calculation for numeric values"""

        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities_multiple')
        if block_measurement == 'none':
            measurement1 = [all_measurement[0]]
        else:
            measurement1 = request.form.getlist('measurement_numeric')

        # handling errors and load data from database
        error = None
        result = {}
        if not measurement1:
            error = "Please select number of {}".format(measurement_name)
        elif not numeric_entities:
            error = "Please select numeric entities"
        elif numeric_entities:
            df, error = get_num_basic_stats(numeric_entities, measurement1, date_filter, limit_filter, filter_service)
            df['measurement'] = df['measurement'].astype(str)
            df = df.set_index(['key', 'measurement'])
            session['basic_stats_table'] = df.to_csv()
            result = df.to_dict()
        if error:
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   measurement_name=measurement_name,
                                   numeric_entities=numeric_entities,
                                   measurement_numeric=measurement1,
                                   error=error)
        else:
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   name=measurement_name,
                                   measurement_name=measurement_name,
                                   numeric_entities=numeric_entities,
                                   basic_stats=result,
                                   measurement_numeric=measurement1,
                                   first_value=list(result.keys())[0],
                                   )

    if 'basic_stats_c' in request.form:
        """ calculation for categorical values"""

        # list selected data by client
        categorical_entities = request.form.getlist('categorical_entities')
        if block_measurement == 'none':
            measurement = [all_measurement[0]]
        else:
            measurement = request.form.getlist('measurement_categorical')

        # handling errors and load data from database
        df = pd.DataFrame()
        if not measurement:
            error = "Please select number of {}".format(measurement_name)
        elif not categorical_entities:
            error = "Please select entities"
        else:
            df, error = get_cat_date_basic_stats(categorical_entities, measurement, date_filter, limit_filter,
                                                 filter_service, 'examination_categorical', session_db)
            df['measurement'] = df['measurement'].astype(str)

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   name=measurement_name,
                                   measurement_name=measurement_name,
                                   all_measurement=all_measurement,
                                   categorical_entities=categorical_entities,
                                   measurement_categorical=measurement,
                                   error=error)
        df = df.set_index(['key', 'measurement'])
        session['basic_stats_table'] = df.to_csv()
        basic_stats_c = df.to_dict()

        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               name=measurement_name,
                               measurement_name=measurement_name,
                               all_measurement=all_measurement,
                               categorical_entities=categorical_entities,
                               measurement_categorical=measurement,
                               basic_stats_c=basic_stats_c, )

    if 'basic_stats_d' in request.form:
        """ calculation for date values"""

        # list selected data by client
        date_entities = request.form.getlist('date_entities')
        if block_measurement == 'none':
            measurement_d = [all_measurement[0]]
        else:
            measurement_d = request.form.getlist('measurement_date')

        # handling errors and load data from database
        df = pd.DataFrame()

        if not measurement_d:
            error = "Please select number of {}".format(measurement_name)
        elif not date_entities:
            error = "Please select entities"
        else:
            df, error = get_cat_date_basic_stats(date_entities, measurement_d, date_filter, limit_filter,
                                                 filter_service, 'examination_date', session_db)
            df['measurement'] = df['measurement'].astype(str)

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   date_tab=True,
                                   name=measurement_name,
                                   measurement_name=measurement_name,
                                   all_measurement=all_measurement,
                                   date_entities=date_entities,
                                   measurement_date=measurement_d,
                                   error=error)
        df = df.set_index(['key', 'measurement'])
        session['basic_stats_table'] = df.to_csv()
        basic_stats_d = df.to_dict()

        return render_template('basic_stats/basic_stats.html',
                               date_tab=True,
                               name=measurement_name,
                               measurement_name=measurement_name,
                               all_measurement=all_measurement,
                               date_entities=date_entities,
                               measurement_date=measurement_d,
                               basic_stats_d=basic_stats_d)
