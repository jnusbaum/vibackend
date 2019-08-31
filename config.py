import os

class Config(object):
    SECRET_KEY = os.environ.get('FLASKKEY') or 'you-will-never-guess'
    LOGLEVEL = os.environ.get('LOGLEVEL') or 'INFO'
    LOGNAME = os.environ.get('LOGNAME') or "viservice.log"
    LOGDIR = os.environ.get('LOGDIR') or "./log/"
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    WWWHOST = 'localhost'
    WWWPORT = 5000
    DBHOST = os.environ.get('DBHOST') or '192.168.0.134'
    DATABASE = os.environ.get('DATABASE') or 'vibackend'
    DBUSER = os.environ.get('DBUSER') or 'vi'
    DBPWD = os.environ.get('DBPWD')
    SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://{user}:{password}@{host}/{db}?charset=utf8'.format(user=DBUSER,
                                                                                                  password=DBPWD,
                                                                                                  host=DBHOST,
                                                                                                  db=DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # itsdangerous, jwt
    JWT_SECRET_KEY = os.environ.get('JWTKEY')
    IDANGEROUSKEY = os.environ.get('ITSDANGEROUSKEY')

    INDEX = os.environ.get('INDEX') or "Vitality Index"