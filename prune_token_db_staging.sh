#!/bin/bash
DBHOST="vibackend.postgres.database.azure.com"; export DBHOST
DATABASE="vi-staging"; export DATABASE
DBUSER="vi@vibackend"; export DBUSER
DBSSLMODE="require"; export DBSSLMODE
VIADMPATH="/home/viadm/VIINC/vidb"; export VIADMPATH
$VIADMPATH/bin/python $VIADMPATH/prune_token_db.py >> $VIADMPATH/log/prune_token_staging.cron.log 2>&1
