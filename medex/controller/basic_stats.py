import csv
import io
import json
from flask import Blueprint, request, send_file, jsonify
from medex.controller.helpers import get_basic_stats_service
from medex.dto.basic_stats import BasicStatsNumericalDataRequest, BasicStatsCategoricalDataRequest, \
    BasicStatsDateRequest

basic_stats_controller = Blueprint('basic_stats_controller', __name__)


@basic_stats_controller.route('/numerical', methods=['GET'])
def get_basic_stats_numerical():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_numerical_request = BasicStatsNumericalDataRequest.parse_obj(json.loads(args.get('basic_stats_data')))
    result_dict = service.get_basic_stats_for_numerical_entities(basic_stats_numerical_request)
    response = {'data': result_dict}
    return jsonify(response)


@basic_stats_controller.route('/categorical', methods=['GET'])
def get_basic_stats_categorical():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_categorical_request = BasicStatsCategoricalDataRequest.parse_obj(
        json.loads(args.get('basic_stats_data'))
    )
    result_dict = service.get_basic_stats_for_categorical_entities(basic_stats_categorical_request)
    response = {'data': result_dict}
    return jsonify(response)


@basic_stats_controller.route('/date', methods=['GET'])
def get_basic_stats_date():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_date_request = BasicStatsDateRequest.parse_obj(json.loads(args.get('basic_stats_data')))
    result_dict = service.get_basic_stats_for_date_entities(basic_stats_date_request)
    response = {'data': result_dict}
    return jsonify(response)


@basic_stats_controller.route('/numerical_csv', methods=['GET'])
def get_basic_stats_numerical_download():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_numerical_request = BasicStatsNumericalDataRequest.parse_obj(json.loads(args.get('basic_stats_data')))
    result_dict = service.get_basic_stats_for_numerical_entities(basic_stats_numerical_request)
    result_bytes = _get_dict_to_csv(result_dict)
    return send_file(result_bytes,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name='basic_stats_numerical.csv')


@basic_stats_controller.route('/categorical_csv', methods=['GET'])
def get_basic_stats_categorical_download():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_categorical_request = BasicStatsCategoricalDataRequest.parse_obj(
        json.loads(args.get('basic_stats_data'))
    )
    result_dict = service.get_basic_stats_for_categorical_entities(basic_stats_categorical_request)
    result_bytes = _get_dict_to_csv(result_dict)
    return send_file(result_bytes,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name='basic_stats_categorical.csv')


@basic_stats_controller.route('/date_csv', methods=['GET'])
def get_basic_stats_date_download():
    service = get_basic_stats_service()
    args = request.args
    basic_stats_date_request = BasicStatsDateRequest.parse_obj(json.loads(args.get('basic_stats_data')))
    result_dict = service.get_basic_stats_for_date_entities(basic_stats_date_request)
    result_bytes = _get_dict_to_csv(result_dict)
    return send_file(result_bytes,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name='basic_stats_for_date_entities.csv')


def _get_dict_to_csv(result):
    field_names = [key for key in result[0].keys()]
    with io.StringIO() as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(result)
        data = csvfile.getvalue()
    buf_byt = io.BytesIO(data.encode("utf-8"))
    return buf_byt
