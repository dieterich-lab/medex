import modules.filtering as ps
from flask import request, session
import datetime


def clean_all_filter(session_db):
    ps.clean_filter(session_db)
    session['filtering'] = {'filter_update': '0', 'case_id': 'No', 'filter_num': {}, 'filter_cat': {}}
    return {'filter': 'cleaned'}


def clean_one_filter(filters, session_db):
    session.get('filtering')['filter_update'] = str(int(session.get('filtering')['filter_update']) - 1)
    if session.get('filtering')['filter_update'] == 0:
        clean_all_filter(session_db)
    else:
        ps.remove_one_filter(filters[0].get('clean_one_filter'), session.get('filtering')['filter_update'], session_db)
        if filters[1].get('type') == 'categorical':
            del session.get('filtering')['filter_cat'][filters[0].get('clean_one_filter')]
        else:
            del session.get('filtering')['filter_num'][filters[0].get('clean_one_filter')]
    return {'filter': 'removed'}


def add_categorical_filter(filters, session_db):
    if filters[0].get('cat') in session.get('filtering')['filter_cat']:
        return {'filter': 'error'}
    else:
        session.get('filtering')['filter_cat'].update({filters[0].get('cat'): ','.join(filters[1].get('sub'))})
        session.get('filtering')['filter_update'] = str(int(session.get('filtering')['filter_update']) + 1)
        ps.add_categorical_filter(filters, int(session.get('filtering')['filter_update']), session_db)
        return {'filter': filters[0].get('cat'), 'subcategory': filters[1].get('sub'),
                'update_filter': session.get('filter_update')}


def add_numerical_filter(filters, session_db):
    if filters[0].get('num') in session.get('filtering')['filter_num']:
        return {'filter': 'error'}
    else:
        from_to = filters[1].get('from_to').split(";")
        session.get('filtering')['filter_num'].update({filters[0].get('num'): (from_to[0], from_to[1],
                                                                               filters[2].get('min_max')[0],
                                                                               filters[2].get('min_max')[1])})
        session.get('filtering')['filter_update'] = str(int(session.get('filtering')['filter_update']) + 1)
        ps.add_numerical_filter(filters, int(session.get('filtering')['filter_update']), session_db)
        return {'filter': filters[0].get('num'), 'from_num': from_to[0], 'to_num': from_to[1],
                'update_filter': session.get('filter_update')}


def add_case_id(case_ids, session_db):
    if session.get('filtering')['case_id'] == 'No':
        session.get('filtering')['filter_update'] = str(int(session.get('filtering')['filter_update']) + 1)
    ps.add_case_ids_to_filter(case_ids['cases_ids'], int(session.get('filtering')['filter_update']),
                              session.get('filtering')['case_id'], session_db)
    session.get('filtering')['case_id'] = 'Yes'


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
