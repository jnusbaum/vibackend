import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from vidb.models import *

dbhost = os.getenv('DBHOST')
database = os.getenv('DATABASE')
dbuser = os.getenv('DBUSER')
dbsslmode = os.getenv('DBSSLMODE')
dbpwd = os.getenv('DBPWD')

url = 'mssql+pymssql://{user}:{password}@{host}/{db}?charset=utf8'.format(user=dbuser,
                                                                          password=dbpwd,
                                                                          host=dbhost,
                                                                          db=database)
engine = create_engine(url, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

db.drop_all()
db.commit()
