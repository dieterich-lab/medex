from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_visit
import pandas as pd

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
            numeric_df,error = ps.get_num_values_basic_stats(numeric_entities,visit1, rdb)
            if not error:
                if len(numeric_df.index) == 0:
                    error = "The selected entities (" + ", ".join(numeric_entities) + ") do not contain any values. "

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
        numeric_df = numeric_df.drop(columns=['Patient_ID'])
        instance=numeric_df['instance'].unique()
        basic_stats =[]
        if 'counts' in request.form:
            counts = numeric_df.groupby(['Key','Visit','instance']).count()
            counts = counts.rename(columns={'Value': 'counts'})
            basic_stats.append(counts)

        if 'counts NaN' in request.form:
            counts2n = numeric_df.groupby(['Key','Visit', 'instance']).count()
            counts2n = int(n) - counts2n
            counts2n = counts2n.rename(columns={'Value': 'counts NaN'})
            basic_stats.append(counts2n)

        if 'mean' in request.form:
            mean2 = numeric_df.groupby(['Key','Visit','instance']).mean().round(decimals=2)
            mean2 = mean2.rename(columns={'Value': 'mean'})
            basic_stats.append(mean2)

        if 'min' in request.form:
            min = numeric_df.groupby(['Key','Visit', 'instance']).min()
            min = min.rename(columns={'Value': 'min'})
            basic_stats.append(min)

        if 'max' in request.form:
            max = numeric_df.groupby(['Key','Visit', 'instance']).max()
            max = max.rename(columns={'Value': 'max'})
            basic_stats.append(max)

        if 'std_dev' in request.form:
            std_dev = numeric_df.groupby(['Key','Visit', 'instance']).std().round(decimals=2)
            std_dev = std_dev.rename(columns={'Value': 'std_dev'})
            basic_stats.append(std_dev)

        if 'std_err' in request.form:
            std_err2 = numeric_df.groupby(['Key','Visit', 'instance']).sem().round(decimals=2)
            std_err2 = std_err2.rename(columns={'Value': 'std_err'})
            basic_stats.append(std_err2)

        if 'median' in request.form:
            median = numeric_df.groupby(['Key','Visit', 'instance']).median().round(decimals=2)
            median = median.rename(columns={'Value': 'median'})
            basic_stats.append(median)

        result = pd.concat(basic_stats, axis=1)
        result =result.to_dict()

        if not any(result.keys()):
            error_message = "You must select at least some statistics"
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_visit=all_visit,
                                   numeric_entities=numeric_entities,
                                   visit1=visit1,
                                   instance=instance,
                                   basic_stats=result,
                                   error=error_message)

        if any(result.keys()):
            any_present = numeric_df.shape[0]
            all_present = numeric_df.dropna().shape[0]
            return render_template('basic_stats/basic_stats.html',
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_visit=all_visit,
                                   numeric_entities=numeric_entities,
                                   basic_stats=result,
                                   visit1=visit1,
                                   instance=instance,
                                   any_present=any_present,
                                   all_present=all_present
                                   )

    if 'basic_stats_c' in request.form:
        """ calculation for categorical values"""

        # list selected data by client
        categorical_entities = request.form.getlist('categorical_entities')
        visit = request.form.getlist('visit')
        if 'Select all' in visit: visit.remove('Select all')
        # handling errors and load data from database
        error = None
        if len(visit) == 0:
            error = "Please select number of visit"
        elif len(categorical_entities) == 0:
            error = "Please select entities"
        else:
            n, error = ps.number(rdb) if not error else (None, error)
            categorical_df,error = ps.get_cat_values_basic_stas(categorical_entities,visit, rdb)
            if not error:
                if len(categorical_df.index) == 0:
                    error = "The selected entities (" + ", ".join(categorical_df) + ") do not contain any values. "

        if error:
            return render_template('basic_stats/basic_stats.html',
                                   categorical_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_visit=all_visit,
                                   categorical_entities=categorical_entities,
                                   visit2=visit,
                                   error=error)


        categorical_df['count NaN'] = int(n) - categorical_df['count']
        instance=categorical_df['number'].unique()


        categorical_df=categorical_df.set_index(['Key', 'Visit','number'])
        basic_stats_c=categorical_df.to_dict()
        return render_template('basic_stats/basic_stats.html',
                               categorical_tab=True,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_visit=all_visit,
                               categorical_entities=categorical_entities,
                               visit2=visit,
                               instance=instance,
                               basic_stats_c=basic_stats_c)


