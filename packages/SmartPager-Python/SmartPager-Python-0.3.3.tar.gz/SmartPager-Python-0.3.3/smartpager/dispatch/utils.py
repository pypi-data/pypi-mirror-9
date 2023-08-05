
from celery import Celery

from smartpager.rest import RestException


class CelerySingleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):

        if not cls._instance:
            broker = None

            if 'broker' in kwargs:
                broker = kwargs.get('broker', None)

            if not broker:
                raise RestException('A broker is required to start celery.')

            cls._instance = Celery(broker=broker)

        return cls._instance


class CeleryVariables:
    SEND_MSG_TASK = 'messaging.tasks.send_message'
    SEND_MSG_FORMAT = 'json'