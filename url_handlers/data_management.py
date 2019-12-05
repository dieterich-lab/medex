import collections
import time
import datetime

from flask import Blueprint, render_template, request
import csv
import misc.utils as utils

from data_warehouse.redis_rwh import get_connection

data_management_page = Blueprint('data_management_page', __name__,
                                 template_folder='flaskr/templates')


# entities = {
#             'diagnostik.hauptdiagnose.tumortyp': 'String',
#             'diagnostik.labor.bare_nuclei': 'String',
#             'diagnostik.labor.bland_chromatin': 'String',
#             'diagnostik.labor.clump_thickness': 'String',
#             'diagnostik.labor.marginal_adhesion': 'String',
#             'diagnostik.labor.mitosis': 'String',
#             'diagnostik.labor.normal_nucleoli': 'String',
#             'diagnostik.labor.single_epithelial_cell_size': 'Integer',
#             'diagnostik.labor.uniformity_of_cell_shape': 'String',
#             'diagnostik.labor.uniformity_of_cell_size': 'String',
#             }

@data_management_page.route('/data_management', methods=['POST'])
def manage_data():
    # example of 1 line in csv file:
    # fe189ec785f674f8d19f3af063c68413, 7dd8eb5937291aedc698e65581be76ca, 2018-05-22, 10:05:00, diagnostik.labor.uniformity_of_cell_size, 10
    csv_file = request.files['csv_file']
    csv_lines = csv_file.stream.read().decode("utf-8").split('\n')
    csv_data = list(csv.reader(csv_lines, delimiter=','))

    # example of entities file (also in csv format):
    # diagnostik.hauptdiagnose.tumortyp, String
    # diagnostik.labor.single_epithelial_cell_size, Integer
    entities_file = request.files['entities_file']
    entities_lines = entities_file.stream.read().decode("utf-8").split('\n')
    entities = dict(csv.DictReader(entities_lines, delimiter=','))

    # I don't like to hardcode it, we should create a config file
    redis_connection = get_connection('localhost', '6379')
    pong = redis_connection.ping()

    update_message = pong
    number_keys = set()
    category_keys = set()
    date_keys = set()
    category_values = collections.defaultdict(set)

    redis_commands = []

    for line in csv_data:
        (patient_id, quarter_id, date_stamp, time_stamp, key, value) = line
        float_value = utils.try_parse_float(value)
        entity_type = entities.get(key)

        if float_value is not None:
            redis_connection.zadd(key, float_value, patient_id)
            redis_commands.append("ZADD {} {} {}".format(key, float_value, patient_id))
            number_keys.add(key)

        elif entity_type == 'String':
            kv = "{}.{}".format(key, value)
            redis_connection.sadd(kv, patient_id)
            redis_commands.append("SADD {} {}".format(kv, patient_id))

            category_keys.add(key)
            category_values[key].add(value)

        elif entity_type == 'null':
            value = time.mktime(datetime.datetime.strptime(date_stamp, "%Y-%m-%d").timetuple())

            value = max(value, 0)
            redis_connection.zadd(key, value, patient_id)
            redis_commands.append("ZADD {} {} {}".format(key, value, patient_id))

            date_keys.add(key)

    for number_key in number_keys:
        redis_connection.sadd("number_keys", number_key)

    for date_key in date_keys:
        redis_connection.sadd("date_keys", date_key)

    for category_key in category_keys:
        redis_connection.sadd("category_keys", category_key)

    for category, cv in category_values.items():
        category_key = "{}_values".format(category)
        for category_value in cv:
            redis_connection.sadd(category_key, category_value)

    # if we got to this point, we did not get any exceptions
    update_message = 'Successfully updated'
    return render_template('data_management.html', update_message=update_message)


@data_management_page.route('/data_management', methods=['GET'])
def get_manage_data():
    return render_template('data_management.html')
