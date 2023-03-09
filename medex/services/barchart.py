import json
import textwrap

import plotly
from pandas import DataFrame
from sqlalchemy import select, func, distinct, literal_column, and_

from medex.dto.barchart import BarChartDataRequest
from medex.services.filter import FilterService
from medex.database_schema import TableCategorical
import plotly.express as px


class BarChartService:
    SVG_HEADER = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                     <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                 """

    def __init__(
            self,
            database_session,
            filter_service: FilterService
    ):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_barchart_json(self, barchart_data: BarChartDataRequest):
        result = self._get_result_from_database(barchart_data)
        fig = self._update_figure_layout(barchart_data, result)
        image_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return image_json

    def get_barchart_svg(self, barchart_data: BarChartDataRequest):
        result = self._get_result_from_database(barchart_data)
        fig = self._update_figure_layout(barchart_data, result)
        image_data = fig.to_image(format='svg')
        return self.SVG_HEADER + image_data

    def _get_result_from_database(self, barchart_data):
        query_select = self._get_table_select(barchart_data)
        query_with_filter = self._filter_service.apply_filter(TableCategorical, query_select)
        query_select_count = self._get_entity_value_count(barchart_data, query_with_filter)
        result = self._database_session.execute(query_select_count)
        return result

    @staticmethod
    def _get_table_select(barchart_data):
        query_select = select(
            func.string_agg(distinct(TableCategorical.value), literal_column("'<br>'")).label('value'),
            TableCategorical.measurement
        ).where(
            and_(
                TableCategorical.key == barchart_data.key,
                TableCategorical.value.in_(barchart_data.categories),
                TableCategorical.measurement.in_(barchart_data.measurements),
            )
        ).group_by(TableCategorical.name_id, TableCategorical.measurement)
        return query_select

    @staticmethod
    def _get_entity_value_count(barchart_data, query_with_filter):
        query_select_count = select(
            query_with_filter.c.value.label(barchart_data.key),
            query_with_filter.c.measurement,
            func.count(query_with_filter.c.value).label('count')
        ).group_by(query_with_filter.c.value, query_with_filter.c.measurement)
        return query_select_count

    @staticmethod
    def _update_figure_layout(barchart_data, result):
        df = DataFrame(result.all())
        if df.empty:
            fig = {'data': [], 'layout': {}}
        else:
            df[barchart_data.key] = df[barchart_data.key].str.wrap(30).replace(to_replace=[r"\\n", "\n"],
                                                                               value=["<br>", "<br>"],
                                                                               regex=True)
            df['%'] = 100 * df['count'] / df.groupby('measurement')['count'].transform('sum')
            legend = textwrap.wrap(barchart_data.key, width=20)
            y = 'count' if barchart_data.plot_type == 'count' else '%'
            fig = px.bar(df, x='measurement', y=y, color=barchart_data.key, barmode='group', template="plotly_white")
            fig.update_layout(
                font=dict(size=16),
                legend_title='<br>'.join(legend),
                title={'text': barchart_data.key, 'x': 0.5, 'xanchor': 'center'}
            )
        return fig
