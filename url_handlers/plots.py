from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from scipy.stats import pearsonr

import data_warehouse.redis_rwh as rwh

plots_page = Blueprint('plots_stats', __name__,
                       template_folder='plots')


@plots_page.route('/plots', methods=['GET'])
# @login_required
def get_plots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    return render_template('plots/plots.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_only_entities)


@plots_page.route('/plots', methods=['POST'])
# @login_required
def post_plots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    if 'plot_numeric' in request.form:
        plot_type = request.form['plot_type']
        error = None
        if not plot_type or plot_type == 'select_plot':
            return render_template('plots/plots.html',
                                       error="Please select plot type",
                                       numeric_tab=True,
                                       all_numeric_entities=all_numeric_entities,
                                       all_categorical_entities=all_categorical_only_entities)

        elif plot_type == 'scatter_plot_n':
            x_axis = request.form.get('x_axis')
            y_axis = request.form.get('y_axis')
            if not x_axis or not y_axis or x_axis == "Choose entity" or y_axis == "Choose entity":
                error = "Please select x_axis and y_axis"

            if x_axis == y_axis:
                error = "You can't compare the same entity"
                return render_template('plots/plots.html',
                                       error=error,
                                       numeric_tab=True,
                                       all_numeric_entities=all_numeric_entities,
                                       all_categorical_entities=all_categorical_only_entities)
            
            numeric_df, err = rwh.get_joined_numeric_values([x_axis, y_axis], rdb) if not error else (None, error)
            error = "Parameter " + x_axis + " and " + y_axis + " do not contain any values. " + \
                    "Please select another parameter" if not error and err else error
                    
            if error:
                return render_template('plots/plots.html',
                                       error=error,
                                       numeric_tab=True,
                                       all_numeric_entities=all_numeric_entities,
                                       all_categorical_entities=all_categorical_only_entities)
            # change columns order and drop NaN values (this will show only the patients with both values)
            numeric_df = numeric_df.dropna()[[x_axis, y_axis, 'patient_id']]
            # rename columns
            numeric_df.columns = ['x', 'y', 'patient_id']
            data_to_plot = list(numeric_df.T.to_dict().values())
            # data_to_plot = numeric_df.values.tolist()
            return render_template('plots/plots.html',
                                   numeric_tab=True,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
                                   x_axis=x_axis,
                                   y_axis=y_axis,
                                   plot_data=data_to_plot,
                                   plot_type=plot_type)
        elif plot_type == 'heat_map_n':
            selected_entities = request.form.getlist('numeric_entities')
            if not selected_entities:
                error = "Please select entities"
                return render_template('plots/plots.html',
                                       numeric_tab=True,
                                       all_numeric_entities=all_numeric_entities,
                                       all_categorical_entities=all_categorical_only_entities,
                                       error=error)

            # 'diagnostik__labor__clump_thickness' -> 'diagnostik.labor.clump_thickness'
            selected_entities = [entity.replace('__', '.') for entity in selected_entities]

            min_max_filter = { }
            for entity in selected_entities:
                if 'min_max_{}'.format(entity.replace('.', '__')) in request.form:
                    min_max_value = list(eval(request.form['min_max_{}'.format(entity.replace('.', '__'))]))
                    min_max_filter[entity] = min_max_value
                
            numeric_df, err = rwh.get_joined_numeric_values(selected_entities, rdb, min_max_filter)
            if err:
                error = "The selected entities (" + ", ".join(selected_entities) + ") do not contain any values. "
                return render_template('plots/plots.html',
                                       error=error,
                                       numeric_tab=True,
                                       all_numeric_entities=all_numeric_entities,
                                       all_categorical_entities=all_categorical_only_entities)

            # remove patient id and drop NaN values (this will show only the patients with both values)
            numeric_df = numeric_df[selected_entities]
            # numeric_df = numeric_df.dropna()[selected_entities]
            dfcols = pd.DataFrame(columns=numeric_df.columns)
            pvalues = dfcols.transpose().join(dfcols, how='outer')
            corr_values = dfcols.transpose().join(dfcols, how='outer')
            for r in numeric_df.columns:
                for c in numeric_df.columns:
                    if c == r:
                        df_corr = numeric_df[[r]].dropna()
                    else:
                        df_corr = numeric_df[[r, c]].dropna()
                    corr_values[r][c], pvalues[r][c] = pearsonr(df_corr[r], df_corr[c])

            pvalues = pvalues.astype(float)
            pvalues = pvalues.round(decimals=3)
            pvalues = pvalues.T.values.tolist()

            corr_values = corr_values.astype(float)
            corr_values = corr_values.round(decimals=2)
            corr_values = corr_values.T.values.tolist()

            plot_data = []
            for i in range(len(corr_values)):
                for j in range(len(corr_values[i])):
                    # highcharts requires this format
                    plot_data.append({ 'x': i, 'y': j, 'value': corr_values[i][j], 'pvalue': pvalues[i][j] })

            min_max_values = { }
            min_values = numeric_df.min()
            max_values = numeric_df.max()
            for entity in selected_entities:
                min_max_values[entity] = {
                    'min' : min_values[entity],
                    'max' : max_values[entity],
                    'step': (max_values[entity] - min_values[entity]) / 100.0
                    }

            return render_template('plots/plots.html',
                                   numeric_tab=True,
                                   all_numeric_entities=all_numeric_entities,
                                   all_categorical_entities=all_categorical_only_entities,
                                   selected_n_entities=selected_entities,
                                   selected_min_max=min_max_filter,
                                   min_max_values=min_max_values,
                                   plot_type=plot_type,
                                   plot_data=plot_data,
                                   )

    if 'plot_categorical' in request.form:
        plot_type = request.form.get('plot_type')
        selected_entities = request.form.getlist('categorical_entities')
        error = None
        if selected_entities:
            categorical_df, c_error = rwh.get_joined_categorical_values(selected_entities, rdb)
            error = "No data based on the selected entities ( " + ", ".join(selected_entities) + " ) " if c_error else None 
        else:
            error = "Please select entities"

        
        if error:
            return render_template('plots/plots.html',
                        categorical_tab=True,
                        all_numeric_entities=all_numeric_entities,
                        selected_c_entities=selected_entities,
                        all_categorical_entities=all_categorical_only_entities,
                        error=error)


        entity_values = { }
        if plot_type == "simple":
            x_categories = None
            for entity in selected_entities:
                entity_df = pd.DataFrame(columns=[entity], data=categorical_df[entity].dropna())
                list_of_values = set(entity_df[entity].unique())
                entity_values[entity] = { }
                for value in list_of_values:
                    entity_values[entity][value] = len(entity_df.loc[entity_df[entity] == value])
            plot_series = []
            for entity in entity_values:
                for value in entity_values[entity]:
                    plot_series.append({
                        'name': '{}: {}'.format(entity, value),
                        'data': [entity_values[entity].get(value, []) for entity in selected_entities]
                        })
        elif plot_type == "stacked":
            # group by the last entity
            groupby = selected_entities[-1]
            groupby_df = pd.DataFrame(columns=['patient_id', groupby], data=categorical_df[groupby].dropna())
            groupby_values = groupby_df[groupby].unique()

            x_categories = []
            for entity in selected_entities[:-1]:
                entity_df = pd.DataFrame(columns=['patient_id', entity], data=categorical_df[entity].dropna())
                list_of_values = set(entity_df[entity].unique())
                entity_values[entity] = { }

                # now find the intersection between groupby values and other entities
                df = groupby_df.loc[groupby_df['patient_id'].isin(entity_df['patient_id'].unique())]
                df = pd.merge(df, entity_df, how='inner', on='patient_id')
                for value in list_of_values:
                    x_categories.append('{}.{}'.format(entity, value))
                    entity_values[entity][value] = []
                    for groupby_value in groupby_values:
                        entity_values[entity][value].append(
                            len(df.loc[(df[entity] == value & df[groupby] == groupby_value)]))

            plot_series = []
            for entity in entity_values:
                for value in entity_values[entity]:
                    plot_series.append({
                        'name': '{}: {}'.format(entity, value),
                        'data': [entity_values[entity].get(value, []) for entity in selected_entities]
                        })

        return render_template('plots/plots.html',
                               categorical_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               all_categorical_entities=all_categorical_only_entities,
                               entity_values=entity_values,
                               selected_c_entities=selected_entities,
                               plot_series=plot_series,
                               plot_type=plot_type,
                               x_categories=x_categories,
                               # min_max_values=min_max_values,
                               )


# js post request - called on selected an entity from a list
@plots_page.route('/plots/get_min_max/<entity>', methods=['POST'])
def get_min_max(entity):
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()

    vals = rwh.get_entity_values(entity, rdb)
    if len(vals) == 0:
        return "There are no values related to the given entity", 400
    
    min_val = vals.min()
    max_val = vals.max()
    min_max_values = {
        'min' : min_val,
        'max' : max_val,
        'step': float(max_val - min_val) / 100.0
        }
    return jsonify(min_max_values)