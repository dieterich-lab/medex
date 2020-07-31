from flask import Blueprint, render_template, request
import plotly.express as px
import modules.load_data_postgre as ps
from webserver import rdb, all_numeric_entities, all_categorical_entities, all_subcategory_entities,all_visit


scatter_plot_page = Blueprint('scatter_plot', __name__,
                       template_folder='tepmlates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():

    return render_template('scatter_plot.html',
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               all_categorical_entities=all_categorical_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_visit=all_visit)


@scatter_plot_page.route('/scatter_plot', methods=['POST'])
def post_plots():

    # list selected data
    y_axis = request.form.get('y_axis')
    x_axis = request.form.get('x_axis')
    visit = request.form.get('visit')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    log_x = request.form.get('log_x')
    log_y = request.form.get('log_y')
    add_group_by = request.form.get('add_group_by') is not None


    # handling errors and load data from database
    error = None
    if visit == "Search entity":
        error = "Please select number of visit"
    elif not x_axis or not y_axis or x_axis == "Search entity" or y_axis == "Search entity":
        error = "Please select x_axis and y_axis"
    elif x_axis == y_axis:
        error = "You can't compare the same entity"
    elif how_to_plot == 'log' and  not log_x and  not log_y:
        error = "Please select type of log"
    elif add_group_by and categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities and add_group_by:
        error = "Please select subcategory"
    elif add_group_by and categorical_entities:
        numerical_df, error = ps.get_values([x_axis, y_axis],visit, rdb) if not error else (None, error)
        df, error= ps.get_cat_values(categorical_entities, subcategory_entities,visit, rdb)
        if not error:
            categorical_df = numerical_df.merge(df, on="Patient_ID").dropna()
            if len(categorical_df[categorical_entities]) == 0:
                error = "Category {} is empty".format(categorical_entities)
        else: (None, error)
    else:
        numeric_df, error = ps.get_values([x_axis, y_axis],visit, rdb)
        if not error:
            numeric_df = numeric_df.dropna()
            if len(numeric_df[x_axis]) == 0:
                error = "Category {} is empty".format(x_axis)
            elif len(numeric_df[y_axis]) == 0:
                error = "Category {} is empty".format(y_axis)
            elif len(numeric_df.index) == 0:
                error = "This two entities don't have common values"
        else: (None, error)


    if error:
        return render_template('scatter_plot.html',
                                error=error,
                                numeric_tab=True,
                                x_axis=x_axis,
                                y_axis=y_axis,
                                all_numeric_entities=all_numeric_entities,
                                all_categorical_entities=all_categorical_entities,
                                add_group_by=add_group_by,
                                all_subcategory_entities=all_subcategory_entities,
                                all_visit=all_visit)

    # Plot figure and convert to an HTML string representation


    if how_to_plot == 'linear':
        if add_group_by :
            fig = px.scatter(categorical_df, x=x_axis, y=y_axis, color=categorical_entities, hover_name='Patient_ID', template="plotly_white",
                                 trendline="ols")
        else:

            fig = px.scatter(numeric_df,x=x_axis, y=y_axis,hover_name = "Patient_ID", template = "plotly_white",trendline="ols")

    else:
        if log_x == 'log_x' and  log_y == 'log_y':
            if add_group_by:
                fig = px.scatter(categorical_df, x=x_axis, y=y_axis, color=categorical_entities, hover_name='Patient_ID',
                                 template="plotly_white",trendline="ols",log_x=True, log_y=True)

            else:
                fig = px.scatter(numeric_df, x=x_axis, y=y_axis, hover_name='Patient_ID', template="plotly_white",
                                 trendline="ols",log_x=True, log_y=True)
        elif log_x == 'log_x':
            if add_group_by:
                fig = px.scatter(categorical_df, x=x_axis, y=y_axis, color=categorical_entities, hover_name='Patient_ID',
                                 template="plotly_white", trendline="ols", log_x=True)

            else:
                fig = px.scatter(numeric_df, x=x_axis, y=y_axis, hover_name='Patient_ID', template="plotly_white",
                                 trendline="ols", log_x=True)
        elif log_y == 'log_y':
            if add_group_by:
                fig = px.scatter(categorical_df, x=x_axis, y=y_axis, color=categorical_entities, hover_name='Patient_ID',
                                 template="plotly_white", trendline="ols",  log_y=True)

            else:
                fig = px.scatter(numeric_df, x=x_axis, y=y_axis, hover_name='Patient_ID', template="plotly_white",
                                 trendline="ols", log_y=True)

    results = px.get_trendline_results(fig)

    fig.update_layout(
        title={
            'text': "Compare values of <b>" + x_axis + "</b> and <b>" + y_axis + "</b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig = fig.to_html()

    return render_template('scatter_plot.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_entities,
                           plot = fig,
                           visit2=visit,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           add_group_by=add_group_by,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit)


















