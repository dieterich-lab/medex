from flask import jsonify

from medex.services.scatter_plot import ScatterPlotService


class ScatterPlotServiceMock(ScatterPlotService):
    def __init__(self):  # noqa
        pass

    def get_image_svg(self, scatter_plot_data) -> bytes:
        svg_string = '<svg class="main-svg xmlns="http://www.w3.org/2000/svg"></svg>'
        result = str.encode(svg_string)
        return result

    def get_image_json(self, scatter_plot_data):
        return jsonify({})
