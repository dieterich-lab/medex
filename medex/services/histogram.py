import json
import textwrap

import plotly
from pandas import DataFrame
from sqlalchemy import select, func, and_

from medex.services.filter import FilterService
from medex.database_schema import NumericalValueTable, CategoricalValueTable
import plotly.express as px


def _get_fix_annotation_text(orig: str):
    value = orig.split('=')[-1]
    if len(value) > 5:
        return value
    else:
        return orig


class HistogramService:
    SVG_HEADER = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                     <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                     """

    def __init__(self, database_session, filter_service: FilterService):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_image_json(self, histogram_data):
        fig = self._get_histogram_plot(histogram_data)
        image_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return image_json

    def get_image_svg(self, histogram_data):
        fig = self._get_histogram_plot(histogram_data)
        image_svg = fig.to_image(format='svg')
        return self.SVG_HEADER + image_svg

    def _get_histogram_plot(self, histogram_data):
        df = self.get_dataframe_for_histogram_and_boxplot(histogram_data)
        if df.empty:
            fig = {'data': [], 'layout': {}}
        else:
            fig = self._get_figure_with_layout(df, histogram_data)
        return fig

    def get_dataframe_for_histogram_and_boxplot(self, histogram_data):
        query_select = self._select_table_columns(histogram_data)
        query_select_with_where = self._get_columns_with_data(histogram_data, query_select)
        query_with_filter = self._filter_service.apply_filter(NumericalValueTable, query_select_with_where)
        df = self._get_dataframe(histogram_data, query_with_filter)
        return df

    @staticmethod
    def _select_table_columns(histogram_data):
        query_select = select(
            NumericalValueTable.patient_id, NumericalValueTable.measurement,
            func.avg(NumericalValueTable.value).label(histogram_data.numerical_entity),
            CategoricalValueTable.value.label(histogram_data.categorical_entity)
        )
        return query_select

    @staticmethod
    def _get_columns_with_data(histogram_data, query_select):
        query_select_with_where = query_select.where(
            and_(
                NumericalValueTable.key == histogram_data.numerical_entity,
                CategoricalValueTable.key == histogram_data.categorical_entity,
                CategoricalValueTable.value.in_(histogram_data.categories),
                NumericalValueTable.measurement.in_(histogram_data.measurements),
                CategoricalValueTable.patient_id == NumericalValueTable.patient_id,
            )
        ).group_by(NumericalValueTable.patient_id, NumericalValueTable.measurement, CategoricalValueTable.value)
        return query_select_with_where

    def _get_dataframe(self, histogram_data, query_with_filter):
        results = self._database_session.execute(query_with_filter)
        df = DataFrame(results.all())
        if not df.empty:
            df[histogram_data.categorical_entity] = df[histogram_data.categorical_entity].str.wrap(30).replace(
                to_replace=[r"\\n", "\n"],
                value=["<br>", "<br>"],
                regex=True
            )
        return df

    def _get_figure_with_layout(self, df, histogram_data):
        fig = px.histogram(df, x=histogram_data.numerical_entity, facet_row='measurement',
                           color=histogram_data.categorical_entity, barmode='overlay', nbins=histogram_data.bins,
                           opacity=0.7, template="plotly_white")
        legend = textwrap.wrap(histogram_data.categorical_entity, width=20)
        fig.update_layout(
            font=dict(size=16),
            legend_title='<br>'.join(legend),
            height=1000,
            title={'text': '<b>' + histogram_data.numerical_entity + '</b> grouped by '
                           '<b>' + histogram_data.categorical_entity + '</b>',
                   'x': 0.5,
                   'xanchor': 'center'}
        )
        self._fix_measurement_labels(fig)
        return fig

    @staticmethod
    def _fix_measurement_labels(fig):
        fig.for_each_annotation(lambda a: a.update(text=_get_fix_annotation_text(a.text)))
