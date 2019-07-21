import os
import logging

from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault.key_vault_client import KeyVaultClient

from vidb.models import *
from mail_tasks import *

dbhost = os.getenv('DBHOST')
database = os.getenv('DATABASE')
dbuser = os.getenv('DBUSER')
dbsslmode = os.getenv('DBSSLMODE')

# Create MSI Authentication
credentials = MSIAuthentication(resource='https://vault.azure.net')
key_vault_client = KeyVaultClient(credentials)
key_vault_uri = 'https://viinc.vault.azure.net'
secret = key_vault_client.get_secret(key_vault_uri, "BACKEND-DB-PWD", "")
dbpwd = secret.value

print("connecting to %s:%s:%s" % (dbhost, database, dbuser))
# configure from environment variables
# these will come in secure form from azure app settings in azure deployment
# database/pony
db.bind(provider='postgres', host=dbhost,
        database=database,
        user=dbuser,
        password=dbpwd,
        sslmode=dbsslmode)
db.generate_mapping()

