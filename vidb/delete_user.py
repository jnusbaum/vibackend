import os
from vidb.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

dbhost = os.getenv('DBHOST')
database = os.getenv('DATABASE')
dbuser = os.getenv('DBUSER')
dbsslmode = os.getenv('DBSSLMODE')
dbpwd = os.getenv('DBPWD')

url = 'mssql+pymssql://vi:v1t@l1ty@192.168.0.134/vibackend?charset=utf8'
engine = create_engine(url, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

u = session.query(User).filter(User.email == 'contact@vitalityindex.com').one_or_none()
session.delete(u)
session.commit()

