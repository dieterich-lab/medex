import modules.filtering as ps
from flask import request, session
import datetime


class Filtering:
    def __init__(self, filter_update, case_id, filter_num, filter_cat):
        self.filter_update = filter_update
        self.case_id = case_id
        self.filter_num = filter_num
        self.filter_cat = filter_cat

    def clean_all_filter(self, session_db):
        ps.clean_filter(session_db)
        self.filter_update, self.case_id, self.filter_num, self.filter_cat = 0, 'No', {}, {}
        return {'filter': 'cleaned'}

    def clean_one_filter(self, filters, session_db):
        self.filter_update = self.filter_update - 1
        if self.filter_update == 0:
            ps.clean_filter(session_db)
        else:
            ps.remove_one_filter(filters[0].get('clean_one_filter'), self.filter_update, session_db)
        if filters[1].get('type') == 'categorical':
            session['filter_cat'].pop(filters[0].get('clean_one_filter'))
        else:
            session['filter_num'].pop(filters[0].get('clean_one_filter'))
        return {'filter': 'removed'}

    def add_categorical_filter(self, filters, session_db):
        if filters[0].get('cat') in self.filter_cat:
            return {'filter': 'error'}
        else:
            self.filter_cat.update({filters[0].get('cat'): ','.join(filters[1].get('sub'))})
            self.filter_update = self.filter_update + 1
            ps.add_categorical_filter(filters, self.filter_update, session_db)
            return {'filter': filters[0].get('cat'), 'subcategory': filters[1].get('sub'),
                    'update_filter': session.get('filter_update')}

    def add_numerical_filter(self, filters, session_db):
        if filters[0].get('num') in self.filter_num:
            return {'filter': 'error'}
        else:
            from_to = filters[1].get('from_to').split(";")
            self.filter_num.update({filters[0].get('num'): (from_to[0], from_to[1], filters[2].get('min_max')[0],
                                                            filters[2].get('min_max')[1])})
            self.filter_update = self.filter_update + 1
            ps.add_numerical_filter(filters, self.filter_update, session_db)
            return {'filter': filters[0].get('num'), 'from_num': from_to[0], 'to_num': from_to[1],
                    'update_filter': session.get('filter_update')}

    def add_case_id(self, case_ids, session_db):
        if self.case_id == 'No':
            self.filter_update = self.filter_update + 1
        ps.add_case_ids_to_filter(case_ids['cases_ids'], self.filter_update, self.case_id, session_db)
        self.case_id = 'Yes'

    def date_filter(self):
        pass

    def limit_offset(self):
        pass


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
