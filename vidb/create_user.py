import os
from datetime import datetime, date
from urllib import parse
from passlib.hash import argon2
from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault.key_vault_client import KeyVaultClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *


dbhost = os.environ.get('DBHOST') or '192.168.0.134'
database = os.environ.get('DATABASE') or 'vibackend'
dbuser = os.environ.get('DBUSER') or 'vi@viback'
dbpwd = os.environ.get('DBPWD')

if not dbpwd:
    # Create MSI Authentication
    credentials = MSIAuthentication(resource='https://vault.azure.net')
    key_vault_client = KeyVaultClient(credentials)
    key_vault_uri = 'https://viinc.vault.azure.net'
    secret = key_vault_client.get_secret(key_vault_uri,  # Your KeyVault URL
                                         "BACKEND-DB-PWD",  # Name of your secret
                                         "")  # The version of the secret. Empty string for latest
    dbpwd = secret.value
dbpwd = parse.quote_plus(dbpwd)
SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://{user}:{password}@{host}/{db}?charset=utf8'.format(user=dbuser,
                                                                                              password=dbpwd,
                                                                                              host=dbhost,
                                                                                              db=database)
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True, connect_args={'tds_version': '7.0'})
Session = sessionmaker(bind=engine)
session = Session()

print("connecting to %s:%s:%s" % (dbhost, database, dbuser))

# ERASE THIS AFTER USING!!!
email = 'webmaster@vitalityindex.com'
password = 'v1t@l1ty'
first_name = 'web'
gender = 'Other'
postal_code = '81631'
birth_date = date(year=1963, month=1, day=8)
role = 'vivendor'

hash = argon2.hash(password)
user = User(email=email,
            pword=hash,
            first_name=first_name,
            gender=gender,
            postal_code=postal_code,
            birth_date=birth_date,
            role=role)
session.add(user)
session.commit()

print("just created user %s" % user.email)
