import csv
import json
import io

from flask import Blueprint, request, jsonify, send_file

from medex.controller.helpers import get_data_service
from medex.dto.data import FilteredDataRequest, SortOrder, SortDirection, SortItem, FilteredDataFlatResponse

data_controller = Blueprint('data_controller', __name__)


@data_controller.route('/flat', methods=['GET'])
def get_filtered_data_flat():
    data_service = get_data_service()
    args = request.args
    filtered_data_request = FilteredDataRequest.parse_obj(json.loads(args.get('table_data')))
    sort_order = _get_sort_order(args)
    result, total = data_service.get_filtered_data_flat(
        measurements=filtered_data_request.measurements,
        entities=filtered_data_request.entities,
        limit=args.get('length'),
        offset=args.get('start'),
        sort_order=sort_order
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
    sort_order = _get_sort_order(args)
    result, total = data_service.get_filtered_data_by_measurement(
        measurements=filtered_data_request.measurements,
        entities=filtered_data_request.entities,
        limit=args.get('length'),
        offset=args.get('start'),
        sort_order=sort_order
    )

    filtered_data_by_measurement_response = {
        'data': result,
        'iTotalDisplayRecords': total,
        'iTotalRecords': total
    }
    return jsonify(filtered_data_by_measurement_response)


def _get_sort_order(args) -> SortOrder:
    sort_column_idx = args.get('order[0][column]')
    sort_direction = args.get('order[0][dir]')
    column = request.args.get('columns[{}][data]'.format(sort_column_idx))
    sort_order = SortOrder(
        items=[
            SortItem(column=column, direction=SortDirection(sort_direction))
        ]
    )
    return sort_order


@data_controller.route('/flat_csv', methods=['GET'])
def get_filtered_data_flat_csv():
    data_service = get_data_service()
    args = request.args
    filtered_data_request = FilteredDataRequest.parse_obj(json.loads(args.get('data')))
    result, total = data_service.get_filtered_data_flat(
        filtered_data_request.measurements,
        filtered_data_request.entities,
    )
    buf_byt = _get_dict_to_csv(result)
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name='filtered_data_flat.csv')


@data_controller.route('/by_measurement_csv', methods=['GET'])
def get_filtered_data_by_measurement_csv():
    data_service = get_data_service()
    args = request.args
    filtered_data_request = FilteredDataRequest.parse_obj(json.loads(args.get('data')))
    result, total = data_service.get_filtered_data_by_measurement(
        filtered_data_request.measurements,
        filtered_data_request.entities,
    )
    buf_byt = _get_dict_to_csv(result)
    return send_file(buf_byt,
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name='filtered_data_by_measurement_.csv')


def _get_dict_to_csv(result):
    field_names = [key for key in result[0].keys()]
    with io.StringIO() as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(result)
        data = csvfile.getvalue()
    buf_byt = io.BytesIO(data.encode("utf-8"))
    return buf_byt
