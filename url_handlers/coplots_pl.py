from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

coplots_plot_page = Blueprint('coplots_pl', __name__,
                         template_folder='templates')


@coplots_plot_page.route('/coplots_pl', methods=['GET'])
def get_coplots():
    
    # connection and load data from database
    from webserver import all_numeric_entities,all_categorical_entities

    return render_template('coplots_pl.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_entities)


@coplots_plot_page.route('/coplots_pl', methods=['POST'])
def post_coplots():
    
    # connection with database and load name of entities
    from webserver import rdb,all_numeric_entities,all_categorical_entities

    # get selected entities
    category1 = request.form.get('category1')
    category2 = request.form.get('category2')
    x_axis = request.form.get('x_axis')
    y_axis = request.form.get('y_axis')
    how_to_plot = request.form.get('how_to_plot')
    how_to_plot2 = request.form.get('how_to_plot2')
    selected_x_min = request.form.get('x_axis_min')
    selected_x_max = request.form.get('x_axis_max')
    selected_y_min = request.form.get('y_axis_min')
    selected_y_max = request.form.get('y_axis_max')
    select_scale = request.form.get('select_scale') is not None

    # handling errors and load data from database
    error = None
    if category1 is None or category1 == 'Search entity':
        error = 'Please select category1'
    elif category2 is None or category2 == 'Search entity':
        error = 'Please select category2'
    elif x_axis is None or x_axis == 'Search entity':
        error = 'Please select x_axis'
    elif y_axis is None or y_axis == 'Search entity':
        error = 'Please select y_axis'
    elif x_axis == y_axis and category1 == category2:
        error = "You can't compare the same entities and categories"
    elif x_axis == y_axis:
        error = "You can't compare the same entities for x and y axis"
    elif category1 == category2:
        error = "You can't compare the same category"
    if not error:
        num_data = ps.get_values([x_axis, y_axis], rdb) if not error else (None, error)
        cat_data = ps.get_cat_values([category1, category2], rdb) if not error else (None, error)
        data = num_data.merge(cat_data, on ="Patient_ID").dropna()
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





    data[category1+' '+category2] = data[category1]+ ' '+ data[category2]
    if how_to_plot2 == "linear":
        if how_to_plot == "single_plot":
            fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",color=category1+' '+category2,trendline="ols")
        else:
            fig = px.scatter(data,x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,template="plotly_white",color=category1+' '+category2,trendline="ols")
    else:
        if how_to_plot == "single_plot":
            fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",color=category1+' '+category2,trendline="ols",log_x=True, log_y=True)
        else:
            fig = px.scatter(data,x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,template="plotly_white",color=category1+' '+category2,trendline="ols",log_x=True, log_y=True)

    fig.update_layout(
        title={
            'text': "Compare values of <b>" + x_axis + "</b> and <b>" + y_axis + "</b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})



    fig = fig.to_html()
    return render_template('coplots_pl.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_entities,
                           category1=category1,
                           category2=category2,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           how_to_plot=how_to_plot,
                           select_scale=select_scale,
                           plot = fig,
                           x_min=x_min,
                           x_max=x_max,
                           y_min=y_min,
                           y_max=y_max)
