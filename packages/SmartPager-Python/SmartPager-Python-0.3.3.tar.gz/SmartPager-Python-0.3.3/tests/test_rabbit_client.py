
import unittest

from smartpager.rest.base import RESTClient


class TestRabbitClient(unittest.TestCase):
    """
    Must be tested by viewing http://10.10.10.100:15672/#/queues/%2F/celery (the queue)
    """

    # Test API user token
    auth_token = '43aeabb708e87a4277ebf6b2df3b236ce27acc39'
    base_url = 'http://localhost:8000/api/v1/'
    timeout = None

    broker_host = '10.10.10.100'
    broker_port = 5672
    broker_user = 'smartpager'
    broker_pass = 'smartpager'

    def setUp(self):
        self.auth = 'Token {}'.format(self.auth_token)

        params = {
            'use_broker': True,
            'broker_host': self.broker_host,
            'broker_port': self.broker_port,
            'broker_user': self.broker_user,
            'broker_pass': self.broker_pass,
        }

        self.client = RESTClient(self.base_url, self.auth, self.timeout, **params)

    def test_send_message(self):

        message_params = {
            'sender_id': 1,
            'message_type': 6,
            'thread': {
                'subscribers': [10],
                'groups': [11],
            },
            'message_data': {
                'patient-name': 'Caleb Shortt',
                'lab-result-scan': 40,
            },
            'users': [
                2,
            ]
        }

        print 'Sending message to broker: ' + str(self.client._dispatch.broker_url)

        self.client.send_message(message_params)





