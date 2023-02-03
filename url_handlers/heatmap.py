from flask import Blueprint, render_template

heatmap_plot_page = Blueprint('heatmap', __name__, template_folder='templates')


@heatmap_plot_page.route('/heatmap', methods=['GET'])
def get_plots():
    return render_template('heatmap.html')
