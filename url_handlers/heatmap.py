from flask import Blueprint, render_template, request,session
import pandas as pd
from scipy.stats import pearsonr
import modules.load_data_postgre as ps
import plotly.graph_objects as go
import url_handlers.filtering as filtering
from webserver import rdb, df_min_max, data


heatmap_plot_page = Blueprint('heatmap', __name__,template_folder='tepmlates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():
    # get data for filters
    start_date, end_date = filtering.date()
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    numerical_filter = filtering.check_for_numerical_filter_get()

    return render_template('heatmap.html',
                           start_date=start_date,
                           end_date=end_date,
                           measurement_filter=session.get('measurement_filter'),
                           filter=categorical_filter,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max
                           )


@heatmap_plot_page.route('/heatmap', methods=['POST'])
def post_plots():

    # get filters
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # get selected entities
    numeric_entities = request.form.getlist('numeric_entities_multiple')

    # handling errors and load data from database
    if len(numeric_entities) > 1:
        df, error = ps.get_heat_map(numeric_entities, case_ids, categorical_filter, categorical_names, name,from1, to1,
                                    measurement_filter, date, rdb)
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
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               df_min_max=df_min_max,
                               error=error)

    # calculate person correlation

    numeric_df = df.drop(columns=['Name_ID'])
    new_numeric_entities = numeric_df.columns.tolist()

    numeric_entities_not_measured = set(numeric_entities).difference(set(new_numeric_entities))
    if len(numeric_entities_not_measured) > 0:
        error = "{} not measure during Replicate".format(numeric_entities_not_measured)
    numeric_entities = new_numeric_entities

    dfcols = pd.DataFrame(columns=numeric_df.columns)
    pvalues = dfcols.transpose().join(dfcols, how='outer')
    corr_values = dfcols.transpose().join(dfcols, how='outer')

    for r in numeric_df.columns:
        for c in numeric_df.columns:
            if c == r:
                df_corr = numeric_df[[r]].dropna()
            else:
                df_corr = numeric_df[[r, c]].dropna()
            if len(df_corr) < 2:
                corr_values[r][c], pvalues[r][c] = None,None

            else:
                corr_values[r][c], pvalues[r][c] = pearsonr(df_corr[r], df_corr[c])

    # currently don't use
    pvalues = pvalues.astype(float)
    pvalues = pvalues.round(decimals=3)
    pvalues = pvalues.T.values.tolist()

    corr_values = corr_values.astype(float)
    corr_values = corr_values.round(decimals=2)
    corr_values = corr_values.T.values.tolist()

    fig = go.Figure(data=go.Heatmap(z=corr_values, x=numeric_entities, y=numeric_entities, colorscale='Viridis'))
    fig.update_layout(height=600)
    fig = fig.to_html()

    return render_template('heatmap.html',
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max,
                           numeric_entities=numeric_entities,
                           measurement_filter=measurement_filter,
                           plot=fig)
