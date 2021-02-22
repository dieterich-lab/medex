from flask import Blueprint, render_template, request,jsonify
import modules.load_data_postgre as ps
from webserver import rdb, all_entities, len_numeric, size_categorical, size_numeric, len_categorical, database, data,\
    Name_ID, measurement_name, block, table_builder, all_numeric_entities, all_categorical_entities_sc,\
    all_subcategory_entities

data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data/data1', methods=['GET','POST'])
def get_data():
    df = data.dict
    table_schema = data.table_schema
    dat = table_builder.collect_data_serverside(request, df, table_schema)
    return jsonify(dat)


@data_page.route('/data', methods=['GET'])
def get_data2():
    categorical_filter = data.categorical_filter
    categorical_names = data.categorical_names
    number_filter = 0
    if categorical_filter:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)
    return render_template('data.html',
                           all_entities=all_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_subcategory_entities=all_subcategory_entities,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           filter=categorical_filter,
                           number_filter=number_filter)


@data_page.route('/data', methods=['POST'])
def post_data2():
    # get selected entities
    id_filter = data.id_filter
    entities = request.form.getlist('entities')

    data.table_browser_entities = entities
    what_table = request.form.get('what_table')
    if 'filter' in request.form or 'all_categorical_filter' in request.form:
        categorical_filter = request.form.getlist('filter')
        categorical_names = request.form.getlist('cat')
        data.categorical_filter = categorical_filter
        data.categorical_names = categorical_names
    categorical_filter = data.categorical_filter
    categorical_names = data.categorical_names
    number_filter = 0

    if len(entities) == 0:
        error = "Please select entities"
    else:
       df, error = ps.get_data(entities, what_table, categorical_filter,categorical_names,id_filter,rdb)
    if categorical_filter is not None:
        number_filter = len(categorical_filter)
        categorical_filter = zip(categorical_names, categorical_filter)
    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities_sc,
                               entities=entities,
                               filter=categorical_filter,
                               number_filter=number_filter,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                               )

    if block == 'none':
        df = df.drop(columns=['measurement'])
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID)})
    else:
        df = df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})

    data.csv = df.to_csv(index=False)
    column = df.columns.tolist()

    column_change_name=[]
    [column_change_name.append(i.replace('.','_')) for i in column]
    df.columns = column_change_name

    data.dict = df.to_dict("records")
    dictOfcolumn = []
    table_schema = []

    [dictOfcolumn.append({'data': column_change_name[i]}) for i in range(0, len(column_change_name))]
    [table_schema.append({'data_name': column_change_name[i],'column_name': column_change_name[i],"default": "","order": 1,"searchable": True}) for i in range(0, len(column_change_name))]
    data.table_schema = table_schema

    data.table_browser_column = column
    data.table_browser_what_table = what_table
    data.table_browser_column2 = dictOfcolumn

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities_sc,
                           entities=entities,
                           name=column,
                           what_table=what_table,
                           column=dictOfcolumn,
                           filter=categorical_filter,
                           number_filter=number_filter,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           )



