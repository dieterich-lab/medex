from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps


coplots_plot_page = Blueprint('coplots_pl', __name__,
                         template_folder='templates')


@coplots_plot_page.route('/coplots_pl', methods=['GET'])
def get_coplots():
    
    # connection and load data from database
    from webserver import get_db2
    rdb = get_db2()
    all_numeric_entities = ps.get_numeric_entities(rdb)
    all_categorical_entities = ps.get_categorical_entities(rdb)

    return render_template('coplots_pl.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_entities)


@coplots_plot_page.route('/coplots_pl', methods=['POST'])
def post_coplots():
    
    # connection with database and load name of entities
    from webserver import get_db2
    rdb = get_db2()
    all_numeric_entities = ps.get_numeric_entities(rdb)
    all_categorical_entities = ps.get_categorical_entities(rdb)

    # get selected entities
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

    # handling errors and load data from database
    error = None
    if category1 is None or category1 == 'Choose entity':
        error = 'Please select category1'
    elif category2 is None or category2 == 'Choose entity':
        error = 'Please select category2'
    elif x_axis is None or x_axis == 'Choose entity':
        error = 'Please select x_axis'
    elif y_axis is None or y_axis == 'Choose entity':
        error = 'Please select y_axis'
    elif x_axis == y_axis and category1 == category2:
        error = "You can't compare the same entities and categories"
    elif x_axis == y_axis:
        error = "You can't compare the same entities for x and y axis"
    elif category1 == category2:
        error = "You can't compare the same category"
    if not error:
        data = ps.get_values([x_axis, y_axis,category1, category2], rdb) if not error else (None, error)
        if len(data.index) == 0:
            error = "No data based on the selected options"

    if error:
        return render_template('coplots_pl.html',
                               all_numeric_entities=all_numeric_entities,
                               categorical_entities=all_categorical_entities,
                               error=error,
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


    x_min = data[x_axis].min() if not select_scale else selected_x_min
    x_max = data[x_axis].max() if not select_scale else selected_x_max
    y_min = data[y_axis].min() if not select_scale else selected_y_min
    y_max = data[y_axis].max() if not select_scale else selected_y_max


    category1_values = set(data[category1].values.tolist())
    category2_values = set(data[category2].values.tolist())

    count=0
    plot_series=[]
    plot_series2 = []
    layout ={}
    for i,cat1_value in enumerate(category1_values):
        for j,cat2_value in enumerate(category2_values):
            count += 1
            df = data.loc[(data[category1] == cat1_value) & (data[category2] == cat2_value)].dropna()
            df.columns = ['patient_id', 'x', 'y', 'cat1', 'cat2']

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
                           layout=layout,
                           how_to_plot=how_to_plot,
                           plot_series=plot_series,
                           plot_series2=plot_series2,
                           select_scale=select_scale,
                           x_min=x_min,
                           x_max=x_max,
                           y_min=y_min,
                           y_max=y_max)
