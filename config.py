import os
from urllib import parse

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
    DBPWD = os.environ.get('DBPWD') or 'zaxxon'
    DBDRIVER = '{ODBC Driver 17 for SQL Server}'
    cstring = 'Driver={driver};Server=tcp:{dbhost},1433;Database={database};Uid={dbuser};Pwd={dbpwd};Connection Timeout=30;'
    cstring = cstring.format(driver=DBDRIVER, dbhost=DBHOST, database=DATABASE, dbuser=DBUSER, dbpwd=DBPWD)
    cstring = parse.quote_plus(cstring)
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % cstring
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # itsdangerous, jwt
    JWT_SECRET_KEY = os.environ.get('JWTKEY') or 'you-will-never-guess'
    IDANGEROUSKEY = os.environ.get('ITSDANGEROUSKEY') or 'you-will-never-guess'

    INDEX = os.environ.get('INDEX') or "Vitality Index"
    WWWHOST = '0.0.0.0'
    WWWPORT = 5000