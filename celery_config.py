import os
from celery import Celery

broker = os.getenv('REDISBROKER')
mailsvr = os.getenv('MAILSVR')
mailuser = os.getenv('MAILUSER')
mailpwd = os.getenv('MAILPWD')

celery = Celery('mail_server', broker=broker)




