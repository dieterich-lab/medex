from os.path import join
from flask import Blueprint, send_from_directory
from medex.services.config import get_config

root_controller = Blueprint('root_controller', __name__, template_folder='templates')


@root_controller.route('/favicon.ico', methods=['GET'])
def favicon():
    folder = join(root_controller.root_path, 'resources')
    return send_from_directory(folder, 'favicon.ico', mimetype='vnd.microsoft.icon')


@root_controller.route('/', methods=['GET'])
def index():
    frontend_path = get_config().frontend_path
    return send_from_directory(frontend_path, 'index.html', mimetype='text/html')

@root_controller.route('/assets/<path:path>', methods=['GET'])
def assers(path):
    assets_path = join(get_config().frontend_path, 'assets')
    return send_from_directory(assets_path, path)
