from os.path import join, exists
from flask import Blueprint, send_from_directory
from medex.services.config import get_config

root_controller = Blueprint('root_controller', __name__, template_folder='templates')


@root_controller.route('/favicon.ico', methods=['GET'])
def favicon():
    return _handle_tunable_resources('favicon.ico', 'vnd.microsoft.icon')


def _handle_tunable_resources(name, mimetype):
    base_folder = join(root_controller.root_path, 'resources')
    custom_folder = join(base_folder, 'custom')
    if exists(join(custom_folder, name)):
        folder = custom_folder
    else:
        folder = base_folder
    return send_from_directory(folder, name, mimetype=mimetype)


@root_controller.route('/app_config.json', methods=['GET'])
def app_config():
    return _handle_tunable_resources('app_config.json', 'application/json')


@root_controller.route('/message_catalog.json', methods=['GET'])
def message_catalog():
    return _handle_tunable_resources('message_catalog.json', 'application/json')


@root_controller.route('/', methods=['GET'])
def index():
    frontend_path = get_config().frontend_path
    return send_from_directory(frontend_path, 'index.html', mimetype='text/html')


@root_controller.route('/assets/<path:path>', methods=['GET'])
def assets(path):
    assets_path = join(get_config().frontend_path, 'assets')
    return send_from_directory(assets_path, path)


@root_controller.route('/config/<path:path>', methods=['GET'])
def custom(path):
    custom_path = join(get_config().frontend_path, 'custom')
    return send_from_directory(custom_path, path)
