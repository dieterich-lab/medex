from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import url_handlers.clustering_function as dwu
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_visit
clustering_plot_page = Blueprint('clustering_pl', __name__,
                            template_folder='clustering_pl')


@clustering_plot_page.route('/clustering_pl', methods=['GET'])
def cluster():

    return render_template('clustering_pl.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_visit=all_visit
                           )


@clustering_plot_page.route('/clustering_pl', methods=['POST'])
def post_clustering():
    # get selected entities
    numeric_entities = request.form.getlist('numeric_entities')
    visit = request.form.get('visit')

    # handling errors and load data from database
    error = None
    if visit == "Search entity":
        error = "Please select number of visit"
    elif len(numeric_entities) > 1:
        df, error = ps.get_values(numeric_entities,visit, rdb)
        for i in numeric_entities:
            if not i in df.columns:
                numeric_entities.remove(i)
                error = "Entity: {} doesn't exist".format(i)
        if not error:
            df = df.dropna()
            if len(df.index) == 0:
                error = "This two entities don't have common values"
        else: (None, error)
    elif len (numeric_entities) < 2:
        error = "Please select more then one category"
    else:
        error = "Please select numeric entities"
    if error:
        return render_template('heatmap.html',
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               numeric_entities=numeric_entities,
                               all_visit=all_visit,
                               visit=visit,
                               error=error)



    cluster_data, cluster_labels, df, error = dwu.cluster_numeric_fields(numeric_entities,df)

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
                            numeric_entities=numeric_entities,
                            all_numeric_entities=all_numeric_entities,
                            any_present=any_present,
                            all_present=all_present,
                            table_data=table_data,
                            all_visit=all_visit,
                            visit=visit,
                            plot_data=plot_data,
                            error=error
                           )


