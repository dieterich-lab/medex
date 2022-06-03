from flask import request, session
import datetime


def checking_for_block(block, df, Name_ID, measurement_name):
    if block == 'none':
        df = df.drop(columns=['measurement'])
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID)})
    else:
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})
    return df


def check_for_date_filter_post():
    change = session['change_date']
    date_filter = request.form.get('Date')
    date = date_filter.split(" - ")
    start_date = session['start_date']
    end_date = session['end_date']

    s_date, e_date = datetime.datetime.strptime(date[0], '%m/%d/%Y').timestamp() * 1000, \
                           datetime.datetime.strptime(date[1], '%m/%d/%Y').timestamp() * 1000

    if start_date != s_date or end_date != e_date:
        change += 1

    date[0], date[1] = datetime.datetime.strptime(date[0], '%m/%d/%Y').strftime('%Y-%m-%d'),\
                    datetime.datetime.strptime(date[1], '%m/%d/%Y').strftime('%Y-%m-%d')
    date.append(change)
    session['start_date'] = s_date
    session['end_date'] = e_date
    session['change_date'] = change

    return s_date, e_date, date


def filter_categorical():

    cat_filter_check = request.form.get('categorical_filter_check')
    filter_cat = request.form.get('categorical_filter')
    filter_sub_cat = request.form.getlist('subcategory_entities')
    print(cat_filter_check, filter_cat, filter_sub_cat)
    session['filter_cat'] = {filter_cat: filter_sub_cat}
    categorical_filter_zip = None

    if filter_cat is not None:
        categorical_filter_zip = zip(filter_sub_cat, filter_cat)
    print(categorical_filter_zip)
    return filter_cat, filter_sub_cat, categorical_filter_zip


def check_for_numerical_filter(df_min_max):

    num_filter_check = request.form.get('numerical_filter_check')
    filter_num = request.form.get('id_numerical_filter')
    num_from = request.form.get('range')
    num_to = request.form.get('input1')
    session['filter_num'] = {filter_num: [num_from, num_to]}

    return num_filter_check, filter_num, num_from, num_to




