from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb,all_categorical_entities, all_subcategory_entities

barchart_page = Blueprint('barchart', __name__,
                           template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():



    return render_template('barchart.html',
                           numeric_tab=True,
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities)


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():



    # list selected entities
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')

    # handling errors and load data from database
    error = None
    if categorical_entities == 'Search entity':
        error = "Please select entities"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        categorical_df,error = ps.get_cat_values_barchart(categorical_entities,subcategory_entities, rdb)
        if not error :
            categorical_df.dropna()
        else: (None, error)
    if error:
        return render_template('barchart.html',
                               all_categorical_entities=all_categorical_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               error=error
                               )

    # Plot figure and convert to an HTML string representation
    fig = px.bar(categorical_df, x=categorical_entities, y="count", barmode='group', template="plotly_white")
    fig = fig.to_html()

    return render_template('barchart.html',
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           plot=fig
                           )
