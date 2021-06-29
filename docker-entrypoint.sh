#!/bin/sh

set -ex # fail on any error & print commands as they're run
if [ "x$MANAGEPY_MIGRATE" = "xon" ]; then
    python manage.py migrate --noinput
fi
if [ "x$MANAGEPY_COLLECTSTATIC" = "xon" ]; then
    python manage.py collectstatic --noinput
fi
if [ "$MANAGEPY_COMPRESS" = "xon" ]; then
    python manage.py compress --extension haml,html --force
fi
if [ "$MANAGEPY_ADD_COUNTRY_ALIAS" = "xon" ]; then
    python manage.py add_country_alias
fi

TYPE=${1:-ureport}
if [ "$TYPE" = "ureport" ]; then
    uwsgi --ini /ureport/uwsgi.ini
elif [ "$TYPE" = "celery" ]; then
    celery multi start ureport.celery ureport.sync ureport.slow \
        -A ureport.celery:app \
        --loglevel=INFO \
        --logfile=/tmp/celery_log/%n%I.log \
        --pidfile=/tmp/celery/%n.pid \
        -E --autoscale=4,1 -O fair \
        -Q:ureport.celery celery -Q:ureport.sync sync -Q:ureport.slow slow
elif [ "$TYPE" = "celery-beat" ]; then
    celery beat -A ureport.celery:app \
        --workdir=/ureport \
        --pidfile=/tmp/celerybeat.pid \
        --logfile=/tmp/celerybeat.log \
        --loglevel=INFO \
        --schedule=/tmp/celerybeat-schedule
fi
