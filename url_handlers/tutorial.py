from flask import Blueprint, render_template
from webserver import all_subcategory_entities

tutorial_page = Blueprint('tutorial', __name__, template_folder='tepmlates')

@tutorial_page.route('/tutorial', methods=['GET', 'POST'])
def logout():
    return render_template('tutorial.html',
                           all_subcategory_entities=all_subcategory_entities,)