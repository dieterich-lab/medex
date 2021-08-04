from flask import Blueprint, render_template, request, jsonify, session
import modules.load_data_postgre as ps
import pandas as pd
import json
import url_handlers.filtering as filtering
from webserver import rdb, data, Name_ID, measurement_name, block, table_builder, all_categorical_entities,\
    all_subcategory_entities, all_numeric_entities,all_entities,df_min_max

data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data/data1', methods=['GET', 'POST'])
def table_data():
    df = data.dict
    table_schema = data.table_schema
    dat = table_builder.collect_data_serverside(request, df, table_schema)
    return jsonify(dat)


@data_page.route('/data', methods=['GET'])
def get_data():
    categorical_filter, categorical_names = filtering.check_for_filter_get(data)
    return render_template('data.html',
                           all_entities=all_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           filter=categorical_filter,
                           df_min_max=df_min_max)


@data_page.route('/data', methods=['POST'])
def post_data():

    # get selected entities
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')

    # get filter
    id_filter = data.id_filter
    categorical_filter, categorical_names, categorical_filter_zip = filtering.check_for_filter_post(data)

    # errors
    if len(entities) == 0:
        error = "Please select entities"
    else:
       df, error = ps.get_data(entities, what_table, categorical_filter, categorical_names, id_filter, rdb)

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities,
                               entities=entities,
                               filter=categorical_filter_zip,
                               )

    df = filtering.checking_for_block(block, df, Name_ID, measurement_name)

    data.table_browser_entities = entities
    data.csv = df.to_csv(index=False)
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
                           all_entities=all_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities,
                           entities=entities,
                           name=column,
                           what_table=what_table,
                           column=dict_of_column,
                           filter=categorical_filter_zip
                           )


