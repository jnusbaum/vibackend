import logging
import os
from datetime import datetime
from flask import Flask
from flask_migrate import Migrate
from config import Config
from flask_jwt_extended import JWTManager
from vidb.models import db

migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # set up logger
    # make file unique
    # we will be running multiple processes behind gunicorn
    # we do not want all the processes writing to the same log file as this can result in garbled data in the file
    # so we need a unique file name each time we run
    # we will add date and time down to seconds (which will probably be the same for all processes)
    # and add process id to get uniqueness
    fparts = app.config['LOGFILE'].split('.')
    bname = fparts[0]
    ename = fparts[1]
    nname = "%s.%s.%d.%s" % (bname, datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S"), os.getpid(), ename)
    logfile = app.config['LOGDIR'] + nname
    # create log directory if it does not exist
    os.makedirs(app.config['LOGDIR'], 0o777, True)
    # set up basic logging
    logging.basicConfig(filename=logfile, level=app.config['LOGLEVEL'],
                        format='%(asctime)s - %(levelname)s - %(message)s')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app
