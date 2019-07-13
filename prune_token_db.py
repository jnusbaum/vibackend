from datetime import datetime
import os

from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault.key_vault_client import KeyVaultClient

from models import *

dbhost = os.getenv('DBHOST')
database = os.getenv('DATABASE')
dbuser = os.getenv('DBUSER')
dbsslmode = os.getenv('DBSSLMODE')

# Create MSI Authentication
credentials = MSIAuthentication(resource='https://vault.azure.net')
key_vault_client = KeyVaultClient(credentials)
key_vault_uri = 'https://viinc.vault.azure.net'
secret = key_vault_client.get_secret(key_vault_uri,  # Your KeyVault URL
                                     "BACKEND-DB-PWD",  # Name of your secret
                                     "")  # The version of the secret. Empty string for latest
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


"""
Delete tokens that have expired from the database.

How (and if) you call this is entirely up you. You could expose it to an
endpoint that only administrators could call, you could run it as a cron,
set it up with flask cli, etc.
"""
now = datetime.utcnow()
print("expiring token expired before %s" % (now, ))
with db_session:
    expired = Token.select(lambda t: t.expires < now)
    for token in expired:
        print("deleting token %s:%s:%s" % (token.user.email, token.token_type, token.expires))
        token.delete()

