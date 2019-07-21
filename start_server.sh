#!/usr/bin/env bash
DBHOST="vibackend.postgres.database.azure.com"; export DBHOST
DATABASE="vi-test"; export DATABASE
DBUSER="vi@vibackend"; export DBUSER
DBSSLMODE="require"; export DBSSLMODE
MAILSVR="smtp.gmail.com"; export MAILSVR
MAILUSER="vicalc@getyourvi.com"; export MAILUSER
REDISBROKER='redis+socket://var/run/redis/redis-server.sock'; export REDISBROKER
VIMSPATH="/home/viadm/VIINC/vimailserver"; export VIMSPATH
$VIMSPATH/venv/bin/celery -A mail_server.celery worker --loglevel=debug >> $VIMSPATH/log/mail_server.log 2>&1 &
