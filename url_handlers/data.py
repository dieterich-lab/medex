from flask import Blueprint, render_template, request, jsonify, session, g
import modules.load_data_postgre as ps
import pandas as pd
import requests
import url_handlers.filtering as filtering
from webserver import rdb, data, Name_ID, collect_data_server_side, block_measurement, all_entities, df_min_max, measurement_name,\
    all_measurement, all_num_entities_list, all_cat_entities_list, all_date_entities_list, Meddusa, \
    EXPRESS_MEDEX_MEDDUSA_URL, MEDDUSA_URL

data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data/data1', methods=['GET', 'POST'])
def table_data():
    df = data.dict
    table_schema = session.get('table_schema')
    dat = collect_data_server_side(df, table_schema)
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

    categorical_filter, categorical_names, categorical_filter_zip = filtering.filter_categorical()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)

    categorical_entities = list(set(entities)-set(all_num_entities_list)-set(all_date_entities_list))
    numerical_entities = list(set(entities) - set(all_cat_entities_list) - set(all_date_entities_list))
    date_entities = list(set(entities) - set(all_num_entities_list) - set(all_cat_entities_list))
    dict_entities = {'entities': entities, 'categorical_entities': categorical_entities,
                     'numerical_entities': numerical_entities, 'data_entities' : date_entities}

    df = pd.DataFrame()
    # errors
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif len(entities) == 0:
        error = "Please select entities"
    else:
        df, error = ps.get_data(dict_entities, what_table, measurement, rdb)
    if error:
        return render_template('data.html',
                               error=error,
                               from_nu = from1,
                               to_num = to1,
                               block=block_measurement,
                               all_entities=all_entities,
                               name=measurement_name,
                               measurement=measurement,
                               entities=entities,
                               df_min_max=df_min_max,
                               what_table=what_table,
                               )

    df = filtering.checking_for_block(block_measurement, df, Name_ID, measurement_name)

    session['table_browser_entities'] = entities
    data.csv = df.to_csv(index=False)
    df = df.fillna("missing data")
    column = df.columns.tolist()

    # change name of entities if they have dot inside otherwise server side table doesn't work properly
    column_change_name = []
    [column_change_name.append(i.replace('.', '_').replace("'", "")) for i in column]
    df.columns = column_change_name

    data.dict = df.to_dict("records")
    dict_of_column = []
    table_schema = []

    [dict_of_column.append({'data': column_change_name[i]}) for i in range(0, len(column_change_name))]
    [table_schema.append({'data_name': column_change_name[i], 'column_name': column_change_name[i], "default": "",
                          "order": 1, "searchable": True}) for i in range(0, len(column_change_name))]

    session['table_schema'] = table_schema

    return render_template('data.html',
                           error=error,
                           block=block_measurement,
                           meddusa=Meddusa,
                           meddusa_url_session=meddusa_url_session,
                           all_entities=all_entities,
                           measurement=measurement,
                           entities=entities,
                           name_column=column,
                           name=measurement_name,
                           what_table=what_table,
                           column=dict_of_column,
                           df_min_max=df_min_max,
                           start_date=s_date,
                           end_date=e_date,
                           categorical_filter=categorical_names,
                           numerical_filter_name=name,
                           filter=categorical_filter_zip,
                           val=update,
                           limit_yes=data.limit_selected,
                           limit=data.limit,
                           offset=data.offset,
                           numerical_filter=numerical_filter,
                           )


