from flask import Blueprint, render_template, request
import numpy as np

import data_warehouse.redis_rwh as rwh
import data_warehouse.data_warehouse_utils as dwu

clustering_page = Blueprint('clustering', __name__,
                            template_folder='clustering')


@clustering_page.route('/clustering', methods=['GET'])
def cluster():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    # numeric_df = rwh.get_joined_numeric_values(all_numeric_entities, rdb)
    #
    # min_values = numeric_df.min()
    # max_values = numeric_df.max()

    min_max_values = { }
    # for entity in all_numeric_entities:
    #     min_max_values[entity] = {
    #         'min': min_values[entity],
    #         'max': max_values[entity],
    #         'step': (max_values[entity] - min_values[entity]) / 100.0
    #     }
    return render_template('clustering/clustering.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_only_entities,
                           min_max_values=min_max_values,
                           )


@clustering_page.route('/clustering', methods=['POST'])
def post_clustering():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))
    min_max_values = { }

    if 'cluster_numeric' in request.form:
        # transforming back underscores to dots
        numeric_entities_with_underscore = request.form.getlist('numeric_entities')
        numeric_entities = [entity.replace('__', '.') for entity in numeric_entities_with_underscore]
        if not numeric_entities:
            error = "Please select entities"
            return render_template('clustering/clustering.html',
                                   numeric_tab=True,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
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
            np.random.seed(8675309)  # what is this number?
            cluster_data, cluster_labels, df, error = dwu.cluster_numeric_fields(
                    numeric_entities,
                    rdb,
                    standardize=numeric_standardize,
                    missing=numeric_missing,
                    min_max_filter=min_max_filter,
                    )
            if error:
                return render_template('clustering/clustering.html',
                                    numeric_tab=True,
                                    selected_n_entities=numeric_entities,
                                    all_numeric_entities=all_numeric_entities,
                                    all_categorical_entities=all_categorical_only_entities,
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
                plot_data.append({ "name": "Cluster {}".format(cluster), "data": entity_series })
            any_present = df.shape[0]
            all_present = df.dropna().shape[0]
            return render_template('clustering/clustering.html',
                                   numeric_tab=True,
                                   selected_n_entities=numeric_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
                                   any_present=any_present,
                                   all_present=all_present,
                                   table_data=table_data,
                                   plot_data=plot_data,
                                   min_max_values=min_max_values,
                                   selected_min_max=min_max_filter,
                                   )

    elif 'cluster_categorical' in request.form:
        eps = float(request.form['eps'])
        min_samples = int(request.form['min_samples'])
        categorical_entities = request.form.getlist('categorical_entities')
        if not categorical_entities:
            error = "Please select entities"
            return render_template('clustering/clustering.html',
                                   numeric_tab=True,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
                                   min_max_values=min_max_values,
                                   error=error,
                                   )

        if any([entity for entity in categorical_entities]):
            eps = eps
            min_samples = min_samples
            np.random.seed(8675309)
            cluster_info = dwu.cluster_categorical_entities(
                    categorical_entities,
                    rdb,
                    eps=eps,
                    min_samples=min_samples
                    )

            ccv, cat_rep_np, category_values, categorical_label_uses, cat_df, error = cluster_info
            if error:
                return render_template('clustering/clustering.html',
                                   categorical_tab=True,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
                                   selected_c_entities=categorical_entities,
                                   c_cluster_info=cluster_info,
                                   min_max_values=min_max_values,
                                   error=error
                                   )
            any_present = cat_df.shape[0]
            all_present = cat_df.dropna().shape[0]

            # df to dict
            cvv_dict = { }
            for key, value in ccv.items():
                normal_value = value.to_dict()
                cvv_dict[key] = normal_value

            return render_template('clustering/clustering.html',
                                   categorical_tab=True,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
                                   selected_c_entities=categorical_entities,
                                   c_cluster_info=cluster_info,
                                   all_present=all_present,
                                   any_present=any_present,
                                   ccv=cvv_dict,
                                   min_max_values=min_max_values,
                                   )
            # heat_map_data=data)
