from flask import jsonify

from medex.services.barchart import BarChartService


class BarChartServiceMock(BarChartService):
    def __init__(self):  # noqa
        pass

    def get_barchart_json(self, barchart_data):
        return jsonify({})

    def get_barchart_svg(self, barchart_data):
        svg_string = '<svg class="main-svg xmlns="http://www.w3.org/2000/svg"></svg>'
        result = str.encode(svg_string)
        return result
