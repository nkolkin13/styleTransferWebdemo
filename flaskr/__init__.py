import os
from flask import Flask
from celery import Celery
import datetime

UPLOAD_FOLDER = './uploaded_ims/'
CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
SECRET_KEY = b'ImSoRandom'
celery = Celery(__name__, broker=CELERY_BROKER_URL,include=['flaskr.blog'])


def create_app(test_config=None):
    #Create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=SECRET_KEY, DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'))
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    if test_config is None:
        # load instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the passed test config file
        app.config.from_mapping(test_config)

    #Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    celery.conf.update(app.config)

    # a test page that says hello and the date/time
    @app.route('/test')
    def hello():
        now = datetime.datetime.now()
        return 'Hello World! the date/time is '+ now.strftime("%Y-%m-%d %H:%M:%S")

    from . import db
    db.init_app(app)

    #from . import auth
    #app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='land')


    return app

