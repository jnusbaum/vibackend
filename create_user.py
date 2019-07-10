import os
from models import *
import datetime
from passlib.hash import argon2

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

# ERASE THIS AFTER USING!!!
email = 'webmaster@vitalityindex.com'
password = 'v1t@l1ty'

hash = argon2.hash(password)
with db_session:
    user = User(email=email, pword=hash, first_name='web', gender='Other', postal_code='81631',
                birth_date=datetime.date(year=1963, month=1, day=8), role='vivendor')
print("just created user %s" % user.email)
