from flask import Blueprint, request, jsonify

from medex.controller.helpers import get_data_service
from medex.dto.data import FilteredDataRequest, FilteredDataFlatResponse

data_controller = Blueprint('data_controller', __name__)


@data_controller.route('/filtered_data_flat', methods=['GET'])
def get_filtered_data_flat():
    data_service = get_data_service()
    request_json = request.get_json()
    data_request = FilteredDataRequest.parse_obj(request_json)
    filtered_data_flat = data_service.get_filtered_data_flat(
        data_request.measurements,
        data_request.entities,
    )
    result = [
        item.dict()
        for item in filtered_data_flat
    ]
    return jsonify(result)


@data_controller.route('/filtered_data_by_measurement', methods=['GET'])
def get_filtered_data_by_measurement():
    data_service = get_data_service()
    request_json = request.get_json()
    data_request = FilteredDataRequest.parse_obj(request_json)
    filtered_data_by_measurement = data_service.get_filtered_data_by_measurement(
        data_request.measurements,
        data_request.entities,
    )
    result = [
        item.dict()
        for item in filtered_data_by_measurement
    ]
    return jsonify(result)
