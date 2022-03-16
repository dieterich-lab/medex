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
    return render_template('calculator.html')


@calculator_page.route('/calculator', methods=['POST'])
def post_data():

    # get selected entities
    entities1 = request.form.get('timestamp_entities1')
    entities2 = request.form.get('timestamp_entities2')
    push = request.form.get('Push')

    if block == 'none':
        date_first_measurement = all_measurement[0]
        date_second_measurement = all_measurement[0]
    else:
        date_first_measurement = request.form.get('date_first_measurement')
        date_second_measurement = request.form.get('date_second_measurement')
    column_name = request.form.get('column_name')


    # errors
    error = None
    if push is None:
        if entities1 == 'Search entity' or entities2 == 'Search entity':
            error = "Please select entities "
        elif date_first_measurement == 'Search entity' or date_second_measurement == 'Search entity':
                error = "Please select entities "
        elif entities1 == entities2 and date_first_measurement == date_second_measurement:
            error = "Please select different entities"
        elif not column_name:
            error = "Please write new column name"
        else:
           df = ps.calculator(entities1, entities2, date_first_measurement, date_second_measurement, column_name, rdb)
           date = df['Date'][0]
           df.drop(columns=['Date'])
    if error:
        return render_template('calculator.html',
                               error=error,
                               name=measurement_name,
                               entities1=entities1,
                               entities2=entities2,
                               date_first_measurement=date_first_measurement,
                               date_second_measurement=date_second_measurement,
                               column_name=column_name
                               )
    if push is None:
        data.csv_new_table = df.to_csv(index=False)

        column = df.columns.tolist()
        data.column =column
        data.new_table_dict = df.to_dict("records")
        table_schema = []
        dict_of_column = []

        [dict_of_column.append({'data': column[i]}) for i in range(0, len(column))]
        [table_schema.append({'data_name':column[i], 'column_name': column[i], "default": "",
                              "order": 1, "searchable": True}) for i in range(0, len(column))]

        df['Case_ID'], df['measurement'], df['Date'], df['Time'], df['Key'] = '', all_measurement[
            0], date, '', column_name
        df = df.rename(columns={column_name: 'Value'})
        df['ID'] = df.index
        df = df[["ID", "Name_ID", "Case_ID", "measurement", "Date", "Time", "Key", "Value"]]
        data.dict =dict_of_column
        data.new_table_schema = table_schema
        data.df = df
    else:
        column = data.column
        dict_of_column = data.dict
        ps.push_to_numerical_table(column_name, data.df, rdb)

    return render_template('calculator.html',
                           entities1=entities1,
                           entities2=entities2,
                           column_name=column_name,
                           name_column=column,
                           date_first_measurement=date_first_measurement,
                           date_second_measurement=date_second_measurement,
                           column=dict_of_column)


@calculator_page.context_processor
def numerical_all():
    size_numerical_table, all_numeric_entities, df_min_max = ps.get_numeric_entities(rdb)
    all_numeric_entities = all_numeric_entities.to_dict('index')
    return dict(all_numeric_entities=all_numeric_entities)