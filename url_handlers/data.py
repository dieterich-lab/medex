from flask import Blueprint, render_template, request,jsonify
import modules.load_data_postgre as ps
from serverside.serverside_table import ServerSideTable
from serverside import table_schemas
from webserver import rdb, all_entities, len_numeric, size_categorical, size_numeric, len_categorical, database, data,name,name2,block,table_builder

data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data/data1', methods=['GET', 'POST'])
def get_data():
    datu = data.dict
    table_schema=data.table_schema
    dat = table_builder.collect_data_serverside(request,datu,table_schema)
    return jsonify(dat)


@data_page.route('/data', methods=['GET'])
def get_data2():

    return render_template('data.html',
                           all_entities=all_entities,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,

                           )


@data_page.route('/data', methods=['POST'])
def post_data2():
    # get selected entities

    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')

    if len(entities) == 0:
        error = "Please select entities"
    else:
       df, error = ps.get_data(entities, what_table, rdb)

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               entities=entities)

    if block == 'none':
        df=df.drop(columns=['measurement'])
    else:
        df = df.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})

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

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           entities=entities,
                           name=column,
                           what_table=what_table,
                           column=dictOfcolumn
                           )



