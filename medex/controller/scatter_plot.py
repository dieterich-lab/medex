import json

from flask import Blueprint, request, send_file

from medex.controller.helpers import get_scatter_plot_service
from medex.dto.scatter_plot import ScatterPlotDataRequest

scatter_plot_controller = Blueprint('scatter_plot_controller', __name__)


@scatter_plot_controller.route('/scatter_plot', methods=['GET'])
def get_scatter_plot():
    scatter_plot_service = get_scatter_plot_service()
    args = request.args
    scatter_plot_request = ScatterPlotDataRequest.parse_obj(json.loads(args.get('scatter_plot_data')))
    figure = scatter_plot_service.get_scatter_plot(
        scatter_plot_request.measurement_x_axis,
        scatter_plot_request.key_x_axis,
        scatter_plot_request.measurement_y_axis,
        scatter_plot_request.key_y_axis,
        scatter_plot_request.date_range,
        scatter_plot_request.scale,
        scatter_plot_request.add_group_by
    )
    return send_file(figure, mimetype='image/svg')
