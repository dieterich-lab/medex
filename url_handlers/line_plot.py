from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb, all_numeric_entities, all_categorical_entities, all_subcategory_entities,all_visit

line_plot_page = Blueprint('time_series', __name__,
                         template_folder='templates')


@line_plot_page.route('/line_plot', methods=['GET'])
def get_boxplots():

    return render_template('line_plot.html',
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit)


@line_plot_page.route('/line_plot', methods=['POST'])
def post_boxplots():
    # get selected entities
    numeric_entities = request.form.getlist('numeric_entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    visit = request.form.getlist('visit')
    add_group_by = request.form.get('add_group_by') is not None
    if how_to_plot == 'mean':
        how_to_plot ='AVG'
    # handling errors and load data from database
    error = None
    if numeric_entities == "Search entity":
        error = "Please select entity"
    elif add_group_by and categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities and add_group_by:
        error = "Please select subcategory"
    elif add_group_by and categorical_entities:
        numeric_df,error = ps.get_num_cat_values_mean(numeric_entities, categorical_entities, subcategory_entities,how_to_plot,rdb)
        if not error:
            numeric_df = numeric_df.dropna()
            if len(numeric_df.index) == 0:
                error = "This two entities don't have common values"
        else: (None, error)
    else:
        numeric_df2, error = ps.get_num_cat_values_mean_more_numeric(numeric_entities,how_to_plot, rdb)
        if not error:
            numeric_df = numeric_df2.dropna()
            if len(numeric_df.index) == 0:
                error = "This two entities don't have common values"
        else: (None, error)

    if error:
        return render_template('line_plot.html',
                               error=error,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_visit=all_visit,
                               numeric_entities=numeric_entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               add_group_by=add_group_by,
                               visit=visit)


    # Plot figure and convert to an HTML string representation
    error = None
    numeric_df = numeric_df.drop(columns=['Patient_ID'])
    numeric_entities = numeric_df.columns.tolist()

    if add_group_by:
        fig = px.scatter(numeric_df, x='Visit', y='Value',color=categorical_entities,facet_row='Key', template="plotly_white").update_traces(mode="lines+markers")
        fig.update_yaxes(matches=None)
        fig.update_layout(
            height=1000)
        fig = fig.to_html()

    else:
        fig = px.scatter(numeric_df2, x='Visit', y='Value', facet_row='Key',
                          template="plotly_white").update_traces(mode="lines+markers")
        fig.update_yaxes(matches=None)
        fig.update_layout(
            height=1000)
        fig = fig.to_html()





    return render_template('line_plot.html',
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit,
                           numeric_entities=numeric_entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           add_group_by=add_group_by,
                           visit=visit,
                           error=error,
                           plot=fig)