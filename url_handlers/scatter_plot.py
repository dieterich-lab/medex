from flask import Blueprint, render_template
scatter_plot_page = Blueprint('scatter_plot', __name__, template_folder='templates')


@scatter_plot_page.route('/scatter_plot', methods=['GET'])
def get_plots():
    return render_template('scatter_plot.html')
