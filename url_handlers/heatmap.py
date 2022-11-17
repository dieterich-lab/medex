from flask import Blueprint, render_template, request, session
import pandas as pd
from scipy.stats import pearsonr

from medex.controller.helpers import get_filter_service
from medex.services.database import get_db_session
from modules.get_data_to_heatmap import get_heat_map
from url_handlers.filtering import check_for_date_filter_post, check_for_limit_offset
import plotly.graph_objects as go
from webserver import start_date, end_date

heatmap_plot_page = Blueprint('heatmap', __name__, template_folder='tepmlates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():
    return render_template('heatmap.html')


@heatmap_plot_page.route('/heatmap', methods=['POST'])
def post_plots():

    # get request values
    numeric_entities = request.form.getlist('numeric_entities_multiple')

    # get_filter
    check_for_date_filter_post(start_date, end_date)
    date_filter = session.get('date_filter')
    limit_filter = check_for_limit_offset()
    update_filter = session.get('filtering')

    # handling errors and load data from database
    df = pd.DataFrame()
    if len(numeric_entities) > 1:
        session_db = get_db_session()
        filter_service = get_filter_service()
        df, error = get_heat_map(numeric_entities, date_filter, limit_filter, filter_service, session_db)
        if not error:
            if len(df.index) == 0:
                error = "This two entities don't have common values"
    elif len(numeric_entities) < 2:
        error = "Please select more then one category"
    else:
        error = "Please select numeric entities"

    if error:
        return render_template('heatmap.html',
                               numeric_entities=numeric_entities,
                               error=error)

    # calculate person correlation
    numeric_df = df.drop(columns=['name_id'])
    new_numeric_entities = numeric_df.columns.tolist()

    numeric_entities_not_measured = set(numeric_entities).difference(set(new_numeric_entities))
    if len(numeric_entities_not_measured) > 0:
        error = "{} not measure during Replicate".format(numeric_entities_not_measured)

    dfcols = pd.DataFrame(columns=numeric_df.columns)
    pvalues = dfcols.transpose().join(dfcols, how='outer')
    corr_values = dfcols.transpose().join(dfcols, how='outer')
    number_of_values = dfcols.transpose().join(dfcols, how='outer')

    for r in numeric_df.columns:
        for c in numeric_df.columns:
            if c == r:
                df_corr = numeric_df[[r]].dropna()
            else:
                df_corr = numeric_df[[r, c]].dropna()
            if len(df_corr) < 2:
                corr_values[r][c], pvalues[r][c] = None, None
            else:
                number_of_values[r][c] = len(df_corr)
                corr_values[r][c], pvalues[r][c] = pearsonr(df_corr[r], df_corr[c])

    corr_values = corr_values.astype(float)
    corr_values = corr_values.round(decimals=2)
    corr_values = corr_values.T.values.tolist()

    number_of_values = number_of_values.T.values.tolist()
    fig = go.Figure(data=go.Heatmap(z=corr_values, x=new_numeric_entities, y=new_numeric_entities,
                                    colorscale='Viridis'))
    fig.update_traces(text=number_of_values, texttemplate="%{text}")
    fig.update_layout(height=600,
                      title='Heatmap shows Pearson correlation')
    fig = fig.to_html()
    return render_template('heatmap.html',
                           error=error,
                           numeric_entities=numeric_entities,
                           plot=fig)
