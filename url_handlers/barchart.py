from flask import Blueprint, render_template, request,session
import modules.load_data_postgre as ps
import plotly.express as px
import url_handlers.filtering as filtering
from webserver import rdb, all_measurement, measurement_name, Name_ID, block, df_min_max, data

barchart_page = Blueprint('barchart', __name__, template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    categorical_filter, categorical_names = filtering.check_for_filter_get()
    numerical_filter = filtering.check_for_numerical_filter_get()
    return render_template('barchart.html',
                           block=block,
                           name='{}'.format(measurement_name),
                           all_measurement=all_measurement,
                           start_date=session.get('start_date'),
                           end_date=session.get('end_date'),
                           measurement_filter=session.get('measurement_filter'),
                           filter=categorical_filter,
                           numerical_filter=numerical_filter,
                           )


@barchart_page.route('/barchart', methods=['POST'])
def post_statistics():
    # get filters
    start_date, end_date,date = filtering.check_for_date_filter_post()
    case_ids = data.case_ids
    categorical_filter, categorical_names, categorical_filter_zip, measurement_filter = filtering.check_for_filter_post()
    numerical_filter, name, from1, to1 = filtering.check_for_numerical_filter(df_min_max)
    session['measurement_filter'] = measurement_filter


    # checking if display selector for measurement
    if block == 'none':
        measurement = all_measurement.values
    else:
        measurement = request.form.getlist('measurement')

    categorical_entities = request.form.get('categorical_entities')
    subcategory_entities = request.form.getlist('subcategory_entities')
    how_to_plot = request.form.get('how_to_plot')

    # handling errors and load data from database
    error = None
    if not measurement:
        error = "Please select number of {}".format(measurement_name)
    elif categorical_entities == "Search entity":
        error = "Please select a categorical value to group by"
    elif not subcategory_entities:
        error = "Please select subcategory"
    else:
        # select data from database
        categorical_df, error = ps.get_cat_values_barchart(categorical_entities, subcategory_entities, measurement, case_ids,
                                                           categorical_filter, categorical_names, name, from1, to1,
                                                           measurement_filter, date, rdb)

        # rename columns
        categorical_df = categorical_df.rename(columns={"Name_ID": "{}".format(Name_ID), "measurement": "{}".format(measurement_name)})
        if not error:
            categorical_df.dropna()

    if error:
        return render_template('barchart.html',
                               name='{}'.format(measurement_name),
                               block=block,
                               start_date=start_date,
                               end_date=end_date,
                               filter=categorical_filter_zip,
                               numerical_filter=numerical_filter,
                               measurement=measurement,
                               measurement_filter=measurement_filter,
                               categorical_entities=categorical_entities,
                               subcategory_entities=subcategory_entities,
                               how_to_plot=how_to_plot,
                               error=error
                               )

    categorical_df['%'] = 100*categorical_df['count']/categorical_df.groupby(measurement_name)['count'].transform('sum')

    # Plot figure and convert to an HTML string representation
    if block == 'none':
        if how_to_plot == 'count':
            fig = px.bar(categorical_df, x=categorical_entities, y="count", barmode='group', template="plotly_white")
        else:
            fig = px.bar(categorical_df, x=categorical_entities, y="%", barmode='group', template="plotly_white")
    else:
        if how_to_plot == 'count':
            fig = px.bar(categorical_df, x=measurement_name, y="count", color=categorical_entities, barmode='group',
                         template="plotly_white")
        else:
            fig = px.bar(categorical_df, x=measurement_name, y="%", color=categorical_entities, barmode='group',
                         template="plotly_white")

    fig.update_layout(font=dict(size=16))
    fig = fig.to_html()

    return render_template('barchart.html',
                           name='{}'.format(measurement_name),
                           block=block,
                           measurement=measurement,
                           measurement_filter=measurement_filter,
                           start_date=start_date,
                           end_date=end_date,
                           filter=categorical_filter_zip,
                           numerical_filter=numerical_filter,
                           categorical_entities=categorical_entities,
                           subcategory_entities=subcategory_entities,
                           how_to_plot=how_to_plot,
                           plot=fig,
                           )
