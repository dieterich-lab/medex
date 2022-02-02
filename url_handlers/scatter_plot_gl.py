fig = go.Figure()

# Create figure
fig = go.Figure()
if add_group_by:
    for i in subcategory_entities:
        dfu = df[df[categorical_entities] == i]
        fig.add_trace(
            go.Scattergl(
                x=dfu[x_axis_m],
                y=dfu[y_axis_m],
                mode='markers',
                name=i,
            )
        )
else:
    fig.add_trace(
        go.Scattergl(
            x=df[x_axis_m],
            y=df[y_axis_m],
            mode='markers',
            marker=dict(
                line=dict(
                    width=1,
                    color='DarkSlateGrey')
            )
        )
    )
if block == 'none':
    fig.update_layout(
        font=dict(size=16),
        title={
            'text': "Compare values of <b>" + x_axis + "</b> and <b>" + y_axis,
            'x': 0.5,
            'xanchor': 'center', })
else:
    split_text = textwrap.wrap("Compare values of <b>" + x_axis + "</b> : " + measurement_name + " <b>" +
                               x_measurement + "</b> and <b>" + y_axis + "</b> : " + measurement_name + " <b>" +
                               y_measurement + "</b> ", width=100)
    xaxis = textwrap.wrap(x_axis_m)
    yaxis = textwrap.wrap(y_axis_m, width=40)
    legend = textwrap.wrap(categorical_entities, width=20)

    fig.update_layout(
        template="plotly_white",
        legend_title='<br>'.join(legend),
        font=dict(size=16),
        xaxis_title='<br>'.join(xaxis),
        yaxis_title='<br>'.join(yaxis),
        title={
            'text': '<br>'.join(split_text),
            'x': 0.5,
            'xanchor': 'center', })
fig.show()

# Should I change for date fo timestamp ?


# categorical_filter
category_filter = ""
numerical_filter = ""
category_filter_where = ""
numerical_filter_where = ""

for i in range(len(categorical)):
    cat = categorical_filter[i]
    cat = cat.replace('<br>', ',')
    cat = "$$" + cat[(cat.find(' is') + 6):].replace(",", "$$,$$") + "$$"
    category_m = 'a_{}'.format(i)
    category_m0 = 'a_{}'.format(i - 1)

    if i == 0:
        cat_filter = """Select {0}."Name_ID" FROM examination_categorical as {0}   """.format(category_m)

        cat_filter_where = """where {0}."Key"=$${1}$$ and {0}."Value" in ({2}) and 
                                {0}.measurement in ({3}) """.format(category_m, categorical[i], cat,
                                                                    measurement_filter)
    else:
        cat_filter = """inner join examination_categorical as {0} 
                        on {1}."Name_ID"={0}."Name_ID" """.format(category_m, category_m0)

        cat_filter_where = """ and {3}."Key"=$${0}$$ and {3}."Value" in ({1}) 
                                and {3}.measurement in ({2}) """.format(categorical[i], cat, measurement_filter,
                                                                        category_m)
    category_filter = category_filter + cat_filter
    category_filter_where = category_filter_where + cat_filter_where
category_filter = category_filter + category_filter_where

for i in range(len(from1)):
    numeric_m = 'b_{}'.format(i)
    numeric_m0 = 'b_{}'.format(i - 1)
    if i == 0:
        num_filter = """Select {0}."Name_ID" FROM examination_numerical as {0}   """.format(numeric_m)

        num_filter_where = """where {0}."Key"=$${1}$$ and {0}."Value" between $${2}$$ and $${3}$$ and 
                                {0}.measurement in ({4}) """.format(numeric_m, numerical_filter_name[i], from1[i],
                                                                    to1[i], measurement_filter, )

    else:
        num_filter = """inner join examination_numerical as {0} 
                        on {1}."Name_ID" = {0}."Name_ID" """.format(numeric_m, numeric_m0)

        num_filter_where = """ and {4}."Key"=$${0}$$ and {4}."Value" between $${1}$$ and $${2}$$ 
                                and {4}.measurement in ({3}) """.format(numerical_filter_name[i], from1[i], to1[i],
                                                                        measurement_filter, numeric_m)
    numerical_filter = numerical_filter + num_filter
    numerical_filter_where = numerical_filter_where + num_filter_where
numerical_filter = numerical_filter + numerical_filter_where

# join filters
if categorical_filter and case_id and numerical_filter_name:
    sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" inner join ({2}) AS c
    on b."Name_ID" = c."Name_ID" """.format(category_filter, numerical_filter, case_id_filter)
elif not case_id and categorical_filter and numerical_filter_name:
    sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
        category_filter, numerical_filter)
elif case_id and not categorical_filter and numerical_filter_name:
    sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
        case_id_filter, numerical_filter)
elif case_id and categorical_filter and not numerical_filter_name:
    sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
        case_id_filter, category_filter)
elif not case_id and not categorical_filter and numerical_filter_name:
    sql = numerical_filter
elif not case_id and not numerical_filter_name and categorical_filter:
    sql = category_filter
elif case_id and not categorical_filter and not numerical_filter_name:
    sql = case_id_filter
else:
    sql = ''