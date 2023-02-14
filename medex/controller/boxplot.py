import json

from flask import Blueprint, request, make_response, render_template

from medex.controller.helpers import get_boxplot_service
from medex.dto.boxplot import BoxplotDataRequest

boxplot_controller = Blueprint('boxplot_controller', __name__)


@boxplot_controller.route('/', methods=['GET'])
def init_boxplot():
    return render_template('boxplot.html')


@boxplot_controller.route('/json', methods=['GET'])
def get_json():
    service = get_boxplot_service()
    boxplot_request = _get_boxplot_request()
    merged_json = service.get_boxplot_json(boxplot_request)
    return merged_json


@boxplot_controller.route('/download', methods=['GET'])
def get_svg():
    service = get_boxplot_service()
    boxplot_request = _get_boxplot_request()
    image_svg = service.get_boxplot_svg(boxplot_request)
    response = make_response(image_svg)
    response.headers.set('content-type', 'attachment')
    return response


def _get_boxplot_request():
    args = request.args
    data = args.get('boxplot_data')
    json_data = json.loads(data)
    boxplot_request = BoxplotDataRequest.parse_obj(json_data)
    return boxplot_request
