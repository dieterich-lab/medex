import modules.filtering as ps
from flask import request, session
import datetime


def check_for_limit_offset():
    limit_selected = request.form.get('limit_yes')
    limit = request.form.get('limit')
    offset = request.form.get('offset')
    session['limit_offset'] = (limit, offset, limit_selected)
    return {'limit': limit, 'offset': offset, 'selected': limit_selected}


def check_for_date_filter_post(start_date, end_date):
    date = request.form.get('Date')
    date = date.split(" - ")

    s_date, e_date = \
        datetime.datetime.strptime(date[0], '%m/%d/%Y').strftime('%Y-%m-%d'),\
        datetime.datetime.strptime(date[1], '%m/%d/%Y').strftime('%Y-%m-%d')
    date[0], date[1] = \
        datetime.datetime.strptime(date[0], '%m/%d/%Y').timestamp() * 1000, \
        datetime.datetime.strptime(date[1], '%m/%d/%Y').timestamp() * 1000
    if date[0] != start_date or date[1] != end_date:
        date_filter = 1
    else:
        date_filter = 0

    session['date_filter'] = (date[0], date[1], date_filter, s_date, e_date)
    return session.get('date_filter')


def checking_for_block(block, df, name_id, measurement_name):
    if block == 'none':
        df = df.drop(columns=['measurement'])
        df = df.rename(columns={"Name_ID": "{}".format(name_id)})
    else:
        df = df.rename(columns={"Name_ID": "{}".format(name_id), "measurement": "{}".format(measurement_name)})
    return df
