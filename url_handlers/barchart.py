from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb,all_categorical_entities, all_subcategory_entities,all_visit

barchart_page = Blueprint('barchart', __name__,
                           template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():



    return render_template('barchart.html',
                           numeric_tab=True,
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit)


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():



    # list selected entities
    visit = request.form.getlist('visit')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    # handling errors and load data from database
    error = None
    if not visit:
        error = "Please select number of visit"
    elif categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        categorical_df, error = ps.get_cat_values_barchart(categorical_entities,subcategory_entities,visit,rdb)
        if not error :
            categorical_df.dropna()
        else: (None, error)

    if error:
        return render_template('barchart.html',
                               all_categorical_entities=all_categorical_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_visit=all_visit,
                               visit2=visit,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               error=error
                               )


    categorical_df['%'] = 100 * categorical_df['count'] / categorical_df.groupby('Billing_ID')['count'].transform('sum')

    # Plot figure and convert to an HTML string representation
    if how_to_plot == 'count':
        fig = px.bar(categorical_df,x='Billing_ID', y="count", color=categorical_entities, barmode='group', template="plotly_white")
        fig = fig.to_html()

    else:
        fig = px.bar(categorical_df,x='Billing_ID', y="%", color=categorical_entities, barmode='group', template="plotly_white")
        fig = fig.to_html()


    return render_template('barchart.html',
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           visit2=visit,
                           all_visit=all_visit,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           plot=fig
                           )
