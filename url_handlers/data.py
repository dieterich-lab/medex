from flask import Blueprint, render_template

data_page = Blueprint('data', __name__, template_folder='templates')


@data_page.route('/data', methods=['GET'])
def get_data():
    return render_template('data.html')
