import os
# Broker settings.
broker_url = os.getenv('REDISBROKER')
# List of modules to import when the Celery worker starts.
imports = ('mail_tasks',)




