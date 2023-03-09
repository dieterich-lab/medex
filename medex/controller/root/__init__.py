import os

from flask import Blueprint, render_template, send_from_directory, redirect

root_controller = Blueprint('root_controller', __name__)


@root_controller.route('/favicon.ico', methods=['GET'])
def favicon():
    folder = os.path.join(root_controller.root_path, 'resources')
    return send_from_directory(folder, 'favicon.ico', mimetype='vnd.microsoft.icon')


@root_controller.route('/', methods=['GET'])
def login_get():
    return redirect('/filtered_data')


@root_controller.route('/logout/', methods=['GET'])
def logout():
    return render_template('logout.html')
