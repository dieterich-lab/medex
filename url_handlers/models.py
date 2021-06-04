from serverside.serverside_table import ServerSideTable


class TableBuilder(object):

    def collect_data_serverside(self, request, DATA_SAMPLE, columns):
        return ServerSideTable(request, DATA_SAMPLE, columns).output_result()
