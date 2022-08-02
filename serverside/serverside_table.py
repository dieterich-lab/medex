from modules.get_data_to_table_browser import get_data_print, get_table_size
from flask import session


class ServerSideTable(object):

    def __init__(self, request, table_browser, date_filter, update_filter, session_db):
        self.result_data = None
        self.cardinality = 0
        self.request_values = request.values
        self._run(table_browser, date_filter, update_filter, session_db)

    def _run(self, table_browser, date_filter, update_filter, session_db):
        self.result_data, self.cardinality = self._custom_paging(table_browser, date_filter, update_filter, session_db)

    def _custom_paging(self, table_browser, date_filter, update_filter, session_db):

        def requires_pagination():
            # Check if the table is going to be paginated
            if self.request_values['iDisplayStart'] != "":
                if int(self.request_values['iDisplayLength']) != -1:
                    return True
            return False

        if not requires_pagination():
            data = """SELECT * FROM examination """
            return data
        information_from_request = (self.request_values['sEcho'],
                                    int(self.request_values['iDisplayLength']),
                                    int(self.request_values['iDisplayStart']),
                                    (table_browser[3][int(self.request_values['iSortCol_0'])]['data'],
                                     self.request_values['sSortDir_0']))

        df = get_data_print(table_browser, information_from_request, date_filter, update_filter, session_db)
        if self.request_values['sEcho'] == '1':
            length = get_table_size(session_db, table_browser, date_filter, update_filter)
            session['table_size'] = length
        else:
            length = int(session.get('table_size'))
        df = df.fillna("missing data")
        data = df.to_dict('records')
        return data, length

    def output_result(self):
        output = {'iTotalRecords': str(self.cardinality),
                  'iTotalDisplayRecords': str(self.cardinality),
                  'data': self.result_data}
        return output
