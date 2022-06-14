from flask import Blueprint, render_template, request, jsonify, session
import pandas as pd
#from serverside.serverside_table import ServerSideTable
from serverside.serverside_table2 import ServerSideTable
from webserver import data, Name_ID, block_measurement, all_entities, measurement_name,\
    all_measurement, session_db
data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data/data1', methods=['GET', 'POST'])
def table_data():
    table_browser = session.get('table_browser')
    dat = ServerSideTable(request, table_browser[0], table_browser[1], table_browser[2], session_db).output_result()
    return jsonify(dat)


@data_page.route('/data', methods=['GET'])
def get_data():
    return render_template('data.html',
                           all_entities=all_entities)


@data_page.route('/data', methods=['POST'])
def post_data():

    # get request values
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')
    if block_measurement == 'none':
        measurement = all_measurement[0]
    else:
        measurement = request.form.getlist('measurement')

    # get_filter
    date_filter = session.get('date_filter')
    limit_filter = session.get('limit_offset')
    update_filter = session.get('filter_update')

    df = pd.DataFrame()
    # errors
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif len(entities) == 0:
        error = "Please select entities"
    else:
        #df, error = ps.get_data(entities, what_table, measurement, session_db)
        df,error=pd.DataFrame(),None

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               entities_selected=entities,
                               measurement=measurement,
                               what_table=what_table,
                               )

    session['table_browser'] = (entities, what_table, measurement)
    data.csv = df.to_csv(index=False)

    if what_table == 'long':
        column = ['name_id', 'case_id', 'measurement', 'key', 'value']
    else:
        column = ['name_id', 'case_id', 'measurement']+entities


    # change name of entities if they have dot inside otherwise server side table doesn't work properly
    column_change_name = []
    [column_change_name.append(i.replace('.', '_').replace("'", "")) for i in column]


    dict_of_column = []
    [dict_of_column.append({'data': i}) for i in column_change_name]

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           entities_selected=entities,
                           measurement=measurement,
                           what_table=what_table,
                           name_column=column,
                           column=dict_of_column,
                           )
