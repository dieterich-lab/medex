import json
from flask import Blueprint, request, make_response, render_template
from medex.controller.helpers import get_scatter_plot_service
from medex.dto.scatter_plot import ScatterPlotDataRequest

scatter_plot_controller = Blueprint('scatter_plot_controller', __name__)


@scatter_plot_controller.route('/', methods=['GET'])
def init_scatter_plot():
    return render_template('scatter_plot.html')


@scatter_plot_controller.route('/json', methods=['GET'])
def get_scatter_plot_json():
    scatter_plot_service = get_scatter_plot_service()
    scatter_plot_request = _get_parsed_request()
    image_json = scatter_plot_service.get_image_json(scatter_plot_request)
    return image_json


@scatter_plot_controller.route('/download', methods=['GET'])
def get_scatter_plot_svg_for_download():
    scatter_plot_service = get_scatter_plot_service()
    scatter_plot_request = _get_parsed_request()
    image_data = scatter_plot_service.get_image_svg(scatter_plot_request)
    response = make_response(image_data)
    response.headers.set('content-type', 'attachment')
    return response


def _get_parsed_request():
    args = request.args
    data = args.get('scatter_plot_data')
    json_data = json.loads(data)
    scatter_plot_request = ScatterPlotDataRequest.parse_obj(json_data)
    return scatter_plot_request
