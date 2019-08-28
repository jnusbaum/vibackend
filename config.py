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
    # configure from environment variables
    # these will come in secure form from azure app settings in azure deployment
    # database/pony
    DBHOST = os.environ.get('DBHOST') or 'localhost'
    DATABASE = os.environ.get('DATABASE') or 'vi'
    DBUSER = os.environ.get('DBUSER') or 'vi'
    DBPWD = os.environ.get('DBPWD')
    DBSSLMODE = os.environ.get('DBSSLMODE') or 'require'
    # itsdangerous, jwt
    JWT_SECRET_KEY = os.environ.get('JWTKEY')
    IDANGEROUSKEY = os.environ.get('ITSDANGEROUSKEY')

    INDEX = os.environ.get('INDEX') or "Vitality Index"