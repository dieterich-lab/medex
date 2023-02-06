import io
import json
import pandas as pd

from flask import Blueprint, request, send_file

from medex.controller.helpers import get_basic_stats_service
from medex.dto.basic_stats import BasicStatsNumericalDataRequest

basic_stats_controller = Blueprint('basic_stats_controller', __name__)


@basic_stats_controller.route('/numerical', methods=['GET'])
def get_basic_stats_numerical():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_numerical_request = BasicStatsNumericalDataRequest.parse_obj(json.loads(args.get('basic_stats_data')))
    result_json = service.get_basic_stats_for_numerical_entities(basic_stats_numerical_request)
    return result_json


@basic_stats_controller.route('/numerical_csv', methods=['GET'])
def get_basic_stats_numerical_download():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_numerical_request = BasicStatsNumericalDataRequest.parse_obj(json.loads(args.get('basic_stats_data')))
    result_json = service.get_basic_stats_for_numerical_entities(basic_stats_numerical_request)
    with open(result_json, encoding='utf-8') as input_file:
        df = pd.read_json(input_file)
    result_csv = io.BytesIO(bytes(df.to_csv(encoding='utf-8', index=False)))
    return send_file(result_csv,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name='basic_stats_numerical.csv')
