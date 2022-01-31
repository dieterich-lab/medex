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
    return render_template('heatmap.html')


@heatmap_plot_page.route('/heatmap', methods=['POST'])
def post_plots():

    # get filters
    start_date, end_date, date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter

    # get request values
    add = request.form.get('Add')
    clean = request.form.get('clean')
    update = request.form.get('update')
    numeric_entities = request.form.getlist('numeric_entities_multiple')

    if update is not None or clean is not None or add is not None:
        if add is not None:
            update_list = list(add.split(","))
            update = add
        elif clean is not None:
            update = '0,0'
            update_list = list(update.split(","))
        else:
            update = '0,0'
            update_list = list(update.split(","))
            print(update)
        data.update_filter = update
        ps.filtering(case_ids, categorical_filter, categorical_names, name, from1, to1, measurement_filter, update_list,rdb)
        return render_template('data.html',
                               val=update,
                               measurement_filter=measurement_filter,
                               start_date=start_date,
                               end_date=end_date,
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               filter=categorical_filter_zip,
                               df_min_max=df_min_max
                               )

    # handling errors and load data from database
    update = data.update_filter
    if len(numeric_entities) > 1:
        df, error = ps.get_heat_map(numeric_entities, date, update, rdb)
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
                               categorical_filter=categorical_names,
                               numerical_filter_name=name,
                               df_min_max=df_min_max,
                               error=error)

    # calculate person correlation

    numeric_df = df.drop(columns=['Name_ID'])
    new_numeric_entities = numeric_df.columns.tolist()

    numeric_entities_not_measured = set(numeric_entities).difference(set(new_numeric_entities))
    if len(numeric_entities_not_measured) > 0:
        error = "{} not measure during Replicate".format(numeric_entities_not_measured)


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

    fig = go.Figure(data=go.Heatmap(z=corr_values, x=new_numeric_entities, y=new_numeric_entities, colorscale='Viridis'))
    fig.update_layout(height=600,
                      title='Heatmap shows Pearson correlation')
    fig = fig.to_html()

    return render_template('heatmap.html',
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           df_min_max=df_min_max,
                           numeric_entities=numeric_entities,
                           measurement_filter=measurement_filter,
                           categorical_filter=categorical_names,
                           numerical_filter_name=name,
                           plot=fig)
