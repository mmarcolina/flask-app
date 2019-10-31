import os
from flask import Flask

def create_app(test_config=None):
# create and configure the app create_app is an application factory function
# __name__ is the name of the current Python module. The app needs to know where it’s located to set up some paths, and __name__ is a convenient way to tell it that
# instance_relative_config=True tells the app that configuration files are relative to the instance folder
# DATABASE = path where SQLite database file will be saved
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr_sqlite'),
    )


    if test_config is None:
    # load the instance config (if it exists) when not testing
    # app.config.from_pyfile() overrides the default configuration with values taken from the config.py file if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
    # load the test config if passed in
        app.config.from_mapping(test_config)

# ensure the instance folder exists
    try:
        # os.makedirs() ensures app.instance_path exists, this is where the project will create the SQLite db file
        os.makedirs(app.instance_path)
    except OSError:
        pass

# say hello!
    @app.route('/hello')
    def hello():
        return 'Hello there!'

# initialize the db from the db.py file's init_app(app) function
    from . import db
    db.init_app(app)

# import and register the blueprint auth
# authentication blueprint will have views to register new users and log in/out
    from . import auth
    app.register_blueprint(auth.bp)

    return app