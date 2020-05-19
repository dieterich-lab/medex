from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps

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

    # handling errors and load data from database
    error = None
    if not entity or not group_by or entity == "Choose entity" or group_by == "Choose entity":
        error = "Please select entity and group by"
    if not error:
        numeric_df = ps.get_num_cat_values([entity],[group_by], rdb)
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


    
    min_val = numeric_df[entity].min()
    max_val = numeric_df[entity].max()
    data =[]
    fig =[]
    groups = set(numeric_df[group_by].values.tolist())
    plot_series = []
    for group in sorted(groups):
        df = numeric_df.loc[numeric_df[group_by] == group]
        values = df[entity].values.tolist()
        if (values):
#           data.append(go.Box(y=values, name =group))
            plot_series.append({
                'y': values,
                'type': "box",
                'name': group,
                })
#    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('boxplot.html',
                           categorical_entities=all_categorical_entities,
                           numeric_entities=all_numeric_entities,
                           selected_entity=entity,
                           group_by=group_by,
                           plot_series=plot_series,
#                           plot = graphJSON,
                           min_val=min_val,
                           max_val=max_val,
                           )
