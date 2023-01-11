import json

from flask import Blueprint, request, jsonify

from medex.controller.helpers import get_data_service
from medex.dto.data import FilteredDataRequest, SortOrder, SortDirection, SortItem, FilteredDataFlatResponse

data_controller = Blueprint('data_controller', __name__)


@data_controller.route('/flat', methods=['GET'])
def get_filtered_data_flat():
    data_service = get_data_service()
    args = request.args
    filtered_data_request = FilteredDataRequest.parse_obj(json.loads(args.get('table_data')))
    limit = args.get('length')
    offset = args.get('start')
    sort_column_idx = args.get('order[0][column]')
    sort_direction = args.get('order[0][dir]')
    sort_order = _get_sort_order(sort_column_idx, sort_direction)
    result, total = data_service.get_filtered_data_flat(
        filtered_data_request.measurements,
        filtered_data_request.entities,
        limit,
        offset,
        sort_order
    )
    filtered_data_flat_response = FilteredDataFlatResponse(
        data=result,
        iTotalDisplayRecords=total,
        iTotalRecords=total
    )
    return filtered_data_flat_response.json()


@data_controller.route('/by_measurement', methods=['GET'])
def get_filtered_data_by_measurement():
    data_service = get_data_service()
    args = request.args
    filtered_data_request = FilteredDataRequest.parse_obj(json.loads(args.get('table_data')))
    limit = args.get('length')
    offset = args.get('start')
    sort_column_idx = args.get('order[0][column]')
    sort_direction = args.get('order[0][dir]')
    sort_order = _get_sort_order(sort_column_idx, sort_direction)
    result, total = data_service.get_filtered_data_by_measurement(
        filtered_data_request.measurements,
        filtered_data_request.entities,
        limit,
        offset,
        sort_order
    )

    filtered_data_by_measurement_response = {
        'data': result,
        'iTotalDisplayRecords': total,
        'iTotalRecords': total
    }
    return jsonify(filtered_data_by_measurement_response)


def _get_sort_order(sort_column_idx, sort_direction) -> SortOrder:
    column = request.args.get('columns[{}][data]'.format(sort_column_idx))
    sort_order = SortOrder(
        items=[
            SortItem(column=column, direction=SortDirection(sort_direction))
        ]
    )
    return sort_order
