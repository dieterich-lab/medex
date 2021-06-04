"""
numeric_df, error = ps.get_values_scatter_plot('Pod.R231Q_A286V.4h.FDR', 'Pod.R231Q_A286V.12h.FDR', '0', '0', rdb)
numeric_df = numeric_df.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})
numeric_df['hover_mouse'] = numeric_df[name2] + '<br />' + numeric_df["Gene.Symbol"]
fig = px.scatter(numeric_df, x='Pod.R231Q_A286V.4h.FDR', y='Pod.R231Q_A286V.12h.FDR', hover_name='hover_mouse',
                 template="plotly_white", trendline="ols")
fig.update_layout(
    font=dict(size=16),
    title={
        'text': "Compare values of <b>" + 'Pod.R231Q_A286V.4h.FDR' + "</b> and <b>" + 'Pod.R231Q_A286V.12h.FDR',
        'y': 0.9,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
fig = fig.to_html()
"""
"""
dictOfcolumn = []
table_schema = []
entities = entity['Key'].tolist()
what_table = 'long'
df, error = ps.get_data(entities, what_table, rdb)
df = df.drop(columns=['measurement'])
df = df.rename(columns={"Name_ID": "{}".format(name2)})
column = df.columns.tolist()
[dictOfcolumn.append({'data': column[i]}) for i in range(0, len(column))]
[table_schema.append({'data_name': column[i],'column_name': column[i],"default": "","order": 1,"searchable": True}) for i in range(0, len(column))]
"""

# Basic Stats
basic_stats_numeric_entities = None
basic_stats_measurement_n = None
basic_stats_instance_n = None
basic_stats_numeric_results_n = None

basic_stats_categorical_entities = None
basic_stats_measurement_c = None
basic_stats_instance_c = None
basic_stats_numeric_results_c = None

# Scatter plot
scatter_plot_x_axis = None
scatter_plot_y_axis = None
scatter_plot_x_measurement = None
scatter_plot_y_measurement = None
scatter_plot_categorical_entities = None
scatter_plot_subcategory_entities = None
scatter_plot_how_to_plot = None
scatter_plot_log_x = None
scatter_plot_log_y = None
scatter_plot_add_group_by = False
scatter_plot_fig = None

# Barchart
barchart_measurement = None
barchart_all_measurement = None
barchart_categorical_entities = None
barchart_subcategory_entities = None
barchart_fig = None

# Histogram
histogram_number_of_bins = None
histogram_numeric_entities = None
histogram_categorical_entities = None
histogram_subcategory_entities = None
histogram_measurement = None
histogram_fig = None

# Boxplot

# Heatmap
heatmap_numeric_entities = None
heatmap_measurement = None
heatmap_plot_series = None

# Clustering
clustering_entities = None
clustering_cluster_info = None
clustering_all_present = None
clustering_any_present = None
clustering_fig = None

# Coplots
coplots_how_to_plot = None
coplots_select_scale = None
coplots_category11 = None
coplots_category22 = None
coplots_category1 = None
coplots_category2 = None
coplots_x_axis = None
coplots_y_axis = None
coplots_x_measurement = None
coplots_y_measurement = None
coplots_fig = None

"""
else:

    entities = data.table_browser_entites
    column = data.table_browser_column
    dictOfcolumn = data.table_browser_column2
    what_table = data.table_browser_what_table

    return render_template('data.html',
                           all_entities=all_entities,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           entities=entities,
                           name=column,
                           what_table=what_table,
                           column=dictOfcolumn
                           )
    """

"""
if data.basic_stats_numeric_entities:
    numeric_entities = data.basic_stats_numeric_entities
    measurement1 = data.basic_stats_measurement_n
    instance = data.basic_stats_instance_n
    result = data.basic_stats_numeric_results_n
    #numeric_entities = session['data.basic_stats_numeric_entities']
    #measurement1 = session['data.basic_stats_measurement_n']
    #instance = session['data.basic_stats_instance_n']
    #result = session['data.basic_stats_numeric_results_n']

    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           name=name,
                           block=block,
                           measurement_name=name,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_measurement=all_measurement,
                           numeric_entities=numeric_entities,
                           basic_stats=result,
                           measurement1=measurement1,
                           instance=instance,
                           first_value=list(result.keys())[0],
                           )
elif data.basic_stats_categorical_entities:
    categorical_entities = data.basic_stats_categorical_entities
    measurement = data.basic_stats_measurement_c
    instance = data.basic_stats_instance_c
    basic_stats_c = data.basic_stats_numeric_results_c

    return render_template('basic_stats/basic_stats.html',
                           categorical_tab=True,
                           name=name,
                           block=block,
                           measurement_name=name,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_measurement=all_measurement,
                           categorical_entities=categorical_entities,
                           measurement2=measurement,
                           instance=instance,
                           basic_stats_c=basic_stats_c)
else:
"""

"""
else:
    x_axis = data.scatter_plot_x_axis
    y_axis = data.scatter_plot_y_axis
    x_measurement = data.scatter_plot_x_measurement
    y_measurement = data.scatter_plot_y_measurement
    categorical_entities = data.scatter_plot_categorical_entities
    subcategory_entities = data.scatter_plot_subcategory_entities
    how_to_plot = data.scatter_plot_how_to_plot
    log_x = data.scatter_plot_log_x
    log_y = data.scatter_plot_log_y
    add_group_by = data.scatter_plot_add_group_by
    fig = data.scatter_plot_fig

    return render_template('scatter_plot.html',
                           name='{} number'.format(name),
                           block=block,
                           numeric_tab=True,
                           all_subcategory_entities=all_subcategory_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_numeric_entities=all_numeric_entities,
                           all_measurement=all_measurement,
                           subcategory_entities=subcategory_entities,
                           categorical_entities=categorical_entities,
                           add_group_by=add_group_by,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           log_x=log_x,
                           log_y=log_y,
                           how_to_plot=how_to_plot,
                           x_measurement=x_measurement,
                           y_measurement=y_measurement,
                           plot=fig
                           )
"""

"""
data.scatter_plot_x_axis = x_axis
data.scatter_plot_y_axis = y_axis
data.scatter_plot_x_measurement = x_measurement
data.scatter_plot_y_measurement = y_measurement
data.scatter_plot_categorical_entities = categorical_entities
data.scatter_plot_subcategory_entities = subcategory_entities
data.scatter_plot_how_to_plot = how_to_plot
data.scatter_plot_log_x = log_x
data.scatter_plot_log_y = log_y
data.scatter_plot_add_group_by = add_group_by
data.scatter_plot_fig = fig
"""