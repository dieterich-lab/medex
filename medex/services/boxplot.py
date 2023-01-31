import json
import textwrap

import plotly

from medex.services.filter import FilterService
from medex.services.histogram import HistogramService
import plotly.graph_objects as go
import plotly.express as px


class BoxplotService:
    SVG_HEADER = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                     <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                     """

    def __init__(self, database_session, filter_service: FilterService, histogram_service: HistogramService):
        self._database_session = database_session
        self._filter_service = filter_service
        self._histogram_service = histogram_service

    def get_boxplot_json(self, boxplot_data):
        df = self._histogram_service.get_dataframe_for_histogram_and_boxplot(boxplot_data)
        fig_table = self._get_boxplot_count_table(boxplot_data, df)
        figure = self._get_boxplot_figure(boxplot_data, df)
        figure = self._update_figure_layout(boxplot_data, figure)
        table_json = json.dumps(fig_table, cls=plotly.utils.PlotlyJSONEncoder)
        image_json = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
        return image_json, table_json

    def get_boxplot_svg(self, boxplot_data):
        df = self._histogram_service.get_dataframe_for_histogram_and_boxplot(boxplot_data)
        figure = self._get_boxplot_figure(boxplot_data, df)
        figure = self._update_figure_layout(boxplot_data, figure)
        image_svg = figure.to_image(format='svg')
        return self.SVG_HEADER + image_svg

    @staticmethod
    def _get_boxplot_count_table(boxplot_data, df):
        table = df.groupby(['measurement', boxplot_data.categorical_entity]).size().reset_index(name='counts')
        table = table.pivot(index='measurement', columns=boxplot_data.categorical_entity, values='counts').reset_index()
        fig_table = go.Figure(data=[
            go.Table(
                header=dict(values=list(table.columns)),
                cells=dict(values=table.transpose().values.tolist())
            )
        ])
        height = 30 + len(table) * 30
        fig_table.update_layout(
            height=height, margin=dict(r=5, l=5, t=5, b=5)
        )
        return fig_table

    @staticmethod
    def _get_boxplot_figure(boxplot_data, df):
        if boxplot_data.plot_type == 'linear':
            fig = px.box(df, x='measurement', y=boxplot_data.numerical_entity, color=boxplot_data.categorical_entity,
                         template="plotly_white")
        else:
            fig = px.box(df, x='measurement', y=boxplot_data.numerical_entity, color=boxplot_data.categorical_entity,
                         template="plotly_white", log_y=True)
        return fig

    @staticmethod
    def _update_figure_layout(boxplot_data, fig):
        legend = textwrap.wrap(boxplot_data.categorical_entity, width=20)
        fig.update_layout(
            font=dict(size=16),
            legend_title='<br>'.join(legend),
            title={
                'text': '<b>' + boxplot_data.numerical_entity + '</b> grouped by '
                                                                '<b>' + boxplot_data.categorical_entity + '</b>',
                'x': 0.5,
                'xanchor': 'center'}
        )
        return fig
