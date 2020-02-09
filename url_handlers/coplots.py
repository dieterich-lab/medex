from flask import Blueprint, render_template, request
import pandas as pd

import data_warehouse.redis_rwh as rwh

coplots_page = Blueprint('coplots', __name__,
                         template_folder='templates')


@coplots_page.route('/coplots', methods=['GET'])
def get_coplots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    return render_template('coplots.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_only_entities)


@coplots_page.route('/coplots', methods=['POST'])
def post_coplots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    plot_series = []
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
        numeric_df, error_message = rwh.get_joined_numeric_values([x_axis, y_axis], rdb) if not error_message else (None, error_message)
        error_message = "No data based on the selected options" if error_message else None

    if error_message:
        return render_template('coplots.html',
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

    x_min = merged_df[x_axis].min() if not select_scale else selected_x_min
    x_max = merged_df[x_axis].max() if not select_scale else selected_x_max
    y_min = merged_df[y_axis].min() if not select_scale else selected_y_min
    y_max = merged_df[y_axis].max() if not select_scale else selected_y_max

    category1_values = merged_df[category1].unique()
    category2_values = merged_df[category2].unique()
    if how_to_plot == 'single_plot':
        plot_series = []
    elif how_to_plot == 'multiple_plots':
        plot_series = { }
    for cat1_value in category1_values:
        for cat2_value in category2_values:
            df = merged_df.loc[(merged_df[category1] == cat1_value) & (merged_df[category2] == cat2_value)].dropna()
            df.columns = ['patient_id', 'x', 'y', 'cat1', 'cat2']
            series = {
                'name'          : '{}_{}'.format(cat1_value, cat2_value),
                'turboThreshold': len(df),
                'data'          : list(df.T.to_dict().values()),
                'cat1'          : cat1_value,
                'cat2'          : cat2_value,
                'series_length' : len(df),
                }
            if how_to_plot == 'single_plot':
                plot_series.append(series)
            elif how_to_plot == 'multiple_plots':
                plot_series['{}_{}'.format(cat1_value, cat2_value)] = series

    return render_template('coplots.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_entities,
                           category1=category1,
                           category2=category2,
                           cat1_values=list(category1_values),
                           cat2_values=list(category2_values),
                           x_axis=x_axis,
                           y_axis=y_axis,
                           how_to_plot=how_to_plot,
                           plot_series=plot_series,
                           select_scale=select_scale,
                           x_min=x_min,
                           x_max=x_max,
                           y_min=y_min,
                           y_max=y_max)
