from flask import Blueprint, jsonify

from medex.controller.helpers import get_entity_service

entity_controller = Blueprint('entity_controller', __name__)


@entity_controller.route('/all', methods=['GET'])
def get_all_entities():
    service = get_entity_service()
    entities = service.get_all_as_dict()
    return jsonify(entities)
