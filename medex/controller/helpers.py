import os
from flask import session


def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = os.urandom(10)
    return session['session_id']
