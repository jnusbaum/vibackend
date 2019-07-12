#! /usr/bin/env python
from models import *
import datetime
import os

from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault.key_vault_client import KeyVaultClient

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


# # importing the requests library
# import requests
#
# # Step 1: Fetch an access token from an MSI-enabled Azure resource
# # Note that the resource here is https://vault.azure.net for the public cloud, and api-version is 2018-02-01
# MSI_ENDPOINT = "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fvault.azure.net"
# r = requests.get(MSI_ENDPOINT, headers = {"Metadata" : "true"})
#
# # Extracting data in JSON format
# # This request gets an access token from Azure Active Directory by using the local MSI endpoint
# data = r.json()
#
# # Step 2: Pass the access token received from the previous HTTP GET call to the key vault
# KeyVaultURL = "https://viinc.vault.azure.net/secrets/BACKEND-DB-PWD?api-version=2016-10-01"
# kvSecret = requests.get(url = KeyVaultURL, headers = {"Authorization": "Bearer " + data["access_token"]})
#
# dbpwd = kvSecret.json()["value"]

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
now = datetime.datetime.now()
print("expiring token expired before %s" % (now, ))
with db_session:
    expired = Token.select(lambda t: t.expires < now)
    for token in expired:
        print("deleting token %s:%s:%s" % (token.user.email, token.token_type, token.expires))
        token.delete()

