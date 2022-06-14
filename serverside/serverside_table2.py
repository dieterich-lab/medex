import modules.load_data_postgre as ps


class ServerSideTable(object):
    """
    Retrieves the values specified by Datatables in the request and processes
    the data that will be displayed in the table (filtering, sorting and
    selecting a subset of it).

    Attributes:
        request: Values specified by DataTables in the request.
        data: Data to be displayed in the table.
        column_list: Schema of the table that will be built. It contains
                     the name of each column (both in the data and in the
                     table), the default values (if available) and the
                     order in the HTML.
    """

    def __init__(self, request, entities, what_table, measurement, session_db):
        self.result_data = None
        self.cardinality = 0
        self.request_values = request.values
        self._run(entities, what_table, measurement, session_db)

    def _run(self, entities, what_table, measurement, session_db):
        """
        Prepares the data, and values that will be generated as output.
        It does the actual filtering, sorting and paging of the data.

        Args:
            data: Data to be displayed by DataTables.
        """

        self.result_data, self.cardinality = self._custom_paging(entities, what_table, measurement, session_db)

    def _custom_paging(self, entities, what_table, measurement, session_db):
        """
        Selects a subset of the filtered and sorted data based on if the table
        has pagination, the current page and the size of each page.

        Args:
            data: Filtered and sorted data.

        Returns:
            Subset of the filtered and sorted data that will be displayed by
            the DataTables if the pagination is enabled.
        """
        def requires_pagination():
            # Check if the table is going to be paginated
            if self.request_values['iDisplayStart'] != "":
                if int(self.request_values['iDisplayLength']) != -1:
                    return True
            return False

        if not requires_pagination():
            data = """SELECT * FROM examination """
            return data

        start = int(self.request_values['iDisplayStart'])
        length = int(self.request_values['iDisplayLength'])

        df, len, error = ps.get_data(entities, what_table, measurement, length, start, session_db)
        df = df.fillna("missing data")
        data = df.to_dict('records')
        return data, len

    def output_result(self):
        """
        Generates a dict with the content of the response. It contains the
        required values by DataTables (echo of the reponse and cardinality
        values) and the data that will be displayed.

        Return:
            Content of the response.
        """
        output = {}
        output['iTotalRecords'] = str(self.cardinality)
        output['iTotalDisplayRecords'] = str(self.cardinality)
        output['data'] = self.result_data
        return output