from flask import Blueprint, render_template, request, jsonify
import numpy as np
import modules.load_data_postgre as ps


scatter_plot_page = Blueprint('scatter_plot', __name__,
                       template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():

    # connection and load data from database
    from webserver import connect_db
    rdb = connect_db()
    all_numeric_entities = ps.get_numeric_entities(rdb)
    all_categorical_entities = ps.get_categorical_entities(rdb)

    return render_template('scatter_plot.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities)


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():
    # connection with database and load name of entities
    from webserver import connect_db
    rdb = connect_db()
    all_numeric_entities = ps.get_numeric_entities(rdb)
    all_categorical_entities = ps.get_categorical_entities(rdb)


    # list selected data
    y_axis = request.form.get('y_axis')
    x_axis = request.form.get('x_axis')
    category = request.form.get('category')
    add_group_by = request.form.get('add_group_by') is not None


    # handling errors and load data from database
    error = None
    if not x_axis or not y_axis or x_axis == "Choose entity" or y_axis == "Choose entity":
        error = "Please select x_axis and y_axis"
    elif x_axis == y_axis:
        error = "You can't compare the same entity"

    numeric_df = ps.get_values([x_axis, y_axis], rdb) if not error else (None, error)
    if len(numeric_df[x_axis]) == 0:
        error = "Category {} is empty".format(x_axis)
    elif len(numeric_df[y_axis]) == 0:
        error = "Category {} is empty".format(y_axis)
    elif len(numeric_df.index) == 0:
        error = "This two entities don't have common values"


    if add_group_by and category == "Choose entity":
        error = "Please select a categorical value to group by"
    elif add_group_by and category:
        categorical_df = ps.get_values([x_axis, y_axis,category], rdb) if not error else (None, error)
        if len(categorical_df[category]) == 0:
            error = "Category {} is empty".format(category)



    if error:
        return render_template('scatter_plot.html',
                                error=error,
                                numeric_tab=True,
                                x_axis=x_axis,
                                y_axis=y_axis,
                                category=category,
                                all_numeric_entities=all_numeric_entities,
                                all_categorical_entities=all_categorical_entities,
                                add_group_by=add_group_by)


    i=0
    plot_series = []
    if not add_group_by:
        i+=1

        #straight line matching
        numeric_df.columns = ['patient_id','x', 'y']
        m, b = np.polyfit(np.array(numeric_df['x']), np.array(numeric_df['y']), 1)
        bestfit_y = (np.array(numeric_df['x']) * m + b)

        #plot seria for Plotly
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

        groups = set(categorical_df[category].values.tolist())
        for group in groups:

            colorGen = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                       'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                       'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                       'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                       'rgb(188, 189, 34)', 'rgb(23, 190, 207)']

            df = categorical_df.loc[(categorical_df[category] == group)].dropna()
            df.columns = ['patient_id', 'x', 'y', 'cat']
            # fit lin to data to plot
            m, b = np.polyfit(np.array(df['x']), np.array(df['y']), 1)
            bestfit_y = (np.array(df['x']) * m + b)
            i += 1

            # plot seria for Plotly
            plot_series.append({
                'x': list(df['x']),
                'y': list(df['y']),
                'mode': 'markers',
                'type': 'scatter',
                'name': group,
                'text': list(df['patient_id']),
                'marker' : {'color': colorGen[i]}
            })


            plot_series.append({
                'x': list(df['x']),
                'y': list(bestfit_y),
                'type': 'scatter',
                'name' : 'Linear regression {0}: <br /> (y={1:.2f}x + {2:.2f})'.format(group, m, b),
                'mode' : 'lines',
                'line' : {'color' : colorGen[i]}
            })



    return render_template('scatter_plot.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           category=category,
                           add_group_by=add_group_by,
                           plot_series=plot_series)


















