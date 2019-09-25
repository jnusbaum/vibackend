import os
from datetime import datetime
from urllib import parse
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
                                         "MSSQL-DB-PWD",  # Name of your secret
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

"""
Delete tokens that have expired from the database.

How (and if) you call this is entirely up you. You could expose it to an
endpoint that only administrators could call, you could run it as a cron,
set it up with flask cli, etc.
"""
now = datetime.utcnow()
print("expiring token expired before %s" % (now, ))
expired = session.query(Token).filter(Token.expires < now)
for token in expired:
    print("deleting token %s:%s:%s" % (token.user.email, token.token_type, token.expires))
    session.delete(token)
session.commit()

