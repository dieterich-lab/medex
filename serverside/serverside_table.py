from medex.services.filter import FilterService
from modules.get_data_to_table_browser import get_data_print, get_table_size
from flask import session


class ServerSideTable(object):

    def __init__(self, request, table_browser, date_filter, filter_service: FilterService, db_session):
        self.result_data = None
        self.cardinality = 0
        self.request_values = request.values
        self._filter_service = filter_service
        self._db_session = db_session
        self._run(table_browser, date_filter)

    def _run(self, table_browser, date_filter):
        self.result_data, self.cardinality = self._custom_paging(table_browser, date_filter)

    def _custom_paging(self, table_browser, date_filter):
        information_from_request = (self.request_values['sEcho'],
                                    int(self.request_values['iDisplayLength']),
                                    int(self.request_values['iDisplayStart']),
                                    (table_browser[3][int(self.request_values['iSortCol_0'])]['data'],
                                     self.request_values['sSortDir_0']))

        df = get_data_print(
            table_browser, information_from_request, date_filter,
            self._filter_service, self._db_session
        )
        if self.request_values['sEcho'] == '1':
            length = get_table_size(self._db_session, table_browser, date_filter, self._filter_service)
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
