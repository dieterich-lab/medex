from flask import Blueprint, render_template

logout_controller = Blueprint('logout_controller', __name__)


@logout_controller.route('/', methods=['GET'])
def logout():
    return render_template('logout.html')
