import sqlite3
# g is a special object that is unique for each request - it's used to store data, the connection is stored and reused instead of creating a new connection if get_db is called 2x in the same request
# current_app = special object that points to the Flask app handling the request. get_db is called when the application is created and handles the request, so current_app can be used
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        # sqlite3.connect() establishes a connection to the file pointed at by the DATABASE configuration key, the file only has to exist when the DB HAS BEEN INITIALIZED.
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3,Row tells the connection to return rows that behave like dictionaries, which allows accessing by column names
        g.db.row_factory = sqlite3.Row

    return g.db

# checks if a connection was created by checking if g.db was set. if the connection exists, it's closed
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    # get_db returns a database connection which is used to execute the read command below
    db = get_db()

    # open_resource() opens a file relative to the flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

# @click.command defines a comand-line command called init-db that calls the init_db function
# more info in the Command Line Interface flask docs
@click.command('init-db')
@with_appcontext
def init_db_command():
    # clear existing data and create new tables
    init_db()
    click.echo('Initialized the database.')