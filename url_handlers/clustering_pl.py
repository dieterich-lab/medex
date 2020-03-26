from flask import Blueprint, render_template, request
import numpy as np
import modules.load_data_postgre as ps

import data_warehouse.redis_rwh as rwh
import data_warehouse.data_warehouse_utils as dwu

clustering_plot_page = Blueprint('clustering_pl', __name__,
                            template_folder='clustering_pl')


@clustering_plot_page.route('/clustering_pl', methods=['GET'])
def cluster():
    # this import has to be here!!
    from webserver import get_db2
    rdb = get_db2()
    all_numeric_entities = ps.get_numeric_entities(rdb)

    min_max_values = { }

    return render_template('clustering_pl.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           min_max_values=min_max_values,
                           )


@clustering_plot_page.route('/clustering_pl', methods=['POST'])
def post_clustering():
    # this import has to be here!!
    from webserver import get_db2
    rdb = get_db2()
    all_numeric_entities = ps.get_numeric_entities(rdb)
    min_max_values = { }


    # transforming back underscores to dots
    numeric_entities_with_underscore = request.form.getlist('numeric_entities')
    numeric_entities = [entity.replace('__', '.') for entity in numeric_entities_with_underscore]
    if not numeric_entities:
        error = "Please select entities"
        return render_template('clustering_pl.html',
                                numeric_tab=True,
                                all_numeric_entities=all_numeric_entities,
                                min_max_values=min_max_values,
                                error=error,
                                )

    numeric_standardize = request.form['n_standardize'] == "yes"
    numeric_missing = request.form['n_missing']
    min_max_filter = { }
    for entity in numeric_entities:
        min_max_entity = 'min_max_{}'.format(entity.replace('.', '__'))
        if min_max_entity in request.form:
            min_value, max_value = list(eval(request.form.get(min_max_entity)))
            min_max_filter[entity] = min_value, max_value

            min_max_values[entity] = {
                'min' : min_value,
                'max' : max_value,
                'step': (max_value - min_value) / float(100),
                }

    if any([entity for entity in numeric_entities]):
        error = None
        df = ps.get_values(numeric_entities, rdb) if not error else (None, error)
        if len(df.index) == 0:
            error = "This two entities don't have common values"

        cluster_data, cluster_labels, df, error = dwu.cluster_numeric_fields(
                numeric_entities,
                df,
                standardize=numeric_standardize,
                missing=numeric_missing
                )
        if error:
            return render_template('clustering_pl.html',
                                numeric_tab=True,
                                selected_n_entities=numeric_entities,
                                all_numeric_entities=all_numeric_entities,
                                min_max_values=min_max_values,
                                selected_min_max=min_max_filter,
                                error=error,
                                )
        table_data = { }
        plot_data = []

        for cluster in sorted(cluster_labels.keys()):
            patient_count = cluster_labels[cluster]
            patient_percent = "{:.0%}".format(cluster_data.weights_[cluster])

            table_data[cluster] = { }
            table_data[cluster]['patient_count'] = patient_count
            table_data[cluster]['patient_percent'] = patient_percent
            for i, entity in enumerate(numeric_entities):
                mean_value = "{0:.2f}".format(cluster_data.means_[cluster][i])
                table_data[cluster][entity] = mean_value
                # filter by cluster
            entity_series = df[df.cluster == cluster][numeric_entities].dropna().values.round(2).tolist()
            plot_data.append({"name": "Cluster {}".format(cluster), "data": entity_series})
            plot_data.append({
                'x': list(df[df.cluster == cluster][numeric_entities[0]]),
                'y': list(df[df.cluster == cluster][numeric_entities[1]]),
                'mode': 'markers',
                'type': 'scatter',
                "name": "Cluster {}".format(cluster),
            })

        any_present = df.shape[0]
        all_present = df.dropna().shape[0]

        return render_template('clustering_pl.html',
                                numeric_tab=True,
                                selected_n_entities=numeric_entities,
                                all_numeric_entities=all_numeric_entities,
                                any_present=any_present,
                                all_present=all_present,
                                table_data=table_data,
                                plot_data=plot_data,
                                min_max_values=min_max_values,
                                selected_min_max=min_max_filter,
                                )


