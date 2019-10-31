import functools
from flask import(Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
# flaskr will have 2 blueprints, one for authentication functions and one for blog posts functions.

bp = Blueprint('auth', __name__, url_prefix='/auth')

# the above uses the class flask.Blueprint object named auth, passed in the __name__ argument to tell the blueprint where it's defined, and will prepend /auth to all URLs associated with the blueprint

@bp.route('/register', methods=('GET', 'POST'))
def register():
# if user submits the form, the method will be POST
# request.form[] is a dictionary mapping submitting keys and values
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        # fechone() returns a row form query to check whether a username is already registered
        elif db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
            error = 'User {} is already registered'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)', (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        # hashes the submitted password in the same way as stored hash and compares them
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        # session is a dictionary that stores data across requests. User id stored in a new session when validation succeeds
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    return render_template('/auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# url_for() function generates the URL to a view based on a name and arguments - the name associated with a view is also called the endpoint, by default it's the same as the name of the view function.