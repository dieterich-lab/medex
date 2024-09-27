import json
from datetime import datetime

from flask import request, jsonify, Blueprint, Response
from pydantic import ValidationError

from medex.controller.helpers import get_filter_service, store_filter_status_in_session
from medex.dto.filter import DeleteFilterRequest, AddCategoricalFilterRequest, \
    CategoricalFilter, AddNumericalFilterRequest, NumericalFilter, FilterStatus

filter_controller = Blueprint('filter_controller', __name__)


@filter_controller.route('/all', methods=['GET'])
def get_all_filters():
    service = get_filter_service()
    return jsonify(service.dict())


@filter_controller.route('/save', methods=['GET'])
def save_filter_status():
    service = get_filter_service()
    data = json.dumps(service.dict())
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d_%H_%M_%S")
    file_name = f"medex_filter_{date_str}.json"
    return Response(
        data,
        mimetype="application/json",
        headers={'Content-Disposition': f"attachment; filename={file_name}"}
    )


@filter_controller.route('/load', methods=['POST'])
def load_filter_status():
    service = get_filter_service()
    try:
        data = FilterStatus.parse_obj(request.json)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    service.set_filter_status(data)
    store_filter_status_in_session(service)
    return jsonify({})


@filter_controller.route('/all', methods=['DELETE'])
def delete_all_filters():
    service = get_filter_service()
    service.delete_all_filters()
    store_filter_status_in_session(service)
    return jsonify({})


@filter_controller.route('/delete', methods=['DELETE'])
def delete_filter():
    service = get_filter_service()
    data = request.get_json()
    delete_request = DeleteFilterRequest.parse_obj(data)
    service.delete_filter(delete_request.entity)
    store_filter_status_in_session(service)
    return jsonify({})


@filter_controller.route('/add_categorical', methods=['POST'])
def add_categorical_filter():
    service = get_filter_service()
    add_request = AddCategoricalFilterRequest.parse_obj(request.get_json())
    new_filter = CategoricalFilter(**add_request.__dict__)
    service.add_filter(add_request.entity, new_filter)
    store_filter_status_in_session(service)
    return jsonify({})


@filter_controller.route('/add_numerical', methods=['POST'])
def add_numerical_filter():
    service = get_filter_service()
    add_request = AddNumericalFilterRequest.parse_obj(request.get_json())
    new_filter = NumericalFilter(**add_request.__dict__)
    service.add_filter(add_request.entity, new_filter)
    store_filter_status_in_session(service)
    return jsonify({})
