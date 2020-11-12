from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_visit,all_entities
import numpy as np
data_page = Blueprint('data', __name__,
                         template_folder='templates')


@data_page.route('/data', methods=['GET'])
def get_data():

    return render_template('data.html',
                           all_entities=all_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,)


@data_page.route('/data', methods=['POST'])
def post_data():
    # get selected entities
    entities = request.form.getlist('entities')
    what_table = request.form.get('what_table')

    if len(entities) == 0 :
        error = "Please select entities"
    else:
       df, error = ps.get_data2(entities, rdb)
    # handling errors and load data from database

    if error:
        return render_template('data.html',
                               error=error,
                               all_entities=all_entities,
                               entities=entities,
                               all_visit=all_visit)

    if what_table == 'long':
        df1 = df
        N=len(df)
        if N > 999: error="The result table was limited due to its size, please limit your search query or use the download button."
        #df = df.to_dict()
        df=df.head(999)
        df = df.to_html(index=False, index_names=False, classes='display" id = "example').replace('border="1"','border="0"')

        df1 = df1.to_html(index=False, index_names=False)
    else:
        df = df.pivot_table(index=["Patient_ID", "Visit"], columns="Key", values="Value",
                                  aggfunc=min).reset_index()
        df1 = df
        N = len(df)
        if N > 999: error = "The result table was limited due to its size, please limit your search query or use the download button."
        df = df.head(999)
        df = df.to_html(index=False, index_names=False, classes='display" id = "example').replace('border="1"','border="0"')
        df1 = df1.to_html(index=False, index_names=False)
    return render_template('data.html',
                           error=error,
                           all_entities=all_entities,
                           entities=entities,
                           N=N,
                           df=df,
                           table=df1
                           )
