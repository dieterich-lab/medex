from flask import Blueprint, render_template

tutorial_page = Blueprint('tutorial', __name__, template_folder='tepmlates')

@tutorial_page.route('/tutorial', methods=['GET', 'POST'])
def logout():
    return render_template('tutorial.html')