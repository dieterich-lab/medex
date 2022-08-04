from flask import Blueprint, render_template, request, jsonify, session
from serverside.serverside_table import ServerSideTable
from url_handlers.filtering import check_for_date_filter_post
from webserver import block_measurement, all_entities, measurement_name,\
    all_measurement, factory, Meddusa, EXPRESS_MEDEX_MEDDUSA_URL, MEDDUSA_URL, start_date, end_date

data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data/data1', methods=['GET', 'POST'])
def table_data():
    session_db = factory.get_session(session.get('session_id'))
    update_filter = session.get('filtering')
    table_browser = session.get('table_browser')
    date_filter = session.get('date_filter')
    dat = ServerSideTable(request, table_browser, date_filter, update_filter, session_db).output_result()

    """
    if Meddusa == 'block':
        session_id = requests.post(EXPRESS_MEDEX_MEDDUSA_URL + '/session/create')
        session_id = session_id.json()

        meddusa_url_send = EXPRESS_MEDEX_MEDDUSA_URL + '/result/cases/set'
        session['meddusa_url_session'] = MEDDUSA_URL + '/_session?sessionid=' + str(session_id['session_id'])

        case_id_json = {"session_id": session_id['session_id'],
                        "cases_ids": [1, 2, 3, 4]}

        requests.post(meddusa_url_send, json=case_id_json)
    """

    return jsonify(dat)


@data_page.route('/data', methods=['GET'])
def get_data():
    return render_template('data.html',
                           all_entities=all_entities)


@data_page.route('/data', methods=['POST'])
def post_data():
    check_for_date_filter_post(start_date, end_date)
    # get request values
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')
    if block_measurement == 'none':
        measurement = [all_measurement[0]]
    else:
        measurement = request.form.getlist('measurement')

    # errors
    error = None
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif len(entities) == 0:
        error = "Please select entities"

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               entities_selected=entities,
                               measurement=measurement,
                               what_table=what_table,
                               )

    if what_table == 'long':
        column = ['name_id', 'case_id', 'date', 'measurement', 'key', 'value']
    else:
        column = ['name_id', 'case_id', 'date', 'measurement']+entities

    # change name of entities if they have dot inside otherwise server side table doesn't work properly
    column_change_name = []
    [column_change_name.append(i.replace('.', '_').replace("'", "")) for i in column]

    dict_of_column = []
    [dict_of_column.append({'data': i}) for i in column_change_name]
    session['table_browser'] = (entities, measurement, what_table, dict_of_column)

    return render_template('data.html',
                           error=error,
                           date=session.get('date_filter'),
                           all_entities=all_entities,
                           entities_selected=entities,
                           measurement=measurement,
                           what_table=what_table,
                           name_column=column,
                           column=dict_of_column,
                           )
