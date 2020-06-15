from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px

boxplot_page = Blueprint('boxplot', __name__,
                         template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():

    # connection and load data from database
    from webserver import all_numeric_entities,all_categorical_entities


    return render_template('boxplot.html',
                           categorical_entities=all_categorical_entities,
                           numeric_entities=all_numeric_entities)


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():
    # connection with database and load name of entities
    from webserver import rdb,all_numeric_entities,all_categorical_entities


    # get selected entities
    entity = request.form.get('numeric_entities')
    group_by = request.form.get('group_by')
    how_to_plot = request.form.get('how_to_plot')

    # handling errors and load data from database
    error = None
    if not entity or not group_by or entity == "Search entity" or group_by == "Search entity":
        error = "Please select entity and group by"
    if not error:
        numeric_df = ps.get_num_cat_values([entity],[group_by], rdb).dropna()
        if len(numeric_df.index) == 0:
            error = "This two entities don't have common values"
    if error:
        return render_template('boxplot.html',
                                error=error,
                                categorical_entities=all_categorical_entities,
                                numeric_entities=all_numeric_entities,
                                selected_entity=entity,
                                group_by=group_by,
                                )




    if how_to_plot == 'linear':
        fig = px.box(numeric_df, x=group_by, y=entity,color=group_by,template="plotly_white")
    else :
        fig = px.box(numeric_df, x=group_by, y=entity, color=group_by, template="plotly_white", log_y=True)

    fig = fig.to_html()


    return render_template('boxplot.html',
                           categorical_entities=all_categorical_entities,
                           numeric_entities=all_numeric_entities,
                           selected_entity=entity,
                           group_by=group_by,
                           plot =fig
                           )
