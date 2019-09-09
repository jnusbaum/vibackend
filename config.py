import os

class Config(object):
    SECRET_KEY = os.environ.get('FLASKKEY') or 'you-will-never-guess'
    LOGLEVEL = os.environ.get('LOGLEVEL') or 'INFO'
    LOGFILE = os.environ.get('LOGFILE') or "viservice.log"
    LOGDIR = os.environ.get('LOGDIR') or "./log/"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    DBHOST = os.environ.get('DBHOST') or '192.168.0.134'
    DATABASE = os.environ.get('DATABASE') or 'viback'
    DBUSER = os.environ.get('DBUSER') or 'vi'
    DBPWD = os.environ.get('DBPWD') or 'v1t@l1ty'
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://{user}:{password}@{host}/{db}?charset=utf8'.format(user=DBUSER,
                                                                                                  password=DBPWD,
                                                                                                  host=DBHOST,
                                                                                                  db=DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'echo': True}
    # itsdangerous, jwt
    JWT_SECRET_KEY = os.environ.get('JWTKEY') or 'you-will-never-guess'
    IDANGEROUSKEY = os.environ.get('ITSDANGEROUSKEY') or 'you-will-never-guess'

    INDEX = os.environ.get('INDEX') or "Vitality Index"
    WWWHOST = 'localhost'
    WWWPORT = 5000