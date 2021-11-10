from flask import Blueprint, render_template, request, jsonify, session
import modules.load_data_postgre as ps
import pandas as pd

import url_handlers.filtering as filtering
from webserver import rdb, data, Name_ID, measurement_name, block, table_builder, all_entities, df_min_max, measurement_name,\
    all_measurement

calculator_page = Blueprint('calculator', __name__, template_folder='templates')


@calculator_page.route('/calculator/table', methods=['GET', 'POST'])
def table_data():
    df = data.new_table_dict
    table_schema = data.new_table_schema
    dat = table_builder.collect_data_serverside(request, df, table_schema)
    return jsonify(dat)


@calculator_page.route('/calculator', methods=['GET'])
def get_data():
    numerical_filter = filtering.check_for_numerical_filter_get()
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    return render_template('calculator.html',
                           block=block,
                           all_entities=all_entities,
                           name=measurement_name,
                           start_date=session.get('start_date'),
                           end_date=session.get('end_date'),
                           measurement_filter=session.get('measurement_filter'),
                           numerical_filter=numerical_filter,
                           filter=categorical_filter)


@calculator_page.route('/calculator', methods=['POST'])
def post_data():

    # get filter
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip,measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # get selected entities
    entities1 = request.form.get('timestamp_entities1')
    entities2 = request.form.get('timestamp_entities2')
    column_name = request.form.get('column_name')

    # errors
    error = None
    if not entities1 or not entities2:
        error = "Please select entities "
    elif not column_name:
        error = "Please write new column name"
    else:
       df = ps.calculator(entities1, entities2, column_name,rdb)

    if error:
        return render_template('calculator.html',
                               error=error,
                               block=block,
                               all_entities=all_entities,
                               all_measurement=all_measurement,
                               name=measurement_name,
                               entities1=entities1,
                               entities2=entities2,
                               column_name=column_name,
                               measurement_filter=measurement_filter,
                               numerical_filter=numerical_filter,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               )


    df1 = data.new_table
    if df1.empty:
        data.new_table = df
    else:
        data.new_table = pd.merge(df, df1, on=["Name_ID", "measurement"],how='outer')
    data.csv_new_table = df.to_csv(index=False)
    new_column = session.get('new_column')
    if not new_column:
        new_column = []
    new_column.append(column_name)
    session['new_column'] = new_column


    column = df.columns.tolist()
    data.new_table_dict = df.to_dict("records")
    table_schema = []
    dict_of_column = []

    [dict_of_column.append({'data': column[i]}) for i in range(0, len(column))]
    [table_schema.append({'data_name':column[i], 'column_name': column[i], "default": "",
                          "order": 1, "searchable": True}) for i in range(0, len(column))]

    data.new_table_schema = table_schema

    return render_template('calculator.html',
                           error=error,
                           block=block,
                           all_entities=all_entities,
                           all_measurement=all_measurement,
                           entities1=entities1,
                           entities2=entities2,
                           column_name=column_name,
                           name_column=column,
                           column=dict_of_column,
                           measurement_filter=measurement_filter,
                           numerical_filter=numerical_filter,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip)