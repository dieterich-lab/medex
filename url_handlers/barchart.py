from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import collections
import pandas as pd
import json
import plotly
import plotly.graph_objs as go
import plotly.express as px


barchart_page = Blueprint('barchart', __name__,
                           template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    # connection with database and load name of entities
    from webserver import connect_db
    rdb = connect_db()
    all_categorical_entities = ps.get_categorical_entities(rdb)

    return render_template('barchart.html',
                           numeric_tab=True,
                           all_categorical_entities=all_categorical_entities)


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():
    # connection with database and load name of entities
    from webserver import connect_db
    rdb = connect_db()
    all_categorical_entities = ps.get_categorical_entities(rdb)

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
        entity_df = pd.DataFrame(columns=[entity], data=categorical_df[entity].dropna())
        list_of_values = set(entity_df[entity].unique())
        entity_values[entity] = {}
        for value in list_of_values:
            entity_values[entity][value] = len(entity_df.loc[entity_df[entity] == value])


    layout = go.Layout(
        barmode='stack',
        template = 'plotly_white'
    )
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])

    div = fig.to_html(full_html=False)

    data = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('barchart.html',
                           categorical_tab=True,
                           all_categorical_entities=all_categorical_entities,
                           plot = graphJSON,
                           ooo = div,
                           entity_values=entity_values,
                           selected_c_entities=selected_c_entities,
                           plot_series=plot_series
                           )
