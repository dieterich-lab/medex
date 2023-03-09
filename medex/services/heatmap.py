import json

import plotly
from pandas import DataFrame
from scipy.stats import pearsonr
from sqlalchemy import func, case, select
from medex.services.filter import FilterService
from medex.database_schema import TableNumerical
import plotly.graph_objects as go
import plotly.figure_factory as ff


class HeatmapService:
    SVG_HEADER = b"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                     <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                 """

    def __init__(self, database_session, filter_service: FilterService):
        self._database_session = database_session
        self._filter_service = filter_service

    def get_heatmap_json(self, heatmap_data):
        df = self._get_results_dataframe(heatmap_data)
        if df.empty:
            fig = {'data': [], 'layout': {}}
        else:
            correlated_values, number_of_values = self._get_pearson_correlation(df)
            fig = self._get_updated_figure(correlated_values, number_of_values, heatmap_data)
        image_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return image_json

    def get_heatmap_svg(self, heatmap_data):
        df = self._get_results_dataframe(heatmap_data)
        correlated_values, number_of_values = self._get_pearson_correlation(df)
        fig = self._get_updated_figure(correlated_values, number_of_values, heatmap_data)
        image_svg = fig.to_image(format='svg')
        return self.SVG_HEADER + image_svg

    def _get_results_dataframe(self, heatmap_data):
        query_select = self._select_table_data(heatmap_data)
        query_with_filter = self._filter_service.apply_filter(TableNumerical, query_select)
        results = self._database_session.execute(query_with_filter)
        df = DataFrame(results.all())
        if not df.empty:
            df = df.drop(columns=['name_id'])
        return df

    @staticmethod
    def _select_table_data(heatmap_data):
        case_when = [
            func.min(case((TableNumerical.key == i, TableNumerical.value))).label(i)
            for i in heatmap_data.entities
        ]
        query_select = select(TableNumerical.name_id, *case_when) \
            .group_by(TableNumerical.name_id)
        return query_select

    @staticmethod
    def _get_pearson_correlation(df):
        df_columns = DataFrame(columns=df.columns)
        correlated_values = df_columns.transpose().join(df_columns, how='outer')
        number_of_values = df_columns.transpose().join(df_columns, how='outer')
        p_values = df_columns.transpose().join(df_columns, how='outer')
        for row in df.columns:
            for col in df.columns:
                if col == row:
                    df_correlated = df[[row]].dropna().astype(float)
                else:
                    df_correlated = df[[row, col]].dropna().astype(float)
                if len(df_correlated) < 2:
                    correlated_values[row][col], p_values[row][col] = None, None
                else:
                    number_of_values[row][col] = len(df_correlated)
                    correlated_values[row][col], p_values[row][col] = pearsonr(df_correlated[row], df_correlated[col])
        correlated_values = correlated_values.astype(float).round(decimals=2)
        return correlated_values, number_of_values

    @staticmethod
    def _get_updated_figure(correlated_values, number_of_values, heatmap_data):
        correlated_values_list = correlated_values.T.values.tolist()
        number_of_values_list = number_of_values.T.values.tolist()
        fig = go.Figure(
            data=ff.create_annotated_heatmap(
                z=correlated_values_list, x=heatmap_data.entities, y=heatmap_data.entities,
                annotation_text=number_of_values_list, colorscale='Viridis', showscale=True)
        )
        fig.update_traces(text=number_of_values_list, texttemplate="%{text}")
        fig.update_layout(height=600, title='Heatmap shown with Pearson Correlation')
        return fig
