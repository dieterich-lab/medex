import os

from flask import Blueprint, render_template, send_from_directory

root_controller = Blueprint('root_controller', __name__, template_folder='templates')


@root_controller.route('/favicon.ico', methods=['GET'])
def favicon():
    folder = os.path.join(root_controller.root_path, 'resources')
    return send_from_directory(folder, 'favicon.ico', mimetype='vnd.microsoft.icon')


@root_controller.route('/', methods=['GET'])
def login_get():
    return render_template('index.html.j2')
