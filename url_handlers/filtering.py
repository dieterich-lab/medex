from flask import request, session
import datetime


def check_for_limit_offset():
    limit_selected = request.form.get('limit_yes')
    limit = request.form.get('limit')
    offset = request.form.get('offset')
    session['limit_offset'] = (limit, offset, limit_selected)
    return {'limit': limit, 'offset': offset, 'selected': limit_selected}


def checking_for_block(block, df, name_id, measurement_name):
    if block == 'none':
        df = df.drop(columns=['measurement'])
        df = df.rename(columns={"Name_ID": "{}".format(name_id)})
    else:
        df = df.rename(columns={"Name_ID": "{}".format(name_id), "measurement": "{}".format(measurement_name)})
    return df


def check_for_date_filter_post():
    date_filter = request.form.get('Date')
    date = date_filter.split(" - ")

    s_date, e_date = \
        datetime.datetime.strptime(date[0], '%m/%d/%Y').timestamp() * 1000,\
        datetime.datetime.strptime(date[1], '%m/%d/%Y').timestamp() * 1000

    date_filter = session['date_filter']
    if date_filter[0] != s_date or date_filter[1] != e_date:
        date_filter[2] += 1
    date[0], date[1] = \
        datetime.datetime.strptime(date[0], '%m/%d/%Y').strftime('%Y-%m-%d'),\
        datetime.datetime.strptime(date[1], '%m/%d/%Y').strftime('%Y-%m-%d')
    date.append(date_filter[2])
    session['date_filter'] = (s_date, e_date, date_filter[2])

    return s_date, e_date, date
