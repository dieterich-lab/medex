from flask import Blueprint, jsonify

from medex.controller.helpers import get_measurement_service


measurement_controller = Blueprint('measurement_controller', __name__)


@measurement_controller.route('/', methods=['GET'])
def _get():
    service = get_measurement_service()
    info = service.get_info()
    return jsonify(info.dict())
