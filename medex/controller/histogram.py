import json

from flask import Blueprint, request, make_response

from medex.controller.helpers import get_histogram_service
from medex.dto.histogram import HistogramDataRequest

histogram_controller = Blueprint('histogram_controller', __name__)


@histogram_controller.route('/histogram/json', methods=['GET'])
def get_histogram_json():
    service = get_histogram_service()
    histogram_request = _get_parsed_request()
    image_json = service.get_image_json(histogram_request)
    return image_json


@histogram_controller.route('/histogram/download', methods=['GET'])
def get_histogram_svg_download():
    service = get_histogram_service()
    histogram_request = _get_parsed_request()
    image_data = service.get_image_svg(histogram_request)
    response = make_response(image_data)
    response.headers.set('content-type', 'attachment')
    return response


def _get_parsed_request():
    args = request.args
    data = args.get('histogram_data')
    json_data = json.loads(data)
    histogram_request = HistogramDataRequest.parse_obj(json_data)
    return histogram_request
