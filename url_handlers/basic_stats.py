from flask import Blueprint, render_template
from webserver import measurement_name

basic_stats_page = Blueprint('basic_stats', __name__, template_folder='basic_stats')


@basic_stats_page.route('/basic_stats', methods=['GET'])
def get_statistics():
    return render_template('basic_stats/basic_stats.html',
                           numeric_tab=True,
                           name=measurement_name,
                           measurement_name=measurement_name)
