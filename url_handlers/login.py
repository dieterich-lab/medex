from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, UserMixin, logout_user

from passlib.hash import sha256_crypt


login_page = Blueprint('login_page', __name__)


# creating a custom User class
class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    @classmethod
    def get_user(self, email, password):
        from webserver import get_db
        rdb = get_db()
        encrypted_password = rdb.hget('users', email) or ''
        if sha256_crypt.verify(password, encrypted_password):
            # todo: how to store ids??
            # for now we use email as an id
            return User(email, email, password)
        return None

    @classmethod
    def get_by_id(self, id):
        # todo: implement user by id
        # for now get user by email and use email as an id
        from webserver import get_db
        rdb = get_db()
        password = rdb.hget('users', id) or ''
        if password:
            return User(id, id, password)
        return None


@login_page.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_user(email, password)
        if user is not None:
            login_user(user)
            return redirect('/basic_stats')
        else:
            error = "Incorrect username or password"
    return render_template('login_page.html',
                           error=error)


@login_page.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/login')
