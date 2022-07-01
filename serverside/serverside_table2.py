import modules.load_data_postgre as ps


class ServerSideTable(object):

    def __init__(self, request, entities, what_table, measurement, columns, date_filter, update_filter, session_db):
        self.result_data = None
        self.cardinality = 0
        self.request_values = request.values
        self._run(entities, what_table, measurement, columns, date_filter, update_filter, session_db)

    def _run(self, entities, what_table, measurement, columns, date_filter, update_filter, session_db):

        self.result_data, self.cardinality = self._custom_paging(entities, what_table, measurement, columns, date_filter,
                                                                 update_filter, session_db)

    def _custom_paging(self, entities, what_table, measurement, columns, date_filter, update_filter, session_db):

        def requires_pagination():
            # Check if the table is going to be paginated
            if self.request_values['iDisplayStart'] != "":
                if int(self.request_values['iDisplayLength']) != -1:
                    return True
            return False

        if not requires_pagination():
            data = """SELECT * FROM examination """
            return data

        offset = int(self.request_values['iDisplayStart'])
        limit = int(self.request_values['iDisplayLength'])
        sort = (columns[int(self.request_values['iSortCol_0'])]['data'], self.request_values['sSortDir_0'])

        df, length, error = ps.get_data(entities, what_table, measurement, limit, offset, sort, date_filter, update_filter,
                                        session_db)
        df = df.fillna("missing data")
        data = df.to_dict('records')
        return data, length

    def output_result(self):

        output = {'iTotalRecords': str(self.cardinality),
                  'iTotalDisplayRecords': str(self.cardinality),
                  'data': self.result_data}
        return output
