#!/bin/bash
DBHOST="viback.database.windows.net"; export DBHOST
DATABASE="vibackend"; export DATABASE
DBUSER="vi@viback"; export DBUSER
VIDBPATH="/home/viadm/VIINC/vidb-alchemy"; export VIDBPATH
$VIDBPATH/venv/bin/python $VIDBPATH/prune_token_db.py >> $VIDBPATH/log/prune_token.cron.log 2>&1
