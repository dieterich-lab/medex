from flask import Blueprint, render_template
histogram_page = Blueprint('histogram', __name__, template_folder='templates')


@histogram_page.route('/histogram', methods=['GET'])
def get_statistics():
    number_of_bins = 20
    return render_template('histogram.html',
                           number_of_bins=number_of_bins)