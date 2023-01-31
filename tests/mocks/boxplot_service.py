from flask import jsonify

from medex.services.boxplot import BoxplotService


class BoxplotServiceMock(BoxplotService):
    def __init__(self):  # noqa
        pass

    def get_boxplot_json(self, boxplot_data):
        return jsonify({})

    def get_boxplot_svg(self, boxplot_data):
        svg_string = '<svg class="main-svg xmlns="http://www.w3.org/2000/svg"></svg>'
        result = str.encode(svg_string)
        return result
