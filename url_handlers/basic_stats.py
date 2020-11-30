from flask import Blueprint, render_template, request, session, send_file
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_measurement,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,all_subcategory_entities,database,data,name
import pandas as pd
import io
import time

basic_stats_page = Blueprint('basic_stats', __name__,
                             template_folder='basic_stats')



@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():

    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           name=name,
                           measurement_name=name,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical
                           )


@basic_stats_page.route('/basic_stats', methods=['POST'])
def get_basic_stats():

    if 'basic_stats' in request.form:
        """ calculation for numeric values"""

        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities')
        measurement1 = request.form.getlist('measurement1')
        if 'Select all' in measurement1: measurement1.remove('Select all')

        # handling errors and load data from database
        error = None
        if not measurement1:
            error = "Please select number of {}".format(name)
        elif len(numeric_entities) == 0:
            error = "Please select numeric entities"
        elif numeric_entities:
            n, error = ps.number(rdb) if not error else (None, error)
            df,error = ps.get_num_values_basic_stats(numeric_entities,measurement1, rdb)
            #if not error:
            #    if len(numeric_df.index) == 0:
            #       error = "The selected entities (" + ", ".join(numeric_entities) + ") do not contain any values. "

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   name=name,
                                   measurement_name=name,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_measurement=all_measurement,
                                   numeric_entities=numeric_entities,
                                   measurement1=measurement1,
                                   error=error)




        # calculation basic stats

        instance=df['instance'].unique()

        if not 'count' in request.form: df= df.drop(['count'], axis=1)
        if 'count NaN' in request.form: df['count NaN'] = int(n) - df0['count']
        if not 'mean' in request.form: df= df.drop(['mean'], axis=1)
        if not 'min' in request.form: df= df.drop(['min'], axis=1)
        if not 'max' in request.form: df= df.drop(['max'], axis=1)
        if not 'std_dev' in request.form: df= df.drop(['stddev'], axis=1)
        if not 'std_err' in request.form: df= df.drop(['stderr'], axis=1)
        if not 'median' in request.form: df= df.drop(['median'], axis=1)

        df=df.set_index(['Key', 'measurement',  'instance' ])
        data.g = df.to_csv()
        if df.empty:
            error_message = "You must select at least some statistics"
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   name=name,
                                   measurement_name=name,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_Replicate=all_Replicate,
                                   numeric_entities=numeric_entities,
                                   measurement1=measurement1,
                                   instance=instance,
                                   basic_stats=df,
                                   error=error_message,
                                   )

        result=df.to_dict()
        if any(df.keys()):

            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   name=name,
                                   measurement_name=name,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_measurement=all_measurement,
                                   numeric_entities=numeric_entities,
                                   basic_stats=result,
                                   measurement1=measurement1,
                                   instance=instance,
                                   first_value=list(result.keys())[0],
                                   )

    if 'basic_stats_c' in request.form:
        """ calculation for categorical values"""

        # list selected data by client
        categorical_entities = request.form.getlist('categorical_entities')
        measurement = request.form.getlist('measurement')
        if 'Select all' in measurement: measurement.remove('Select all')
        # handling errors and load data from database
        error = None
        if len(measurement) == 0:
            error = "Please select number of {}".format(name)
        elif len(categorical_entities) == 0:
            error = "Please select entities"
        else:
            n, error = ps.number(rdb) if not error else (None, error)
            categorical_df,error = ps.get_cat_values_basic_stas(categorical_entities,measurement, rdb)
            if not error:
                if len(categorical_df.index) == 0:
                    error = "The selected entities (" + ", ".join(categorical_entities) + ") do not contain any values. "

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   name=name,
                                   measurement_name=name,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_measurement=all_measurement,
                                   categorical_entities=categorical_entities,
                                   measurement2=measurement,
                                   error=error)


        categorical_df['count NaN'] = int(n) - categorical_df['count']
        instance=categorical_df['number'].unique()


        categorical_df=categorical_df.set_index(['Key', 'measurement','number'])
        basic_stats_c=categorical_df.to_dict()
        data.g = categorical_df.to_csv()
        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               name=name,
                               measurement_name=name,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_measurement=all_measurement,
                               categorical_entities=categorical_entities,
                               measurement2=measurement,
                               instance=instance,
                               basic_stats_c=basic_stats_c)



