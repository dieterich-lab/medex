from flask import Blueprint, render_template, request
import modules.load_data_postgre as ps


import plotly.express as px
from webserver import rdb, all_numeric_entities, all_categorical_entities,all_visit,all_entities,len_numeric,size_categorical,size_numeric,len_categorical,all_subcategory_entities,database

coplots_plot_page = Blueprint('coplots_pl', __name__,
                         template_folder='templates')


@coplots_plot_page.route('/coplots_pl', methods=['GET'])
def get_coplots():

    return render_template('coplots_pl.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit,
                           database=database,
                           size_categorical=size_categorical,
                           size_numeric=size_numeric,
                           len_numeric=len_numeric,
                           len_categorical=len_categorical
                           )


@coplots_plot_page.route('/coplots_pl', methods=['POST'])
def post_coplots():
    # get selected entities
    category1 = request.form.get('category1')
    category2 = request.form.get('category2')

    category11 = request.form.getlist('category11')
    category22 = request.form.getlist('category22')

    x_axis = request.form.get('x_axis')
    y_axis = request.form.get('y_axis')

    x_visit = request.form.get('x_visit')
    y_visit = request.form.get('y_visit')

    how_to_plot = request.form.get('how_to_plot')
    how_to_plot2 = request.form.get('how_to_plot2')

    log_x = request.form.get('log_x')
    log_y = request.form.get('log_y')

    select_scale = request.form.get('select_scale') is not None

    # handling errors and load data from database
    error = None
    if x_visit == "Search entity" or y_visit == "Search entity":
        error = "Please select number of visit"
    elif category1 is None or category1 == 'Search entity':
        error = 'Please select category1'
    elif category2 is None or category2 == 'Search entity':
        error = 'Please select category2'
    elif x_axis is None or x_axis == 'Search entity':
        error = 'Please select x_axis'
    elif y_axis is None or y_axis == 'Search entity':
        error = 'Please select y_axis'
    elif x_axis == y_axis and category1 == category2:
        error = "You can't compare the same entities and categories"
    elif x_axis == y_axis and x_visit == y_visit:
        error = "You can't compare the same entities for x and y axis"
    elif category1 == category2:
        error = "You can't compare the same category"
    elif not category22 or not category11:
        error = "Please select subcategory"
    elif how_to_plot == 'log' and not log_x and not log_y:
        error = "Please select type of log"
    if not error:
        num_data, error = ps.get_values_scatter_plot(x_axis, y_axis,x_visit,y_visit, rdb) if not error else (None, error)
        if x_axis == y_axis:
            x_axis=x_axis+'_x'
            y_axis=y_axis+'_y'
        if not x_axis in num_data.columns:
            error = "The entity {} wasn't measured".format(x_axis)
        elif not y_axis in num_data.columns:
            error = "The entity {} wasn't measured".format(y_axis)
        elif not error:
            cat_data1, error = ps.get_cat_values(category1,category11,[x_visit,y_visit], rdb) if not error else (None, error)
            if not error:
                cat_data2, error = ps.get_cat_values(category2,category22,[x_visit,y_visit], rdb)
                if not error:
                    data = num_data.merge(cat_data1, on ="Patient_ID")
                    data = data.merge(cat_data2, on="Patient_ID")
                    data = data.dropna()
                    if len(data.index) == 0:
                        error = "No data based on the selected options"
                else: (None, error)
    if error:
        return render_template('coplots_pl.html',
                               all_subcategory_entities=all_subcategory_entities,
                               all_numeric_entities=all_numeric_entities,
                               categorical_entities=all_categorical_entities,
                               all_visit=all_visit,
                               error=error,
                               category1=category1,
                               category2=category2,
                               x_axis=x_axis,
                               y_axis=y_axis,
                               x_visit=x_visit,
                               y_visit=y_visit,
                               how_to_plot=how_to_plot,
                               select_scale=select_scale,
                               category11=category11,
                               category22=category22)

    # Plot figure and convert to an HTML string representation
    len1 = len(category11)
    len2 = len(category22)
    data[category1+'|'+category2] = data[category1]+ '|'+ data[category2]
    #regline = sm.OLS(data[x_axis], sm.add_constant(y_axis)).fit().fittedvalues



    if how_to_plot2 == "linear":
        if how_to_plot == "single_plot":
            try:
                fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",  color=category1 + '|' + category2,trendline="ols")

            except:
                fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white", color=category1 + '|' + category2)
        else:
            try:
                fig = px.scatter(data,x=x_axis, y=y_axis,facet_row=category2, facet_col=category1,color=category1+'|'+category2,
                                 template="plotly_white",render_mode="svg",trendline="ols",trendline_color_override="black")

                #fig.update_traces(marker=dict(color="RoyalBlue"),selector=dict(type="scattergl"))


                #fig.for_each_trace(
                #    lambda trace: trace.update(marker_symbol="square") if trace.type == "scattergl" else (),
                #)

            except:
                fig = px.scatter(data, x=x_axis, y=y_axis, facet_row=category2, facet_col=category1,
                                 template="plotly_white", color=category1 + '|' + category2)
            fig.update_layout(
                height=500 * len2,
                width=800 * len1)
    else:
        if log_x == 'log_x' and log_y == 'log_y':
            if how_to_plot == "single_plot":
                try:
                    fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",color=category1+'|'+category2,
                                     trendline="ols",log_x=True, log_y=True)
                except:
                    fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",
                                     color=category1 + ' ' + category2,log_x=True, log_y=True)
            else:
                try:
                    fig = px.scatter(data,x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,color=category1+'|'+category2,
                                     template="plotly_white",trendline="ols",trendline_color_override="black",log_x=True, log_y=True)
                except:
                    fig = px.scatter(data, x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,
                                     template="plotly_white", color=category1 + '|' + category2,
                                     log_x=True, log_y=True)
                fig.update_layout(
                    height=500 * len2,
                    width=800 * len1)
        elif log_x == 'log_x':
            if how_to_plot == "single_plot":
                try:
                    fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",color=category1+'|'+category2,
                                     trendline="ols",log_x=True)
                except:
                    fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",
                                     color=category1 + '|' + category2, log_x=True)
            else:
                try:
                    fig = px.scatter(data,x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,
                                     template="plotly_white",color=category1+'|'+category2,trendline="ols",trendline_color_override="black",log_x=True)
                except:
                    fig = px.scatter(data, x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,
                                     template="plotly_white", color=category1 + '|' + category2,
                                     log_x=True)
                fig.update_layout(
                    height=500 * len2,
                    width=800 * len1)
        elif log_y == 'log_y':
            if how_to_plot == "single_plot":
                try:
                    fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",color=category1+'|'+category2,
                                     trendline="ols", log_y=True)
                except:
                    fig = px.scatter(data, x=x_axis, y=y_axis, template="plotly_white",
                                     color=category1 + '|' + category2, log_y=True)
            else:
                try:
                    fig = px.scatter(data,x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,template="plotly_white",color=category1+'|'+category2,trendline="ols",log_y=True)
                except:
                    fig = px.scatter(data, x=x_axis, y=y_axis, facet_row=category1, facet_col=category2,
                                     template="plotly_white", color=category1 + '|' + category2,
                                     log_y=True)
                fig.update_layout(
                    height=500 * len2,
                    width=800 * len1)
    fig.for_each_annotation(lambda a: a.update(text=a.text.replace("=",'<br>')))
    #fig.update_xaxes(title=x_axis.replace("_",'<br>'))

    N=len(fig.data)
    fig1=fig
    #print(fig.data.type)
    #for i in range(N):
        #fig.data[i].mode = fig.data[i].mode.replace('markers', 'lines')
        #fig1.data[i].type = fig1.data[i].type.replace('scattergl', 'scatter')
        #print(fig.data[i].mode)



    fig.update_layout(
        font=dict(size=16),
        title={
            'text': "Compare values of <b>" + x_axis + "</b> and <b>" + y_axis + "</b>",
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})


    fig = fig.to_html()
    return render_template('coplots_pl.html',
                           all_numeric_entities=all_numeric_entities,
                           categorical_entities=all_categorical_entities,
                           all_subcategory_entities=all_subcategory_entities,
                           all_visit=all_visit,
                           how_to_plot=how_to_plot,
                           select_scale=select_scale,
                           category11=category11,
                           category22=category22,
                           category1=category1,
                           category2=category2,
                           x_axis=x_axis,
                           y_axis=y_axis,
                           x_visit=x_visit,
                           y_visit=y_visit,
                           plot=fig
                           )
