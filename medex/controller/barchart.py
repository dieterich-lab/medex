import json

from flask import Blueprint, request, make_response

from medex.controller.helpers import get_barchart_service
from medex.dto.barchart import BarChartDataRequest

barchart_controller = Blueprint('barchart_controller', __name__)


@barchart_controller.route('/barchart/json', methods=['GET'])
def get_barchart_json():
    service = get_barchart_service()
    barchart_request = _get_parsed_request()
    image_json = service.get_barchart_json(barchart_request)
    return image_json


@barchart_controller.route('/barchart/download', methods=['GET'])
def get_barchart_svg():
    service = get_barchart_service()
    barchart_request = _get_parsed_request()
    image_data = service.get_barchart_svg(barchart_request)
    response = make_response(image_data)
    response.headers.set('content-type', 'attachment')
    return response


def _get_parsed_request():
    args = request.args
    data = args.get('barchart_data')
    json_data = json.loads(data)
    barchart_request = BarChartDataRequest.parse_obj(json_data)
    return barchart_request
