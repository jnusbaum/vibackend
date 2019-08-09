import os
from models import *

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

db.generate_mapping()

with db_session:
    u = User.get(email='brandong@thoughtlab.com')
    u.delete()

    u = User.get(email='jnusbaum@cybermesa.com')
    u.delete()

    u = User.get(email='joec@thoughtlab.com')
    u.delete()

    u = User.get(email='aliz@thoughtlab.com')
    u.delete()
