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
database = os.environ.get('DATABASE') or 'vibackend-test'
dbuser = os.environ.get('DBUSER') or 'vi@viback'
dbpwd = os.environ.get('DBPWD') or 'foobar'
dbdriver = '{ODBC Driver 17 for SQL Server}'

SQLALCHEMY_TRACK_MODIFICATIONS = False

if not dbpwd:
    # Create MSI Authentication
    credentials = MSIAuthentication(resource='https://vault.azure.net')
    key_vault_client = KeyVaultClient(credentials)
    key_vault_uri = 'https://viinc.vault.azure.net'
    secret = key_vault_client.get_secret(key_vault_uri,  # Your KeyVault URL
                                         "BACKEND-DB-PWD",  # Name of your secret
                                         "")  # The version of the secret. Empty string for latest
    dbpwd = secret.value
cstring = 'Driver={driver};Server=tcp:{dbhost},1433;Database={database};Uid={dbuser};Pwd={dbpwd};Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;'
cstring = cstring.format(driver=dbdriver, dbhost=dbhost, database=database, dbuser=dbuser, dbpwd=dbpwd)
cstring = parse.quote_plus(cstring)
SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=%s" % cstring

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

print("connecting to %s:%s:%s" % (dbhost, database, dbuser))

# ERASE THIS AFTER USING!!!
email = 'raymond.nusbaum@gmail.com'

u = session.query(User).filter(User.email == email).one_or_none()
if u:
    session.delete(u)
    session.commit()

print("just deleted user %s" % email)