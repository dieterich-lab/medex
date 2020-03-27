from flask import Blueprint, render_template, request, jsonify
import numpy as np
import pandas as pd
import json


import data_warehouse.redis_rwh as rwh

scatter_plot_page = Blueprint('scatter_plot', __name__,
                       template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    return render_template('scatter_plot.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_only_entities)


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))


    y_axis = request.form.get('y_axis')
    x_axis = request.form.get('x_axis')
    category = request.form.get('category')
    add_group_by = request.form.get('add_group_by') is not None
    add_separate_regression = request.form.get('add_separate_regression') is not None


    error = None
    if not x_axis or not y_axis or x_axis == "Choose entity" or y_axis == "Choose entity":
        error = "Please select x_axis and y_axis"
    elif x_axis == y_axis:
        error = "You can't compare the same entity"
    elif add_group_by and category == "Choose entity":
        error = "Please select a categorical value to group by"
    elif add_group_by and category:
        categorical_df, error = rwh.get_joined_categorical_values([category], rdb)
        error = "No data based on the selected entities ( " + ", ".join([category]) + " ) " if error else None

    numeric_df, error = rwh.get_joined_numeric_values([x_axis, y_axis], rdb) if not error else (None, error)

    if error:
        return render_template('scatter_plot.html',
                                error=error,
                                numeric_tab=True,
                                x_axis=x_axis,
                                y_axis=y_axis,
                                category=category,
                                all_numeric_entities=all_numeric_entities,
                                all_categorical_entities=all_categorical_only_entities,
                                add_group_by=add_group_by,
                                add_separate_regression=add_separate_regression)


    i=0
    if not add_group_by:
        i+=1
        plot_series = []
        # change columns order and drop NaN values (this will show only the patients with both values)
        numeric_df = numeric_df.dropna()[[x_axis, y_axis, 'patient_id']]
        # rename columns
        numeric_df.columns = ['x', 'y', 'patient_id']
        # data_to_plot = list(numeric_df.T.to_dict().values())
        # fit lin to data to plot
        m, b = np.polyfit(np.array(numeric_df['x']), np.array(numeric_df['y']), 1)
        bestfit_y = (np.array(numeric_df['x']) * m + b)

        plot_series.append({
            'x': list(numeric_df['x']),
            'y': list(numeric_df['y']),
            'mode': 'markers',
            'type': 'scatter',
            'name' : 'Patients',
            'text': list(numeric_df['patient_id']),
        })



        plot_series.append({
            'x': list(numeric_df['x']),
            'y': list(bestfit_y),
            'type': 'scatter',
            'name' : 'Linear regression: <br /> (y={0:.2f}x + {1:.2f})'.format(m, b)
        })
    else:
        numeric_df = numeric_df.dropna()
        categorical_df = categorical_df.dropna()
        merged_df = pd.merge(numeric_df, categorical_df, how='inner', on='patient_id')

        category_values = merged_df[category].unique()

        plot_series = []
        for cat_value in category_values:

            colorGen = [ 'rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                       'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                       'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                       'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                       'rgb(188, 189, 34)', 'rgb(23, 190, 207)']

            df = merged_df.loc[(merged_df[category] == cat_value)].dropna()
            df.columns = ['patient_id', 'x', 'y', 'cat']
            # fit lin to data to plot
            m, b = np.polyfit(np.array(df['x']), np.array(df['y']), 1)
            bestfit_y = (np.array(df['x']) * m + b)
            i += 1

            plot_series.append({
                'x': list(df['x']),
                'y': list(df['y']),
                'mode': 'markers',
                'type': 'scatter',
                'name': cat_value,
                'text': list(df['patient_id']),
                'marker' : {'color': colorGen[i]}
            })


            plot_series.append({
                'x': list(df['x']),
                'y': list(bestfit_y),
                'type': 'scatter',
                'name' : 'Linear regression {0}: <br /> (y={1:.2f}x + {2:.2f})'.format(cat_value, m, b),
                'mode' : 'lines',
                'line' : {'color' : colorGen[i]}
            })



    return render_template('scatter_plot.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_only_entities,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           add_group_by=add_group_by,
                           add_separate_regression=add_separate_regression,
                           plot_series=plot_series)


















