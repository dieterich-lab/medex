from flask import request,session
import datetime
#from webserver import start_date, end_date

def date():
    start_date = session.get('start_date')
    end_date = session.get('end_date')
    if start_date is None:
        now = datetime.datetime.now()
        start_date = datetime.datetime.timestamp(now - datetime.timedelta(days=365.24*100)) * 1000
        end_date = datetime.datetime.timestamp(now) * 1000
    return start_date, end_date


def check_for_filter_get():
    categorical_filter = session.get('categorical_filter')
    categorical_names = session.get('categorical_filter')
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

    categorical_filter = request.form.getlist('filter')
    categorical_names = request.form.getlist('cat')
    session['categorical_filter'] = categorical_filter
    session['categorical_names'] = categorical_names
    categorical_filter_zip = None

    if categorical_filter is not None:
        categorical_filter_zip = zip(categorical_names, categorical_filter)

    return categorical_filter, categorical_names, categorical_filter_zip


def check_for_date_filter_post():
    change = session['change_date']
    date_filter = request.form.get('Date')
    date = date_filter.split(" - ")
    start_date = session['start_date']
    end_date = session['end_date']

    s_date, e_date = datetime.datetime.strptime(date[0], '%m/%d/%Y').timestamp() * 1000, \
                           datetime.datetime.strptime(date[1], '%m/%d/%Y').timestamp() * 1000

    if start_date != s_date or end_date != e_date:
        change +=1

    date[0], date[1] = datetime.datetime.strptime(date[0], '%m/%d/%Y').strftime('%Y-%m-%d'),\
                    datetime.datetime.strptime(date[1], '%m/%d/%Y').strftime('%Y-%m-%d')
    date.append(change)
    session['start_date'] = s_date
    session['end_date'] = e_date
    session['change_date'] = change

    return s_date, e_date, date


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

