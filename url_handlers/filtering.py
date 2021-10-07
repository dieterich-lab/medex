from flask import request,session
from datetime import datetime


def check_for_filter_get():
    categorical_filter = session.get('categorical_filter')
    categorical_names = session.get('categorical_names')
    if categorical_filter:
        categorical_filter = zip(categorical_names, categorical_filter)
    return categorical_filter, categorical_names


def check_for_numerical_filter_get():
    name, from1, to1, min1, max1 = session.get('name'), session.get('from'), session.get('to'), session.get(
        'min'), session.get('max')
    if name:
        numerical_filter = zip(name, from1, to1, min1, max1)
    else:
        numerical_filter = {}
    return numerical_filter


def check_for_filter_post():

    measurement_filter = request.form.getlist("measurement_filter")
    measurement_filter_text = ",".join(measurement_filter)
    categorical_filter = request.form.getlist('filter')
    categorical_names = request.form.getlist('cat')
    session['categorical_filter'] = categorical_filter
    session['categorical_names'] = categorical_names
    categorical_filter_zip = None
    print(categorical_filter)
    if categorical_filter is not None:
        categorical_filter_zip = zip(categorical_names, categorical_filter)

    return categorical_filter, categorical_names, categorical_filter_zip, measurement_filter, measurement_filter_text


def check_for_date_filter_post():
    date_filter = request.form.get('Date')
    date = date_filter.split(" - ")

    start_date, end_date = datetime.strptime(date[0], '%m/%d/%Y').timestamp() * 1000, \
                           datetime.strptime(date[1], '%m/%d/%Y').timestamp() * 1000
    session['start_date'] = start_date
    session['end_date'] = end_date
    date[0], date[1] = datetime.strptime(date[0], '%m/%d/%Y').strftime('%Y-%m-%d'),\
                    datetime.strptime(date[1], '%m/%d/%Y').strftime('%Y-%m-%d')

    return start_date,end_date,date


def check_for_numerical_filter(df_min_max):

    name = request.form.getlist("name")
    value = request.form.getlist("loan_term")
    from1, to1, min1, max1 = [], [], [], []

    for i in value:
        v = i.split(';')
        from1.append(v[0])
        to1.append(v[1])
    for i in name:
        df = df_min_max[i]
        min_n,max_n = df['min'], df['max']
        min1.append(min_n)
        max1.append(max_n)
    session['name'], session['from'], session['to'], session['min'], session['max'] = name, from1, to1, min1, max1
    if name:
        numerical_filter = zip(name, from1, to1, min1, max1)
    else:
        numerical_filter = {}
    return numerical_filter, name, from1, to1


def checking_for_block(block, df, Name_ID, measurement_name):
    if block == 'none':
        df = df.drop(columns=['measurement'])
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID)})
    else:
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})
    return df

