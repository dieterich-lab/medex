from flask import Blueprint, render_template

barchart_page = Blueprint('barchart', __name__, template_folder='templates')


@barchart_page.route('/barchart', methods=['GET'])
def get_statistics():
    return render_template('barchart.html')
