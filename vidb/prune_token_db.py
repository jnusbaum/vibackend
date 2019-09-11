import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Index, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from msrestazure.azure_active_directory import MSIAuthentication
from azure.keyvault.key_vault_client import KeyVaultClient

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), nullable=False, unique=True)
    pword = Column(String(256), nullable=False)
    first_name = Column(String(256), nullable=False)
    birth_date = Column(Date, nullable=False, index=True)
    gender = Column(String(8), nullable=False, default='Other', index=True)
    postal_code = Column(String(256), nullable=False, )
    role = Column(String(32), nullable=False, default='viuser')  # one of vivendor, viuser
    last_login = Column(DateTime, index=True)
    last_notification = Column(DateTime, index=True)
    # foreign keys
    # relationships
    results = relationship('Result', cascade="all, delete-orphan", back_populates='user', order_by="Result.time_generated.desc()")
    answers = relationship('Answer', cascade="all, delete-orphan", back_populates='user', order_by="Answer.time_received.desc(), Answer.question_name")
    tokens = relationship('Token', cascade="all, delete-orphan", back_populates='user')

# indexes
Index('user_idx_email_pword', User.email, User.pword)


class Token(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(256), nullable=False, index=True)
    token_type = Column(String(10), nullable=False)
    revoked = Column(Boolean, nullable=False)
    expires = Column(DateTime, nullable=False)
    # foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    # relationships
    user = relationship('User', back_populates='tokens')


dbhost = os.environ.get('DBHOST') or '192.168.0.134'
database = os.environ.get('DATABASE') or 'vibackend'
dbuser = os.environ.get('DBUSER') or 'vi@viback'

# Create MSI Authentication
credentials = MSIAuthentication(resource='https://vault.azure.net')
key_vault_client = KeyVaultClient(credentials)
key_vault_uri = 'https://viinc.vault.azure.net'
secret = key_vault_client.get_secret(key_vault_uri,  # Your KeyVault URL
                                     "BACKEND-DB-PWD",  # Name of your secret
                                     "")  # The version of the secret. Empty string for latest
dbpwd = secret.value
SQLALCHEMY_DATABASE_URI = 'mssql+pymssql://{user}:{password}@{host}/{db}?charset=utf8'.format(user=dbuser,
                                                                                                  password=dbpwd,
                                                                                                  host=dbhost,
                                                                                                  db=database)
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
from sqlalchemy.orm import sessionmaker
session = sessionmaker(bind=engine)

print("connecting to %s:%s:%s" % (dbhost, database, dbuser))

"""
Delete tokens that have expired from the database.

How (and if) you call this is entirely up you. You could expose it to an
endpoint that only administrators could call, you could run it as a cron,
set it up with flask cli, etc.
"""
from datetime import datetime

now = datetime.utcnow()
print("expiring token expired before %s" % (now, ))
expired = session.query(Token).filter(Token.expires < now)
for token in expired:
    print("deleting token %s:%s:%s" % (token.user.email, token.token_type, token.expires))
    session.delete(token)
session.commit()

