from flask import Blueprint, render_template, request
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import json
import plotly

import data_warehouse.redis_rwh as rwh

coplots_plot_page = Blueprint('coplots_pl', __name__,
                         template_folder='templates')


@coplots_plot_page.route('/coplots_pl', methods=['GET'])
def get_coplots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    return render_template('coplots_pl.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_only_entities)


@coplots_plot_page.route('/coplots_pl', methods=['POST'])
def post_coplots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    category1 = request.form.get('category1')
    category2 = request.form.get('category2')
    x_axis = request.form.get('x_axis')
    y_axis = request.form.get('y_axis')
    how_to_plot = request.form.get('how_to_plot')
    selected_x_min = request.form.get('x_axis_min')
    selected_x_max = request.form.get('x_axis_max')
    selected_y_min = request.form.get('y_axis_min')
    selected_y_max = request.form.get('y_axis_max')
    select_scale = request.form.get('select_scale') is not None

    error_message = None
    if category1 is None or category1 == 'Choose entity':
        error_message = 'Please select category1'
    elif category2 is None or category2 == 'Choose entity':
        error_message = 'Please select category2'
    elif x_axis is None or x_axis == 'Choose entity':
        error_message = 'Please select x_axis'
    elif y_axis is None or y_axis == 'Choose entity':
        error_message = 'Please select y_axis'
    elif x_axis == y_axis and category1 == category2:
        error_message = "You can't compare the same entities and categories"
    elif x_axis == y_axis:
        error_message = "You can't compare the same entities for x and y axis"
    elif category1 == category2:
        error_message = "You can't compare the same category"
    # get joined categorical values
    if not error_message:
        categorical_df, error_message = rwh.get_joined_categorical_values([category1, category2], rdb)
        numeric_df, error = rwh.get_joined_numeric_values([x_axis, y_axis], rdb) if not error_message else (None, error_message)
        error_message = "No data based on the selected options" if error_message else None

    if error_message:
        return render_template('coplots_pl.html',
                               all_numeric_entities=all_numeric_entities,
                               categorical_entities=all_categorical_only_entities,
                               error=error_message,
                               category1=category1,
                               category2=category2,
                               x_axis=x_axis,
                               y_axis=y_axis,
                               how_to_plot=how_to_plot,
                               x_min=selected_x_min,
                               x_max=selected_x_max,
                               y_min=selected_y_min,
                               y_max=selected_y_max,
                               select_scale=select_scale)

    categorical_df = categorical_df.dropna()
    numeric_df = numeric_df.dropna()
    merged_df = pd.merge(numeric_df, categorical_df, how='inner', on='patient_id')
    print(categorical_df)


    x_min = merged_df[x_axis].min() if not select_scale else selected_x_min
    x_max = merged_df[x_axis].max() if not select_scale else selected_x_max
    y_min = merged_df[y_axis].min() if not select_scale else selected_y_min
    y_max = merged_df[y_axis].max() if not select_scale else selected_y_max


    category1_values = merged_df[category1].unique()
    category2_values = merged_df[category2].unique()

    fig = make_subplots(rows=len(category1_values), cols=len(category2_values), subplot_titles=('Plot 1', 'Plot 2',
                                                          'Plot 3', 'Plot 4'))
    count=0
    plot_series=[]
    plot_series2 = []
    data =[]
    d=0
    layout ={}
    for i,cat1_value in enumerate(category1_values):
        for j,cat2_value in enumerate(category2_values):
            count += 1
            df = merged_df.loc[(merged_df[category1] == cat1_value) & (merged_df[category2] == cat2_value)].dropna()
            df.columns = ['patient_id', 'x', 'y', 'cat1', 'cat2']
            fig.add_trace(go.Scatter(x=list(df['x']), y=list(df['y']), mode = 'markers'),row = (i+1), col=(j+1))
            data.append(go.Scatter(x=list(df['x']), y=list(df['y']), mode = 'markers'))
            plot_series.append({
                'x': list(df['x']),
                'y': list(df['y']),
                'mode': 'markers',
                'type': 'scatter',
                'xaxis': 'x{}'.format(count),
                'yaxis': 'y{}'.format(count),
                'name': '{}: {} <br /> {}: {}'.format(category1,cat1_value,category2 ,cat2_value),
                'text': list(df['patient_id'])
            })
            plot_series2.append({
                'x': list(df['x']),
                'y': list(df['y']),
                'mode': 'markers',
                'type': 'scatter',
                'name': '{}: {} <br /> {}: {}'.format(category1, cat1_value, category2, cat2_value),
                'text': list(df['patient_id'])
            }
            )
            layout.update({
                'xaxis{}'.format(count): {
                    'title': {
                        'text': x_axis,
                    }
                },
                'yaxis{}'.format(count): {
                    'title': {
                        'text': y_axis,
                    }
                },})

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    layout.update(title='Compare values of <b>' + x_axis + '</b> and <b>' + y_axis + '</b>')
    layout['grid'] = {'rows': len(category1_values), 'columns': len(category2_values), 'pattern': 'independent'}


    return render_template('coplots_pl.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_entities,
                           category1=category1,
                           category2=category2,
                           cat1_values=list(category1_values),
                           cat2_values=list(category2_values),
                           x_axis=x_axis,
                           y_axis=y_axis,
                           layout =layout,
                           how_to_plot=how_to_plot,
                           plot_series=plot_series,
                           plot_series2=plot_series2,
                           fig =graphJSON,
                           select_scale=select_scale,
                           x_min=x_min,
                           x_max=x_max,
                           y_min=y_min,
                           y_max=y_max)
