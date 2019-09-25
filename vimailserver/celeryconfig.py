import os
from urllib import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault.key_vault_client import KeyVaultClient
from celery import Celery

dbhost = os.environ.get('DBHOST') or '192.168.0.134'
database = os.environ.get('DATABASE') or 'vibackend'
dbuser = os.environ.get('DBUSER') or 'vi@viback'
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

broker = os.getenv('REDISBROKER')

mailsvr = os.getenv('MAILSVR')
mailuser = os.getenv('MAILUSER')
# get mail password from key vault
secret = key_vault_client.get_secret(key_vault_uri, "MAILPWD", "")
mailpwd = secret.value

celery = Celery('mail_server', broker=broker)




