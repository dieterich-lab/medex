from flask import Blueprint, render_template, request
import plotly.express as px
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_measurement,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,all_subcategory_entities,database,name,name2,block


scatter_plot_page = Blueprint('scatter_plot', __name__, template_folder='tepmlates')

block = 'none'
@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():

    return render_template('scatter_plot.html',
                           name='{} number'.format(name),
                           block=block,
                           numeric_tab=True,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical
                           )


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():

    # list selected data
    y_axis = request.form.get('y_axis')
    x_axis = request.form.get('x_axis')

    if block == 'none':
        x_measurement = all_measurement.values[0]
        y_measurement = all_measurement.values[0]
    else:
        x_measurement = request.form.get('x_measurement')
        y_measurement = request.form.get('y_measurement')

    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    log_x = request.form.get('log_x')
    log_y = request.form.get('log_y')
    add_group_by = request.form.get('add_group_by') is not None

    # handling errors and load data from database
    error = None
    if x_measurement == "Search entity" or y_axis == "Search entity":
        error = "Please select number of {}".format(name)
    elif x_axis == "Search entity" or y_axis == "Search entity":
        error = "Please select x_axis and y_axis"
    elif x_axis == y_axis and x_measurement == y_measurement:
        error = "You can't compare the same entity"
    elif how_to_plot == 'log' and not log_x and not log_y:
        error = "Please select type of log"
    elif add_group_by and categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities and add_group_by:
        error = "Please select subcategory"
    elif add_group_by and categorical_entities:
        numerical_df, error = ps.get_values_scatter_plot(x_axis, y_axis,x_measurement,y_measurement, rdb)
        if x_axis == y_axis:
            x_axis_v = x_axis+'_x'
            y_axis_v = y_axis + '_y'
        else:
            x_axis_v = x_axis
            y_axis_v = y_axis
        if not error:
            df, error = ps.get_cat_values(categorical_entities, subcategory_entities, [x_measurement, y_measurement], rdb)
            if not error:
                categorical_df = numerical_df.merge(df, on="Name_ID").dropna()
                categorical_df = categorical_df.sort_values(by=[categorical_entities])
                categorical_df = categorical_df.rename(
                    columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})
                if len(categorical_df[categorical_entities]) == 0:
                    error = "Category {} is empty".format(categorical_entities)
    else:
        numeric_df, error = ps.get_values_scatter_plot(x_axis, y_axis,x_measurement,y_measurement, rdb)
        numeric_df = numeric_df.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})
        if x_axis == y_axis:
            x_axis_v = x_axis+'_x'
            y_axis_v = y_axis + '_y'
        else:
            x_axis_v = x_axis
            y_axis_v = y_axis
        if not error:
            numeric_df = numeric_df.dropna()
            if len(numeric_df[x_axis_v]) == 0:
                error = "Category {} is empty".format(x_axis)
            elif len(numeric_df[y_axis_v]) == 0:
                error = "Category {} is empty".format(y_axis)
            elif len(numeric_df.index) == 0:
                error = "This two entities don't have common values"

    if error:
        return render_template('scatter_plot.html',
                               name='{} number'.format(name),
                               block=block,
                               numeric_tab=True,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_measurement=all_measurement,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               add_group_by=add_group_by,
                               x_axis=x_axis,
                               y_axis=y_axis,
                               x_measurement=x_measurement,
                               y_measurement=y_measurement,
                               error=error,
                               )



    # Plot figure and convert to an HTML string representation
    if how_to_plot == 'linear':
        if add_group_by :
            fig = px.scatter(categorical_df, x=x_axis_v, y=y_axis_v, color=categorical_entities, hover_name=name2, template="plotly_white",
                                 trendline="ols")
        else:

            fig = px.scatter(numeric_df,x=x_axis_v, y=y_axis_v,hover_name = name2, template = "plotly_white",trendline="ols")

    else:
        if log_x == 'log_x' and log_y == 'log_y':
            if add_group_by:
                fig = px.scatter(categorical_df, x=x_axis_v, y=y_axis_v, color=categorical_entities, hover_name=name2,
                                 template="plotly_white",trendline="ols",log_x=True, log_y=True)

            else:
                fig = px.scatter(numeric_df, x=x_axis_v, y=y_axis_v, hover_name=name2, template="plotly_white",
                                 trendline="ols",log_x=True, log_y=True)
        elif log_x == 'log_x':
            if add_group_by:
                fig = px.scatter(categorical_df, x=x_axis_v, y=y_axis_v, color=categorical_entities, hover_name=name2,
                                 template="plotly_white", trendline="ols", log_x=True)

            else:
                fig = px.scatter(numeric_df, x=x_axis_v, y=y_axis_v, hover_name=name2, template="plotly_white",
                                 trendline="ols", log_x=True)
        elif log_y == 'log_y':
            if add_group_by:
                fig = px.scatter(categorical_df, x=x_axis_v, y=y_axis_v, color=categorical_entities, hover_name=name2,
                                 template="plotly_white", trendline="ols",  log_y=True)

            else:
                fig = px.scatter(numeric_df, x=x_axis_v, y=y_axis_v, hover_name=name2, template="plotly_white",
                                 trendline="ols", log_y=True)

#    results = px.get_trendline_results(fig)

    fig.update_layout(
        font=dict(size=16),
        title={
            'text': "Compare values of <b>" + x_axis + "</b> : "+ name +" <b>" + x_measurement + "</b> and <b>" + y_axis + "</b> : " + name + " <b>" + y_measurement + "</b> ",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig = fig.to_html()

    return render_template('scatter_plot.html',
                           name='{} number'.format(name),
                           block=block,
                           numeric_tab=True,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_measurement=all_measurement,
                           subcategory_entities=subcategory_entities,
                           categorical_entities=categorical_entities,
                           add_group_by=add_group_by,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           x_measurement=x_measurement,
                           y_measurement=y_measurement,
                           plot=fig
                           )


















