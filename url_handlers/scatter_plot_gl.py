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


