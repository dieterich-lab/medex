from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import collections
import json
import plotly
import plotly.graph_objs as go



barchart_page = Blueprint('barchart', __name__,
                           template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    # connection with database and load name of entities
    from webserver import all_numeric_entities,all_categorical_entities


    return render_template('barchart.html',
                           numeric_tab=True,
                           all_categorical_entities=all_categorical_entities)


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():
    # connection with database and load name of entities
    from webserver import rdb,all_numeric_entities,all_categorical_entities

    # list selected entities
    selected_c_entities = request.form.getlist('categorical_entities')

    # handling errors and load data from database
    error = None
    if not selected_c_entities:
        error = "Please select entities"
    elif selected_c_entities:
        categorical_df = ps.get_cat_values(selected_c_entities, rdb)



    if error:
        return render_template('barchart.html',
                               categorical_tab=True,
                               all_categorical_entities=all_categorical_entities,
                               selected_c_entities=selected_c_entities,
                               error=error
                               )

    entity_values = {}
    key =[]
    plot_series = []
    data = []
    for entity in selected_c_entities:
        counter = collections.Counter(categorical_df[entity])
        values_c = list(counter.values())
        key_c = list(counter.keys())
        key.append(list(counter.keys()))
        data.append(go.Bar(x=key_c, y=values_c, name=entity, width=0.3))
        plot_series.append({
            'x': key_c,
            'y': values_c,
            'name': entity,
            'type': "bar",
            'width': 0.3
        })


    layout = go.Layout(
        barmode='stack',
        template = 'plotly_white'
    )




    data = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('barchart.html',
                           categorical_tab=True,
                           all_categorical_entities=all_categorical_entities,
                           plot = graphJSON,
                           entity_values=entity_values,
                           selected_c_entities=selected_c_entities
                           )
