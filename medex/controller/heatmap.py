import json

from flask import Blueprint, request, make_response, render_template

from medex.controller.helpers import get_heatmap_service
from medex.dto.heatmap import HeatmapDataRequest

heatmap_controller = Blueprint('heatmap_controller', __name__)


@heatmap_controller.route('/', methods=['GET'])
def init_heatmap():
    return render_template('heatmap.html')


@heatmap_controller.route('/json', methods=['GET'])
def get_heatmap_plot_json():
    service = get_heatmap_service()
    heatmap_request = _get_parsed_request()
    image_json = service.get_heatmap_json(heatmap_request)
    return image_json


@heatmap_controller.route('/download', methods=['GET'])
def get_heatmap_svg_for_download():
    service = get_heatmap_service()
    heatmap_request = _get_parsed_request()
    image_svg = service.get_heatmap_svg(heatmap_request)
    response = make_response(image_svg)
    response.headers.set('content-type', 'attachment')
    return response


def _get_parsed_request():
    args = request.args
    data = args.get('heatmap_data')
    data_json = json.loads(data)
    heatmap_request = HeatmapDataRequest.parse_obj(data_json)
    return heatmap_request
