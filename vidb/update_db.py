import os
from .models import *

dbhost = os.getenv('DBHOST')
database = os.getenv('DATABASE')
dbuser = os.getenv('DBUSER')
dbsslmode = os.getenv('DBSSLMODE')
dbpwd = os.getenv('DBPWD')

db.bind(provider='postgres', host=dbhost,
        database=database,
        user=dbuser,
        password=dbpwd,
        sslmode=dbsslmode)

db.generate_mapping(check_tables=True)
