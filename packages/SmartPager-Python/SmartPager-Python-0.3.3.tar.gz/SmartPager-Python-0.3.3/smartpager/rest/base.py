

from smartpager.resources.models import \
    SmartPagerAccount, \
    SmartPagerGroup, \
    SmartPagerMessage, \
    SmartPagerUser, \
    SmartPagerMessageType, \
    SmartPagerPagingGroup, \
    SmartPagerOnCall

from smartpager.dispatch.rabbitmq import RabbitMQDispatch


class RESTClient(object):
    """
    Full SmartPager REST client.
    """
    def __init__(self, base_url, auth, timeout=None, use_broker=False, broker_host='localhost', broker_port=5672, broker_user='', broker_pass=''):
        """

        :param base_url:
        :param auth:
        :param timeout:
        :param use_broker:
        :param broker_host:
        :param broker_port:
        :param broker_user:
        :param broker_pass:
        :return:
        """
        self.params = {
            'base_url': base_url,
            'auth': auth,
            'timeout': timeout,
        }

        self._dispatch = None
        if use_broker:
            broker_params = {
                'host': broker_host,
                'port': broker_port,
                'user': broker_user,
                'password': broker_pass,
            }

            self._dispatch = RabbitMQDispatch(**broker_params)

        self._groups = None
        self._users = None
        self._accounts = None
        self._messages = None
        self._messagetypes = None
        self._paginggroups = None
        self._oncalls = None

    def send_message(self, message_params):
        """
        If a dispatch is configured, use it to send the message, else use the REST API to create the message.
        :param message_params:
        :return:
        """
        if self._dispatch:
            self._dispatch.send_message(message_params)
        else:
            self.messages.create(message_params)

    @property
    def users(self):
        if not self._users:
            self._users = SmartPagerUser(**self.params)
            self._users.resource_name = 'users'
        return self._users

    @property
    def groups(self):
        if not self._groups:
            self._groups = SmartPagerGroup(**self.params)
            self._groups.resource_name = 'groups'
        return self._groups

    @property
    def accounts(self):
        if not self._accounts:
            self._accounts = SmartPagerAccount(**self.params)
            self._accounts.resource_name = 'accounts'
        return self._accounts

    @property
    def messages(self):
        if not self._messages:
            self._messages = SmartPagerMessage(**self.params)
            self._messages.resource_name = 'messages'
        return self._messages

    @property
    def messagetypes(self):
        if not self._messagetypes:
            self._messagetypes = SmartPagerMessageType(**self.params)
            self._messagetypes.resource_name = 'messagetypes'
        return self._messagetypes

    @property
    def paginggroups(self):
        if not self._paginggroups:
            self._paginggroups = SmartPagerPagingGroup(**self.params)
            self._paginggroups.resource_name = 'paginggroups'
        return self._paginggroups

    @property
    def oncalls(self):
        if not self._oncalls:
            self._oncalls = SmartPagerOnCall(**self.params)
            self._oncalls.resource_name = 'paginggroups'
        return self._oncalls




