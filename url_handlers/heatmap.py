from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from scipy.stats import pearsonr

import data_warehouse.redis_rwh as rwh

heatmap_plot_page = Blueprint('heatmap', __name__,
                       template_folder='tepmlates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))

    return render_template('heatmap.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_only_entities)


@heatmap_plot_page.route('/heatmap', methods=['POST'])
# @login_required
def post_plots():
    # this import has to be here!!
    from webserver import get_db
    rdb = get_db()
    all_numeric_entities = rwh.get_numeric_entities(rdb)
    all_categorical_entities = rwh.get_categorical_entities(rdb)
    all_categorical_only_entities = sorted(set(all_categorical_entities) - set(all_numeric_entities))



    selected_entities = request.form.getlist('numeric_entities')

    if not selected_entities:
        error = "Please select entities"
        return render_template('heatmap.html',
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               all_categorical_entities=all_categorical_only_entities,
                               error=error)


    numeric_df, err = rwh.get_joined_numeric_values(selected_entities, rdb)
    if err:
        return render_template('heatmap.html',
                               error=err,
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


    plot_series = []
    plot_series.append({'z': corr_values,
                        'x' : selected_entities,
                        'y' : selected_entities,
                        'type': "heatmap"
                        })



    return render_template('heatmap.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_categorical_entities=all_categorical_only_entities,
                           selected_n_entities=selected_entities,
                           plot_series=plot_series
                           )

