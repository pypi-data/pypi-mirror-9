from __future__ import absolute_import

from celery import Celery
from nibada.config import celery_cfg

app = Celery('nibada',
                include=['nibada.tasks'])
app.config_from_object(celery_cfg)

if __name__ == '__main__':
    app.start()
