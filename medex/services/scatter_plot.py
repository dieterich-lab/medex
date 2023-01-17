import textwrap
from typing import Optional, List

from pandas import DataFrame
from sqlalchemy import select, func, and_, distinct, literal_column
from sqlalchemy.orm import aliased

from medex.dto.scatter_plot import ScaleScatterPlot, GroupByCategoricalEntity, DateRange
from medex.services.filter import FilterService
from modules.models import TableNumerical, TableCategorical
import plotly.graph_objects as go


class ScatterPlotService:
    def __init__(
            self,
            database_session,
            filter_service: FilterService,
    ):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_scatter_plot(
            self,
            measurement_x_axis: str,
            entity_x_axis: str,
            measurement_y_axis: str,
            entity_y_axis: str,
            date_range: Optional[DateRange] = None,
            scale: Optional[ScaleScatterPlot] = None,
            add_group_by: Optional[GroupByCategoricalEntity] = None,
    ) -> (bytes, List[tuple]):
        query_select = self._get_table_self_join(measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis,
                                                 date_range)
        query_with_filter = self._filter_service.apply_filter(TableNumerical, query_select)
        query_with_group = self._get_group_by(add_group_by, query_with_filter)
        result = self._database_session.execute(query_with_group)
        figure = self._get_scatter_plot_figure(add_group_by, result, entity_x_axis, entity_y_axis, measurement_x_axis,
                                               measurement_y_axis, scale)
        return figure

    @staticmethod
    def _get_table_self_join(measurement_x_axis, entity_x_axis, measurement_y_axis, entity_y_axis, date_range):
        table_alias = aliased(TableNumerical)
        query_select = select(
            TableNumerical.name_id,
            func.avg(TableNumerical.value).label('value1'),
            func.avg(table_alias.value).label('value2')
        ).where(
            and_(
                TableNumerical.key == entity_x_axis,
                TableNumerical.measurement == measurement_x_axis,
                table_alias.key == entity_y_axis,
                table_alias.measurement == measurement_y_axis,
                TableNumerical.name_id == table_alias.name_id,
                TableNumerical.date.between(
                    date_range.from_date.strftime('%Y-%m-%d'),
                    date_range.to_date.strftime('%Y-%m-%d'))
            )
        ).group_by(TableNumerical.name_id)
        return query_select

    @staticmethod
    def _get_group_by(add_group_by, query_with_filter):
        if add_group_by is not None:
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

    def _get_scatter_plot_figure(self, add_group_by, result, entity_x_axis, entity_y_axis, measurement_x_axis,
                                 measurement_y_axis, scale):
        df = DataFrame(result.all())
        df.rename(
            columns={
                'value1': f'{entity_x_axis}_{measurement_x_axis}',
                'value2': f'{entity_y_axis}_{measurement_y_axis}'
            },
            inplace=True
        )
        number_of_points = len(df.index)
        x_axis, y_axis = entity_x_axis + '_' + measurement_x_axis, entity_y_axis + '_' + measurement_y_axis
        fig = go.Figure()
        self._add_trace_to_figure(add_group_by, df, fig, x_axis, y_axis)
        self._update_figure_layout(add_group_by, entity_x_axis, entity_y_axis, fig, measurement_x_axis,
                                   measurement_y_axis, number_of_points, x_axis, y_axis)

        if scale.log_x is True:
            fig.update_xaxes(type="log")
        if scale.log_y is True:
            fig.update_yaxes(type="log")

        figure = fig.to_image(format='svg')
        return figure

    @staticmethod
    def _add_trace_to_figure(add_group_by, df, fig, x_axis, y_axis):
        if add_group_by is not None:
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

    @staticmethod
    def _update_figure_layout(add_group_by, entity_x_axis, entity_y_axis, fig, measurement_x_axis, measurement_y_axis,
                              number_of_points, x_axis, y_axis):
        split_text = textwrap.wrap("Compare values of <b>" +
                                   entity_x_axis + "</b> : " + 'Visit' + " <b>" +
                                   measurement_x_axis + "</b> and <b>" +
                                   entity_y_axis + "</b> : " + 'Visit' + " <b>" +
                                   measurement_y_axis + "</b>" + "<br> Number of Points: " +
                                   str(number_of_points),
                                   width=100)
        x_axis = textwrap.wrap(x_axis)
        y_axis = textwrap.wrap(y_axis, width=40)
        legend = textwrap.wrap(add_group_by.key, width=20)
        fig.update_layout(
            template="plotly_white",
            legend_title='<br>'.join(legend),
            font=dict(size=16),
            xaxis_title='<br>'.join(x_axis),
            yaxis_title='<br>'.join(y_axis),
            title={'text': ''.join(split_text), 'x': 0.5, 'xanchor': 'center', })
