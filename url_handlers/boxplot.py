from flask import Blueprint, render_template

boxplot_page = Blueprint('boxplot', __name__, template_folder='templates')


@boxplot_page.route('/boxplot', methods=['GET'])
def get_boxplots():
    return render_template('boxplot.html')
