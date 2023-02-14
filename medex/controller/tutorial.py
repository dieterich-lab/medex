from flask import Blueprint, render_template

tutorial_controller = Blueprint('tutorial_controller', __name__)


@tutorial_controller.route('/', methods=['GET'])
def tutorial():
    return render_template('tutorial.html')
