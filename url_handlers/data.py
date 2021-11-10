from flask import Blueprint, render_template, request, jsonify, session
import modules.load_data_postgre as ps
import pandas as pd

import url_handlers.filtering as filtering
from webserver import rdb, data, Name_ID, measurement_name, block, table_builder, all_entities, df_min_max, measurement_name,\
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
    numerical_filter = filtering.check_for_numerical_filter_get()
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    return render_template('data.html',
                           block=block,
                           all_entities=all_entities,
                           name=measurement_name,
                           start_date=session.get('start_date'),
                           end_date=session.get('end_date'),
                           measurement_filter=session.get('measurement_filter'),
                           numerical_filter=numerical_filter,
                           filter=categorical_filter,
                           df_min_max=df_min_max)


@data_page.route('/data', methods=['POST'])
def post_data():

    # get filter
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # get selected entities
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')

    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    # errors
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif len(entities) == 0:
        error = "Please select entities"
    else:
       new_column = session.get('new_column')
       if new_column:
            entities1 = [x for x in entities if x not in new_column]
       else:
           entities1 = entities
       df0, error = ps.get_data(entities1, what_table, measurement, case_ids, categorical_filter, categorical_names, name, from1, to1,
                               measurement_filter, date, rdb)

       df = data.new_table
       if df.empty:
           df = df0
       else:
           entities = [x for x in entities if x in new_column]
           c = ["Name_ID", "measurement"] + entities
           df1 = df[c]
           df1 = df1.loc[df1['measurement'].isin(measurement)]
           if what_table != 'long':
                df = pd.merge(df0, df1, on=["Name_ID", "measurement"])
           else:
                df_melt = df1.melt(id_vars=["Name_ID", "measurement"], var_name='Key', value_name="Value")
                df = pd.concat([df0, df_melt]).fillna(0)

    if error:
        return render_template('data.html',
                               error=error,
                               block=block,
                               all_entities=all_entities,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               measurement=measurement,
                               measurement_filter=measurement_filter,
                               entities=entities,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               df_min_max=df_min_max
                               )

    df = filtering.checking_for_block(block, df, Name_ID, measurement_name)

    data.table_browser_entities = entities
    data.csv = df.to_csv(index=False)
    df = df.fillna("missing data")
    column = df.columns.tolist()

    column_change_name = []
    [column_change_name.append(i.replace('.','_')) for i in column]
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
                           all_measurement=all_measurement,
                           measurement=measurement,
                           measurement_filter=measurement_filter,
                           entities=entities,
                           name_column=column,
                           name=measurement_name,
                           start_date=start_date,
                           end_date=end_date,
                           what_table=what_table,
                           column=dict_of_column,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max
                           )


