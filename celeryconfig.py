import os
import logging
from celery import Celery

broker = os.getenv('REDISBROKER')
mailsvr = os.getenv('MAILSVR')
mailuser = os.getenv('MAILUSER')
mailpwd = os.getenv('MAILPWD')

logging.info("connecting to redis broker at %s", broker)
celery = Celery('mail_server', broker=broker)
