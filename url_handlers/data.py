from flask import Blueprint, render_template, request, g, send_file,session
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_visit,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,database,data
data_page = Blueprint('data', __name__,
                         template_folder='templates')
import time






@data_page.route('/data', methods=['GET'])
def get_data():

    return render_template('data.html',
                           all_entities=all_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical
    )


@data_page.route('/data', methods=['POST'])
def post_data():
    # get selected entities
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')

    if len(entities) == 0 :
        error = "Please select entities"
    else:
       start_time = time.time()
       df, error = ps.get_data2(entities,what_table, rdb)
       end_time = time.time()
       time3 = end_time - start_time
       print(time3)
    # handling errors and load data from database

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               entities=entities,
                               all_visit=all_visit)



    start_time = time.time()
    data.g =df.to_csv(index=False)
    end_time = time.time()
    time3 = end_time - start_time
    print(time3)

    start_time = time.time()
    N=len(df)
    if N > 999: error="The result table was limited due to its size, please limit your search query or use the download button."
    df=df.head(999)
    name = df.columns.tolist()
    df = df.to_json(orient="values")
    end_time = time.time()
    time3 = end_time - start_time
    print(time3)


    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           entities=entities,
                           N=N,
                           df=df,
                           name=name)



