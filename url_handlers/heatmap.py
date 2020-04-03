from flask import Blueprint, render_template, request
import pandas as pd
from scipy.stats import pearsonr
import modules.load_data_postgre as ps

heatmap_plot_page = Blueprint('heatmap', __name__,
                       template_folder='tepmlates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():
    
    # connection and load data from database
    from webserver import connect_db
    rdb = connect_db()
    all_numeric_entities = ps.get_numeric_entities(rdb)

    return render_template('heatmap.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities)


@heatmap_plot_page.route('/heatmap', methods=['POST'])
def post_plots():
    
    # connection with database and load name of entities
    from webserver import connect_db
    rdb = connect_db()
    all_numeric_entities = ps.get_numeric_entities(rdb)

    # get selected entities
    numeric_entities = request.form.getlist('numeric_entities')

    # handling errors and load data from database
    error = None
    if len(numeric_entities) > 1:
        numeric_df = ps.get_values(numeric_entities, rdb)
        if len(numeric_df.index) == 0:
            error = "This two entities don't have common values"
    elif len (numeric_entities) < 2:
        error = "Please select more then one category"
    else:
        error = "Please select numeric entities"
    if error:
        return render_template('heatmap.html',
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               selected_n_entities=numeric_entities,
                               error=error)
    

    numeric_df = numeric_df[numeric_entities]
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
                        'x' : numeric_entities,
                        'y' : numeric_entities,
                        'type': "heatmap"
                        })



    return render_template('heatmap.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           selected_n_entities=numeric_entities,
                           plot_series=plot_series
                           )

