from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps
import plotly.express as px
from webserver import rdb,all_categorical_entities, all_subcategory_entities,all_visit,all_entities

barchart_page = Blueprint('barchart', __name__,
                           template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():



    return render_template('barchart.html',
                           numeric_tab=True,
                           all_entities=all_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit)


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():



    # list selected entities
    visit = request.form.getlist('visit')
    entities = request.form.getlist('entities')
    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    add_group_by = request.form.get('add_group_by') is not None

    # handling errors and load data from database
    error = None
    if not visit:
        error = "Please select number of visit"
    elif not entities:
        error = "Please select entities"
    elif add_group_by and categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities and add_group_by:
        error = "Please select subcategory"
    elif add_group_by and categorical_entities:
        categorical_df, error = ps.get_cat_values_barchart(categorical_entities,subcategory_entities,visit,rdb)
        categorical_df2, error = ps.barchart_visit(entities, visit, rdb)
        if not error :
            categorical_df.dropna()
        else: (None, error)
    else:
        categorical_df2, error = ps.barchart_visit(entities, visit, rdb)
        categorical_df2['Billing_ID'] = categorical_df2['Billing_ID'].apply(str)
        if not error :
            categorical_df2.dropna()
        else: (None, error)
    if error:
        return render_template('barchart.html',
                               all_entities=all_entities,
                               all_categorical_entities=all_categorical_entities,
                               all_subcategory_entities=all_subcategory_entities,
                               all_visit=all_visit,
                               entities=entities,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               error=error
                               )

    # Plot figure and convert to an HTML string representation
    if add_group_by:
        fig1 = px.bar(categorical_df,x='Billing_ID', y="count", color=categorical_entities, barmode='group', template="plotly_white")
        fig1 = fig1.to_html()
        fig2 = px.bar(categorical_df2, x='Billing_ID', y="count", color="Key", template="plotly_white")
        fig2.update_layout(xaxis=dict(type='category'))

        fig2 = fig2.to_html()

    else:
        fig2 = px.bar(categorical_df2, x='Billing_ID', y="count",color="Key", template="plotly_white")
        fig2.update_layout(xaxis=dict(type='category'))

        fig2 = fig2.to_html()
        fig1 = []

    return render_template('barchart.html',
                           all_entities=all_entities,
                           all_categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           visit2=visit,
                           all_visit=all_visit,
                           entities=entities,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           plot2=fig2,
                           plot1=fig1
                           )
