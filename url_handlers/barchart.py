from flask import Blueprint, render_template, request
import collections
import pandas as pd
import json
import plotly
import plotly.graph_objs as go

import data_warehouse.redis_rwh as rwh

barchart_page = Blueprint('barchart', __name__,
                           template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    return render_template('barchart.html',
                           numeric_tab=True,
                           all_categorical_entities=all_categorical_only_entities)


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))


    selected_entities = request.form.getlist('categorical_entities')
    category1 = request.form.get('category1')

    error = None
    if category1 is None:
        error = 'Please select category1'
    elif selected_entities is None:
        error = "Please select entities"
    if not error:
        categorical_df, c_error = rwh.get_joined_categorical_values(selected_entities, rdb)
        error = "No data based on the selected options " if error else None


    if error:
        return render_template('barchart.html',
                               categorical_tab=True,
                               all_categorical_entities=all_categorical_only_entities,
                               selected_c_entities=selected_entities,
                               error=error,
                               category1=category1
                               )

    entity_values = {}
    key =[]
    data =[]
    plot_series = []
    data = []
    for entity in selected_entities:
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



    print(key_c)
    layout = go.Layout(
        barmode='stack',
        template = 'plotly_white'
    )

    data = go.Figure(data=data, layout=layout)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('barchart.html',
                           categorical_tab=True,
                           all_categorical_entities=all_categorical_only_entities,
                           plot = graphJSON,
                           entity_values=entity_values,
                           category1=category1,
                           selected_c_entities=selected_entities,
                           plot_series=plot_series
                           )
