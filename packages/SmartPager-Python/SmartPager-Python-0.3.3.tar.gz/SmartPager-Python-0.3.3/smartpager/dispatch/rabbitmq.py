
import logging

from smartpager.dispatch.base import GenericDispatch
from smartpager.dispatch.utils import CelerySingleton, CeleryVariables
from smartpager.dispatch import DispatchException

log = logging.getLogger(__name__)


class RabbitMQDispatch(GenericDispatch):

    # pull down configuration?
    # http://stackoverflow.com/questions/12398134/accessing-celery-instance-outside-of-virtualenv
    # amqp://smartpager:smartpager@10.10.10.100:5672

    def __init__(self, host='localhost', port=5672, user='', password=''):
        super(RabbitMQDispatch, self).__init__()

        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.broker_url = 'amqp://{}:{}@{}:{}'.format(self.user, self.password, self.host, self.port)
        self.sanitized_broker_url = 'amqp://<username>:<password>@{}:{}'.format(self.host, self.port)

    def send_message(self, message_params):

        log.debug('Sending message via RabbitMQ to {}'.format(self.sanitized_broker_url))

        sender_id = message_params.get('sender_id', None)
        message_type = message_params.get('message_type', None)
        message_data = message_params.get('message_data', None)
        users = message_params.get('users', None)
        groups = message_params.get('groups', None)
        thread = message_params.get('thread', None)
        attachments = message_params.get('attachments', None)
        enumerated_user_id = message_params.get('enumerated_user_id', None)

        # Have to use 'is not None' as an int that is 0 evaluates to False in Python
        if not (sender_id is not None and message_type is not None and message_data and (users or groups)):
            raise DispatchException('Message did not contain the minimum required elements.')

        msg_params = {
            'sender_id': sender_id,
            'message_type_id': message_type,
            'message_data': message_data,
        }

        if users:
            msg_params['users'] = users

        if groups:
            msg_params['groups'] = groups

        if thread:
            msg_params['thread'] = thread

        if attachments:
            msg_params['attachments'] = attachments

        if enumerated_user_id:
            msg_params['enumerated_user_id'] = enumerated_user_id

        return CelerySingleton(broker=self.broker_url).send_task(CeleryVariables.SEND_MSG_TASK, [],
                                                                 serializer=CeleryVariables.SEND_MSG_FORMAT,
                                                                 kwargs=msg_params)








