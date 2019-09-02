import logging
import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # set up logger
    logfile = app.config['LOGDIR'] + app.config['LOGNAME']
    # check for existence and rotate
    if os.path.isfile(logfile):
        # rename with time
        bname = app.config['LOGNAME'].split('.')[0]
        nname = "%s.%s.log" % (bname, datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"))
        os.rename(logfile, os.path.join(app.config['LOGDIR'], nname))
    else:
        # create log directory if it does not exist
        os.makedirs(app.config['LOGDIR'], 0o777, True)
    # set up basic logging
    logging.basicConfig(filename=logfile, level=app.config['LOGLEVEL'],
                        format='%(asctime)s - %(levelname)s - %(message)s')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
