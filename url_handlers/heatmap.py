from flask import Blueprint, render_template, request
import pandas as pd
from scipy.stats import pearsonr
import modules.load_data_postgre as ps
import plotly.graph_objects as go
import url_handlers.filtering as filtering
from webserver import rdb, all_numeric_entities, all_categorical_entities_sc, all_measurement,measurement_name, block, \
    all_subcategory_entities, data


heatmap_plot_page = Blueprint('heatmap', __name__,template_folder='tepmlates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():
    categorical_filter, categorical_names = filtering.check_for_filter_get(data)
    return render_template('heatmap.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_measurement=all_measurement,
                           filter=categorical_filter
                           )


@heatmap_plot_page.route('/heatmap', methods=['POST'])
def post_plots():

    # get selected entities
    numeric_entities = request.form.getlist('numeric_entities_multiple')
    if block == 'none':
        measurement = all_measurement.values[0]
    else:
        measurement = request.form.get('measurement')

    # get filter
    id_filter = data.id_filter
    categorical_filter, categorical_names, categorical_filter_zip = filtering.check_for_filter_post(data)

    # handling errors and load data from database
    if measurement == "Search entity":
        error = "Please select number of {}".format(measurement)
    elif len(numeric_entities) > 1:
        numeric_df, error = ps.get_values_heatmap(numeric_entities, measurement, categorical_filter, categorical_names,
                                                  id_filter, rdb)
        if not error:
            if len(numeric_df.index) == 0:
                error = "This two entities don't have common values"

    elif len(numeric_entities) < 2:
        error = "Please select more then one category"
    else:
        error = "Please select numeric entities"

    if error:
        return render_template('heatmap.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities_sc,
                               numeric_entities=numeric_entities,
                               measurement=measurement,
                               all_measurement=all_measurement,
                               filter=categorical_filter_zip,
                               error=error)

    # calculate person correlation
    numeric_df = numeric_df.drop(columns=['Name_ID'])
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
    fig.update_layout(height=900)
    fig = fig.to_html()
    plot_series = []
    plot_series.append({'z': corr_values,
                        'x': numeric_entities,
                        'y': numeric_entities,
                        'type': "heatmap",
                        'color': 'corr'
                        })

    return render_template('heatmap.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities_sc,
                           all_measurement=all_measurement,
                           numeric_entities=numeric_entities,
                           measurement=measurement,
                           plot_series=plot_series,
                           plot=fig,
                           filter=categorical_filter_zip
                           )
