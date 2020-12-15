from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_measurement,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,all_subcategory_entities,database,name,name2,block,data

barchart_page = Blueprint('barchart', __name__,
                           template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():


    categorical_entities = data.data_x_axis
    print(categorical_entities)
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')
    categorical_entities = request.form.get('categorical_entities')
    if categorical_entities == None:
        categorical_entities = 'cos'
    subcategory_entities = request.form.getlist('subcategory_entities')
    if len(subcategory_entities) == 0:
        subcategory_entities.append('cos')




    return render_template('barchart.html',
                           numeric_tab=True,
                           block=block,
                           name='{} number'.format(name),
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_measurement=all_measurement,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical,
                           measurement2=measurement,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           )


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():

    # list selected entities
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')
    data.data_x_axis=categorical_entities
    # handling errors and load data from database
    error = None
    if not measurement:
        error = "Please select number of {}".format(name)
    elif categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        categorical_df, error = ps.get_cat_values_barchart(categorical_entities,subcategory_entities,measurement,rdb)
        categorical_df = categorical_df.rename(columns={"Name_ID": "{}".format(name2), "measurement": "{}".format(name)})
        if not error :
            categorical_df.dropna()
        else: (None, error)

    if error:
        return render_template('barchart.html',
                               name='{} number'.format(name),
                                block=block,
                               all_categorical_entities=all_categorical_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_measurement=all_measurement,
                               measurement2=measurement,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               error=error
                               )


    categorical_df['%'] = 100 * categorical_df['count'] / categorical_df.groupby(name)['count'].transform('sum')

    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'count':
            fig = px.bar(categorical_df,x=categorical_entities, y="count", barmode='group', template="plotly_white")
        else:
            fig = px.bar(categorical_df,x=categorical_entities, y="%", barmode='group', template="plotly_white")
    else:
        if how_to_plot == 'count':
            fig = px.bar(categorical_df,x=name, y="count", color=categorical_entities, barmode='group', template="plotly_white")
        else:
            fig = px.bar(categorical_df,x=name, y="%", color=categorical_entities, barmode='group', template="plotly_white")

    fig.update_layout(font=dict(size=16))
    fig = fig.to_html()


    return render_template('barchart.html',
                           name='{} number'.format(name),
                           block=block,
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           measurement2=measurement,
                           all_measurement=all_measurement,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           plot=fig
                           )
