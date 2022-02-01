from flask import Blueprint, render_template, request, jsonify, session
import modules.load_data_postgre as ps
import pandas as pd
import time
import url_handlers.filtering as filtering
from webserver import rdb, data, Name_ID, block, table_builder, all_entities, df_min_max, measurement_name,\
    all_measurement

data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data/data1', methods=['GET', 'POST'])
def table_data():
    df = data.dict
    table_schema = data.table_schema
    dat = table_builder.collect_data_serverside(request, df, table_schema)
    return jsonify(dat)


@data_page.route('/data', methods=['GET'])
def get_data():
    return render_template('data.html',
                           block=block,
                           all_entities=all_entities,
                           name=measurement_name)


@data_page.route('/data', methods=['POST'])
def post_data():

    # get filter
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # get request values
    add = request.form.get('Add')
    clean = request.form.get('clean')
    update = request.form.get('update')
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')
    measurement = request.form.getlist('measurement')

    if update is not None or clean is not None or add is not None:
        if add is not None:
            update_list = list(add.split(","))
            update = add
        elif clean is not None:
            update = '0,0'
            update_list = list(update.split(","))
        else:
            update = '0,0'
            update_list = list(update.split(","))
            print(update)
        data.update_filter = update
        start_time = time.time()
        ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1, measurement_filter, update_list,rdb)
        print("--- %s seconds data ---" % (time.time() - start_time))
        return render_template('data.html',
                               block=block,
                               all_entities=all_entities,
                               val=update,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               filter=categorical_filter_zip,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               measurement=measurement,
                               entities=entities,
                               df_min_max=df_min_max
                               )

    update = data.update_filter
    df = pd.DataFrame()
    # errors
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif len(entities) == 0:
        error = "Please select entities"
    else:
        data.information = entities, what_table, measurement, date, rdb
        df, error = ps.get_data(entities, what_table, measurement, date, update, rdb)

    if error:
        return render_template('data.html',
                               error=error,
                               block=block,
                               all_entities=all_entities,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               measurement=measurement,
                               entities=entities,
                               df_min_max=df_min_max,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               filter=categorical_filter_zip,
                               val=update,
                               numerical_filter=numerical_filter,
                               )

    df = filtering.checking_for_block(block, df, Name_ID, measurement_name)

    data.table_browser_entities = entities
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

    data.table_schema = table_schema
    data.table_browser_column = column
    data.table_browser_what_table = what_table
    data.table_browser_column2 = dict_of_column

    return render_template('data.html',
                           error=error,
                           block=block,
                           all_entities=all_entities,
                           measurement=measurement,
                           entities=entities,
                           name_column=column,
                           name=measurement_name,
                           what_table=what_table,
                           column=dict_of_column,
                           df_min_max=df_min_max,
                           measurement_filter=measurement_filter,
                           start_date=start_date,
                           end_date=end_date,
                           categorical_filter=categorical_names,
                           numerical_filter_name=name,
                           filter=categorical_filter_zip,
                           val=update,
                           numerical_filter=numerical_filter,
                           )


