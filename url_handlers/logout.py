from flask import Blueprint, render_template

logout_page = Blueprint('logout', __name__, template_folder='logout')


@logout_page.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('logout.html')
