import os
import logging
from celery import Celery

broker = os.environ.get('REDISBROKER') or 'redis://13.88.10.107'
mailsvr = os.environ.get('MAILSVR') or 'smtp.gmail.com'
mailuser = os.environ.get('MAILUSER') or 'vicalc@getyourvi.com'
mailpwd = os.environ.get('MAILPWD') or 'v1t@l1ty'

logging.info("connecting to redis broker at %s", broker)
celery = Celery('mail_server', broker=broker)
