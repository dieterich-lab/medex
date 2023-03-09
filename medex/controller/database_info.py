from flask import Blueprint, jsonify

from medex.controller.helpers import get_database_info_service

database_info_controller = Blueprint('database_info_controller', __name__)


@database_info_controller.route('/', methods=['GET'])
def get_all_entities():
    service = get_database_info_service()
    info = service.get()
    return jsonify(info.__dict__)
