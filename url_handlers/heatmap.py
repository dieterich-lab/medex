from flask import Blueprint, render_template, request
import pandas as pd
from scipy.stats import pearsonr
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb, all_numeric_entities,all_visit


heatmap_plot_page = Blueprint('heatmap', __name__,
                       template_folder='tepmlates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():

    return render_template('heatmap.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_visit=all_visit)


@heatmap_plot_page.route('/heatmap', methods=['POST'])
def post_plots():
    # get selected entities
    numeric_entities = request.form.getlist('numeric_entities')
    visit = request.form.get('visit')

    # handling errors and load data from database
    error = None
    if visit == "Search entity":
        error = "Please select number of visit"
    elif len(numeric_entities) > 1:
        numeric_df, error = ps.get_values(numeric_entities,visit, rdb)
        if not error:
            if len(numeric_df.index) == 0:
                error = "This two entities don't have common values"
        else:
            (None, error)
    elif len (numeric_entities) < 2:
        error = "Please select more then one category"
    else:
        error = "Please select numeric entities"
    if error:
        return render_template('heatmap.html',
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               numeric_entities=numeric_entities,
                               visit=visit,
                               all_visit=all_visit,
                               error=error)
    error=None
    for i in numeric_entities:
        if not i in numeric_df.columns:
            numeric_entities.remove(i)
            error = "{} not exist".format(i)

    # calculate person correlation
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

    # currently don't use
    pvalues = pvalues.astype(float)
    pvalues = pvalues.round(decimals=3)
    pvalues = pvalues.T.values.tolist()

    corr_values = corr_values.astype(float)
    corr_values = corr_values.round(decimals=2)
    corr_values = corr_values.T.values.tolist()



#    fig = px.imshow(corr_values,x=numeric_entities,y=numeric_entities)
#    fig.show()
    # structure data for ploting
    plot_series = []
    plot_series.append({'z': corr_values,
                        'x' : numeric_entities,
                        'y' : numeric_entities,
                        'type': "heatmap",
                        'color': 'corr'
                        })



    return render_template('heatmap.html',
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           numeric_entities=numeric_entities,
                           visit=visit,
                           all_visit=all_visit,
                           plot_series=plot_series,
                           error=error
                           )

