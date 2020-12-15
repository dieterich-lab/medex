from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import url_handlers.clustering_function as dwu
import url_handlers.UMAP as um
import plotly.express as px
import pandas as pd
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_measurement,all_entities,len_numeric,\
                        size_categorical,size_numeric,len_categorical,all_subcategory_entities,database, data,name,block
clustering_plot_page = Blueprint('clustering_pl', __name__,
                            template_folder='clustering_pl')

block = 'none'
@clustering_plot_page.route('/clustering', methods=['GET'])
def cluster():

    return render_template('clustering/clustering.html',
                           name=name,
                           block=block,
                           numeric_tab=True,
                           all_entities=all_entities,
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


@clustering_plot_page.route('/clustering', methods=['POST'])
def post_clustering():
    if 'cluster_numeric' in request.form:
        # get selected entities
        numeric_entities = request.form.getlist('numeric_entities')
        if block == 'none':
            measurement = all_measurement.values[0]
        else:
            measurement = request.form.get('measurement')

        # handling errors and load data from database
        error = None
        if measurement == "Search entity":
            error = "Please select number of {}".format(name)
        elif len(numeric_entities) > 1:
            df, error = ps.get_values_heatmap(numeric_entities,measurement, rdb)
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
            return render_template('clustering/clustering.html',
                                   name=name,
                                   block=block,
                                   numeric_tab=True,
                                   all_categorical_entities=all_categorical_entities,
                                   all_numeric_entities=all_numeric_entities,
                                   all_subcategory_entities=all_subcategory_entities,
                                   numeric_entities=numeric_entities,
                                   all_measurement=all_measurement,
                                   measurement=measurement,
                                   error=error)


        cluster_data, cluster_labels, df, error = dwu.cluster_numeric_fields(numeric_entities, df)


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
        df = df.sort_values(by=['cluster'])

        any_present = df.shape[0]
        all_present =  df.dropna().shape[0]

        df_c = df[numeric_entities]
        df_label = df['cluster'].values
        print(df_label)

        reducer,embedding=um.calculate(df_c.values, df_label)
        df_new = pd.DataFrame()
        df_new['x']=reducer.embedding_[:, 0]
        df_new['y']=reducer.embedding_[:, 1]
        df_new['cluster']=df_label

        fig = px.scatter(df_new, x='x', y='y', color='cluster',
                             template="plotly_white")

        fig = fig.to_html()



        data.g = df.to_csv(index=False)
        return render_template('clustering/clustering.html',
                               name=name,
                               block=block,
                               numeric_tab=True,
                               numeric_entities=numeric_entities,
                               all_categorical_entities=all_categorical_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               any_present=any_present,
                               all_present=all_present,
                               table_data=table_data,
                               all_measurement=all_measurement,
                               measurement=measurement,
                               table=df,
                               plot=fig,
                               error=error
                               )
    elif 'cluster_categorical' in request.form:

        categorical_entities = request.form.getlist('categorical_entities')
        measurement = request.form.get('measurement1')
        data2,error =ps.get_values_cat_heatmap(categorical_entities,measurement,rdb)

        if not categorical_entities:
            error = "Please select entities"
            return render_template('clustering/clustering.html',
                                   numeric_tab=True,
                                   block=block,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
                                   all_measurement=all_measurement,
                                   measurement=measurement,
                                   error=error,
                                   )

        if any([entity for entity in categorical_entities]):
            cluster_info = dwu.cluster_categorical_entities(categorical_entities,data2)

            distance,ccv, cat_rep_np, category_values, categorical_label_uses, cat_df = cluster_info
            print(distance.shape)
            any_present = cat_df.shape[0]
            all_present = cat_df.dropna().shape[0]
            label = cat_df['cluster'].values

            # df to dict
            cvv_dict = { }
            for key, value in ccv.items():
                normal_value = value.to_dict()
                cvv_dict[key] = normal_value
            reducer,embedding=um.calculate(distance, label)
            df_new = pd.DataFrame()
            df_new['x'] = reducer.embedding_[:, 0]
            df_new['y'] = reducer.embedding_[:, 1]
            df_new['cluster'] = label

            fig = px.scatter(df_new, x='x', y='y', color='cluster',
                             template="plotly_white")

            fig = fig.to_html()

        return render_template('clustering/clustering.html',
                               categorical_tab=True,
                               block=block,
                               all_numeric_entities=all_numeric_entities,
                               all_categorical_entities=all_categorical_entities,
                               selected_c_entities=categorical_entities,
                               all_measurement=all_measurement,
                               measurement=measurement,
                               plot_c =fig,
                               c_cluster_info=cluster_info,
                               all_present=all_present,
                               any_present=any_present,
                               ccv=cvv_dict,

                                   )
    elif 'cluster_mixed' in request.form:

        entities = request.form.getlist('mixed_entities')
        data3,error=ps.get_values_clustering(entities,rdb)
        df = df.fillna(value=np.nan)
        print(data3)
        if not entities:
            error = "Please select entities"
            return render_template('clustering/clustering.html',
                                    numeric_tab=True,
                                   block=block,
                                    all_numeric_entities=all_numeric_entities,
                                    all_categorical_entities=all_categorical_entities,
                                    error=error,
                                    )

        if any([entity for entity in entities]):
            cluster_info = dwu.cluster_mixed_entities(entities,data3)

            distance, categorical_label_uses, cat_df = cluster_info
            any_present = cat_df.shape[0]
            all_present = cat_df.dropna().shape[0]
            label = cat_df['cluster'].values
            print(label)

            reducer,embedding=um.calculate(distance, label)
            df_new = pd.DataFrame()
            df_new['x'] = reducer.embedding_[:, 0]
            df_new['y'] = reducer.embedding_[:, 1]
            df_new['cluster'] = label

            fig = px.scatter(df_new, x='x', y='y', color='cluster',
                             template="plotly_white")
            fig.show()
            fig = fig.to_html()


            # df to dict
            #cvv_dict = {}
            #for key, value in ccv.items():
            #    normal_value = value.to_dict()
            #    cvv_dict[key] = normal_value

            return render_template('clustering/clustering.html',
                                   categorical_tab=True,
                                   block=block,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_entities,
                                   all_entities=all_entities,
                                   entities=entities,
                                   c_cluster_info=cluster_info,
                                   all_present=all_present,
                                   any_present=any_present,
                                   plot=fig,
                                    )




