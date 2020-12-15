from serverside.serverside_table import ServerSideTable
from serverside import table_schemas


class TableBuilder(object):

    def collect_data_serverside(self, request, DATA_SAMPLE,columns):
        #columns = table_schemas.SERVERSIDE_TABLE_COLUMNS
        return ServerSideTable(request, DATA_SAMPLE, columns).output_result()