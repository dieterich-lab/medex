from flask import jsonify

from medex.services.heatmap import HeatmapService


class HeatmapServiceMock(HeatmapService):
    def __init__(self):  # noqa
        pass

    def get_heatmap_json(self, heatmap_data):
        return jsonify({})

    def get_heatmap_svg(self, heatmap_data):
        svg_string = '<svg class="main-svg xmlns="http://www.w3.org/2000/svg"></svg>'
        result = str.encode(svg_string)
        return result
