from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
from webserver import rdb, all_entities, len_numeric, size_categorical, size_numeric, len_categorical, database, data,name,name2,block
data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data', methods=['GET'])
def get_data():

    return render_template('data.html',
                           all_entities=all_entities,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,

                           )


@data_page.route('/data', methods=['POST'])
def post_data():
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

    data.g = df.to_csv(index=False)

    column = df.columns.tolist()
    df = df.to_json(orient="values")

    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           what_table=what_table,
                           entities=entities,
                           df=df,
                           name=column)



