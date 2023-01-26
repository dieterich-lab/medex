from flask import jsonify

from medex.services.histogram import HistogramService


class HistogramServiceMock(HistogramService):
    def __init__(self):  # noqa
        pass

    def get_image_json(self, histogram_data):
        return jsonify({})

    def get_image_svg(self, histogram_data):
        svg_string = '<svg class="main-svg xmlns="http://www.w3.org/2000/svg"></svg>'
        result = str.encode(svg_string)
        return result

