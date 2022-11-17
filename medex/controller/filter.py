from flask import request, session, jsonify, Blueprint

from medex.controller.helpers import get_filter_service
from medex.dto.filter import DeleteFilterRequest, AddCategoricalFilterRequest, CategoricalFilter, \
    AddNumericalFilterRequest, NumericalFilter
from medex.services.database import get_db_session
from medex.services.filter import FilterService
from url_handlers import filtering as filtering
from webserver import app

filter_controller = Blueprint('filter_controller', __name__)


def store_filter_status_in_session(filter_service: FilterService):
    session['filter_status'] = filter_service.dict()


@filter_controller.route('/delete_all', methods=['DELETE'])
def delete_all_filters():
    service = get_filter_service()
    service.delete_all_filters()
    store_filter_status_in_session(service)
    return jsonify({})


@filter_controller.route('/delete', methods=['DELETE'])
def delete_filter():
    service = get_filter_service()
    delete_request = DeleteFilterRequest.parse_obj(request.get_json())
    service.delete_filter(delete_request.entity)
    store_filter_status_in_session(service)
    return jsonify({})


@filter_controller.route('/add_categorical', methods=['POST'])
def add_categorical_filter():
    service = get_filter_service()
    add_request = AddCategoricalFilterRequest.parse_obj(request.get_json())
    new_filter = CategoricalFilter(add_request)
    service.add_filter(add_request.entity, new_filter)
    store_filter_status_in_session(service)
    return jsonify({})


@filter_controller.route('/add_numerical', methods=['POST'])
def add_numerical_filter():
    service = get_filter_service()
    add_request = AddNumericalFilterRequest.parse_obj(request.get_json())
    new_filter = NumericalFilter(add_request)
    service.add_filter(add_request.entity, new_filter)
    store_filter_status_in_session(service)
    return jsonify({})


@app.route('/filtering', methods=['POST', 'GET'])
def filter_data():
    session_db = get_db_session()
    results = {}
    if request.is_json:
        filters = request.get_json()
        if 'clean' in filters[0]:
            results = filtering.clean_all_filter(session_db)
        elif 'clean_one_filter' in filters[0]:
            results = filtering.clean_one_filter(filters, session_db)
        elif 'cat' in filters[0]:
            results = filtering.add_categorical_filter(filters, session_db)
        elif "num" in filters[0]:
            results = filtering.add_numerical_filter(filters, session_db)
        session['filtering'] = session.get('filtering')
    return jsonify(results)
