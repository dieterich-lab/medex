import json
import textwrap

import plotly
from pandas import DataFrame
from sqlalchemy import select, func, and_, distinct, literal_column
from sqlalchemy.orm import aliased
from medex.services.filter import FilterService
from modules.models import TableNumerical, TableCategorical
import plotly.graph_objects as go


class ScatterPlotService:
    SVG_HEADER = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                     <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                 """

    def __init__(
            self,
            database_session,
            filter_service: FilterService,
    ):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_image_svg(self, scatter_plot_data) -> bytes:
        result = self._get_result_from_database(scatter_plot_data)
        image_data = self._get_svg(scatter_plot_data, result)
        return image_data

    def get_image_json(self, scatter_plot_data):
        result = self._get_result_from_database(scatter_plot_data)
        image_json = self._get_json(scatter_plot_data, result)
        return image_json

    def _get_result_from_database(self, scatter_plot_data):
        query_select = self._get_table_self_join(scatter_plot_data)
        query_with_filter = self._filter_service.apply_filter(TableNumerical, query_select)
        query_with_group = self._get_group_by(scatter_plot_data.add_group_by, query_with_filter)
        result = self._database_session.execute(query_with_group)
        return result

    @staticmethod
    def _get_table_self_join(scatter_plot_data):
        table_alias = aliased(TableNumerical)
        query_select = select(
            TableNumerical.name_id,
            func.avg(TableNumerical.value).label('value1'),
            func.avg(table_alias.value).label('value2')
        ).where(
            and_(
                TableNumerical.key == scatter_plot_data.entity_x_axis,
                TableNumerical.measurement == scatter_plot_data.measurement_x_axis,
                table_alias.key == scatter_plot_data.entity_y_axis,
                table_alias.measurement == scatter_plot_data.measurement_y_axis,
                TableNumerical.name_id == table_alias.name_id,
                TableNumerical.date.between(
                    scatter_plot_data.date_range.from_date.strftime('%Y-%m-%d'),
                    scatter_plot_data.date_range.to_date.strftime('%Y-%m-%d'))
            )
        ).group_by(TableNumerical.name_id)
        return query_select

    @staticmethod
    def _get_group_by(add_group_by, query_with_filter):
        if add_group_by.key != 'Search Entity':
            query_with_filter = select(
                query_with_filter.c.name_id,
                func.avg(query_with_filter.c.value1).label('value1'),
                func.avg(query_with_filter.c.value2).label('value2'),
                func.string_agg(distinct(TableCategorical.value), literal_column("'<br>'")).label(add_group_by.key)
            ).join(
                TableCategorical,
                TableCategorical.name_id == query_with_filter.c.name_id
            ).where(
                and_(
                    TableCategorical.key == add_group_by.key,
                    TableCategorical.value.in_(add_group_by.categories)
                )
            ).group_by(query_with_filter.c.name_id)
        return query_with_filter

    def _get_svg(self, scatter_plot_data, result):
        fig = self._create_scatter_plot_figure(result, scatter_plot_data)
        image_data = fig.to_image(format='svg')
        return self.SVG_HEADER + image_data

    def _get_json(self, scatter_plot_data, result):
        fig = self._create_scatter_plot_figure(result, scatter_plot_data)
        image_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return image_json

    def _create_scatter_plot_figure(self, result, scatter_plot_data):
        df = DataFrame(result.all())
        df.rename(
            columns={
                'value1': f'{scatter_plot_data.entity_x_axis}_{scatter_plot_data.measurement_x_axis}',
                'value2': f'{scatter_plot_data.entity_y_axis}_{scatter_plot_data.measurement_y_axis}'
            },
            inplace=True
        )
        number_of_points = len(df.index)
        x_axis, y_axis = scatter_plot_data.entity_x_axis + '_' + scatter_plot_data.measurement_x_axis, \
                         scatter_plot_data.entity_y_axis + '_' + scatter_plot_data.measurement_y_axis
        figure = go.Figure()
        figure = self._add_trace_to_figure(scatter_plot_data.add_group_by, df, figure, x_axis, y_axis)
        figure = self._update_figure_layout(scatter_plot_data, figure, number_of_points, x_axis, y_axis)
        figure = self._get_log_scale(figure, scatter_plot_data)
        return figure

    @staticmethod
    def _add_trace_to_figure(add_group_by, df, fig, x_axis, y_axis):
        if add_group_by.key != 'Search Entity':
            for category in add_group_by.categories:
                df_new = df[df[add_group_by.key] == category]
                fig.add_trace(
                    go.Scattergl(
                        x=df_new[x_axis], y=df_new[y_axis], mode='markers', name=category
                    )
                )
        else:
            fig.add_trace(
                go.Scattergl(
                    x=df[x_axis], y=df[y_axis], mode='markers', marker=dict(line=dict(width=1, color='DarkSlateGrey'))
                )
            )
        return fig

    @staticmethod
    def _update_figure_layout(scatter_plot_data, fig, number_of_points, x_axis, y_axis):
        split_text = textwrap.wrap("Compare values of <b>" +
                                   scatter_plot_data.entity_x_axis + "</b> : " + 'Visit' + " <b>" +
                                   scatter_plot_data.measurement_x_axis + "</b> and <br> <b>" +
                                   scatter_plot_data.entity_y_axis + "</b> : " + 'Visit' + " <b>" +
                                   scatter_plot_data.measurement_y_axis + "</b>" + "<br> Number of Points: " +
                                   str(number_of_points),
                                   width=100)
        x_axis = textwrap.wrap(x_axis)
        y_axis = textwrap.wrap(y_axis, width=40)
        if scatter_plot_data.add_group_by is not None:
            legend = textwrap.wrap(scatter_plot_data.add_group_by.key, width=20)
        else:
            legend = textwrap.wrap('')
        fig.update_layout(
            template="plotly_white",
            legend_title='<br>'.join(legend),
            font=dict(size=16),
            xaxis_title='<br>'.join(x_axis),
            yaxis_title='<br>'.join(y_axis),
            title={'text': ''.join(split_text), 'x': 0.5, 'xanchor': 'center', })
        return fig

    @staticmethod
    def _get_log_scale(fig, scatter_plot_data):
        if scatter_plot_data.scale.log_x is True:
            fig.update_xaxes(type="log")
        if scatter_plot_data.scale.log_y is True:
            fig.update_yaxes(type="log")
        return fig
