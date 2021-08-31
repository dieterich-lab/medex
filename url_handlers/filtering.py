from flask import request,session


def check_for_filter_get():
    categorical_filter = session.get('categorical_filter')
    categorical_names = session.get('categorical_names')
    if categorical_filter:
        categorical_filter = zip(categorical_names, categorical_filter)
    return categorical_filter, categorical_names


def check_for_filter_post():

    categorical_filter = request.form.getlist('filter')
    categorical_names = request.form.getlist('cat')
    session['categorical_filter'] = categorical_filter
    session['categorical_names'] = categorical_names
    categorical_filter_zip = None
    if categorical_filter is not None:
        categorical_filter_zip = zip(categorical_names, categorical_filter)

    return categorical_filter, categorical_names, categorical_filter_zip

def check_for_data_filter():

    Date = request.form.get('Date')
    #Divide dates
    #change dates

    return Date


def checking_for_block(block, df, Name_ID, measurement_name):
    if block == 'none':
        df = df.drop(columns=['measurement'])
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID)})
    else:
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})
    return df

