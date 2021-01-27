from flask import Blueprint, render_template, request
import pandas as pd
from scipy.stats import pearsonr
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_measurement,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,database,name, block,all_subcategory_entities,data


heatmap_plot_page = Blueprint('heatmap', __name__,
                       template_folder='tepmlates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():
    filter = data.filter_store
    cat = data.cat
    number_filter = 0
    if filter != None:
        number_filter = len(filter)
        filter = zip(cat, filter)
    return render_template('heatmap.html',
                           name='{} number'.format(name),
                           block=block,
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           number_filter=number_filter,
                           filter=filter
                           )


@heatmap_plot_page.route('/heatmap', methods=['POST'])
def post_plots():
    if 'filter_c' in request.form:
        filter = request.form.getlist('filter')
        cat = request.form.getlist('cat')
        data.filter_store = filter
        data.cat = cat
        number_filter = 0
        if filter != None:
            number_filter = len(filter)
            filter = zip(cat, filter)
        return render_template('data.html',
                               all_entities=all_entities,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities,
                               filter=filter,
                               number_filter=number_filter,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                               )
    # get selected entities
    numeric_entities = request.form.getlist('numeric_entities')
    #if 'filter' in request.form or 'all_categorical_filter' in request.form:
    #    filter = request.form.getlist('filter')
    #    cat = request.form.getlist('cat')
    #    data.filter_store = filter
    #    data.cat = cat
    #    number_filter = 0
    filter = data.filter_store
    cat = data.cat
    number_filter = 0
    if block == 'none':
        measurement = all_measurement.values[0]
    else:
        measurement = request.form.get('measurement')

    # handling errors and load data from database
    error = None
    if measurement == "Search entity":
        error = "Please select number of {}".format(name)
    elif len(numeric_entities) > 1:
        numeric_df, error = ps.get_values_heatmap(numeric_entities,measurement,filter,cat, rdb)

        if not error:
            if len(numeric_df.index) == 0:
                error = "This two entities don't have common values"
        else:
            (None, error)
    elif len (numeric_entities) < 2:
        error = "Please select more then one category"
    else:
        error = "Please select numeric entities"
    if filter != None:
        number_filter = len(filter)
        filter = zip(cat, filter)
    if error:
        return render_template('heatmap.html',
                               name='{} number'.format(name),
                               block=block,
                               numeric_tab=True,
                               all_numeric_entities=all_numeric_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_categorical_entities=all_categorical_entities,
                               database=database,
                               size_categorical=size_categorical,
                               size_numeric=size_numeric,
                               len_numeric=len_numeric,
                               len_categorical=len_categorical,
                               numeric_entities=numeric_entities,
                               measurement=measurement,
                               all_measurement=all_measurement,
                               number_filter=number_filter,
                               filter=filter,
                               error=error)
    error = None
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
                corr_values[r][c], pvalues[r][c] = -1,-1
            else:
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
                           name='{} number'.format(name),
                           block=block,
                           numeric_tab=True,
                           all_numeric_entities=all_numeric_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           numeric_entities=numeric_entities,
                           measurement=measurement,
                           plot_series=plot_series,
                           number_filter=number_filter,
                           filter=filter,
                           error=error
                           )

