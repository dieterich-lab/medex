from flask import Blueprint, render_template, request
import pandas as pd
import json
import plotly
import plotly.graph_objs as go
import data_warehouse.redis_rwh as rwh

boxplot_page = Blueprint('boxplot', __name__,
                         template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)

    return render_template('boxplot.html', categorical_entities=all_categorical_entities,
                           numeric_entities=all_numeric_entities)


@boxplot_page.route('/boxplot', methods=['POST'])
def post_boxplots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    entity = request.form.get('entity')
    group_by = request.form.get('group_by')

    error = None
    if not entity or not group_by or entity == "Choose entity" or group_by == "Choose entity":
        error = "Please select entity and group by"
    
    # get joined numerical and categorical values
    if not error:
        numeric_df, error = rwh.get_joined_numeric_values([entity], rdb)
        categorical_df, error = rwh.get_joined_categorical_values([group_by], rdb) if not error else (None, error)
        error = "No data based on the selected entity '" + entity + "' and group '" + group_by + "'" if error else None
    if error:
        return render_template('boxplot.html',
                                error=error,
                                categorical_entities=all_categorical_entities,
                                numeric_entities=all_numeric_entities,
                                selected_entity=entity,
                                group_by=group_by,
                                )


    merged_df = pd.merge(numeric_df, categorical_df, how='inner', on='patient_id')
    min_val = numeric_df[entity].min()
    max_val = numeric_df[entity].max()
    data =[]
    groups = set(categorical_df[group_by].values.tolist())
    plot_series = []
    for group in sorted(groups):
        df = merged_df.loc[merged_df[group_by] == group]
        # print(df)
        values = df[entity].values.tolist()
        # print(entity, group, values[:10])
        if (values):
            data.append(go.Box(y=values, name =group))
            plot_series.append({
                'y': values,
                'type': "box",
                # 'opacity': 0.5,
                'name': group,
                })
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('boxplot.html',
                           categorical_entities=all_categorical_entities,
                           numeric_entities=all_numeric_entities,
                           selected_entity=entity,
                           group_by=group_by,
                           plot_series=plot_series,
                           plot = graphJSON,
                           min_val=min_val,
                           max_val=max_val,
                           )
