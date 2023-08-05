
import logging

from dateutil import parser

from . import SmartPagerResourceParseError
from smartpager.rest.utils import make_smartpager_request


class Resource(object):
    """
    Rest Resource
    """
    def __init__(self, base_url, auth, timeout=None, resource_name='Resource'):
        self.base_url = self._prepare_base_url(base_url)
        self.auth = auth
        self.timeout = timeout
        self.resource_name = resource_name

    def request(self, method, url, **kwargs):
        """
        Send an http request to the resource
        """
        if 'timeout' not in kwargs and self.timeout:
            kwargs['timeout'] = self.timeout

        response = make_smartpager_request(method, url, self.auth, **kwargs)
        return response

    def load_from_json(self, json_data):
        """
        Load a JSON object of parameters into the resource's properties dictionary.
        Make sure not to clobber the uri property.
        (Is the default function - loads everything as a property)
        """
        if json_data and 'uri' in json_data.keys():
            del json_data['uri']

        self.__dict__.update(json_data)

    def _prepare_base_url(self, url):
        sanitized_url = url
        if str(url).endswith('/') or str(url).endswith('\\'):
            sanitized_url = str(url)[:-1]
        return sanitized_url

    @property
    def uri(self):
        return '{}/{}'.format(self.base_url, self.resource_name)


class SmartPagerResource(Resource):
    """
    A generic smartpager REST resource
    """
    def __init__(self, base_url, auth, timeout=None):
        super(SmartPagerResource, self).__init__(base_url, auth, timeout)
        self.id = None

    def get(self, uid, params=None):
        """
        Get resources based on the uid given.
        """

        uri = '{}/{}/'.format(self.uri, uid)

        if params and 'url_extension' in params:
            uri += '{}/'.format(params.get('url_extension'))
            del params['url_extension']

        response = self.request('GET', uri, params=params)
        data = response.json()

        result = self.json_to_entity(data)
        return result

    def list(self, params):
        """
        Get (possibly) multiple resources based on the parameters.
        Returns a list of Resource objects specified by the parameters.
        """

        uri = self.uri

        if params and 'id' in params:
            uri += '/{}'.format(params.get('id'))
            # del params['id']

        if params and 'url_extension' in params:
            uri += '/{}'.format(params.get('url_extension'))
            del params['url_extension']

        response = self.request('GET', uri + '/', params=params)
        json_data = response.json()

        if json_data and 'id' in json_data:
            result = self.json_to_entity(json_data)
            result_set = [result, ]

        elif 'results' in json_data:
            paginated_data = json_data.get('results')
            result_set = [self.json_to_entity(data) for data in paginated_data]

        else:
            result_set = [self.json_to_entity(data) for data in json_data]

        return result_set

    def create(self, params):
        """
        Create a resource with the given params.
        Returns the created resource
        """
        url = self.uri + '/'
        response = self.request('POST', url, params=params)
        data = response.json()
        resource = self.json_to_entity(data)
        return resource

    def delete(self, uid):
        """
        Delete the specified resource.
        Returns a boolean (success)
        """
        uri = '{}/{}/'.format(self.uri, uid)
        response = self.request('DELETE', uri)
        return response.status_code == 204

    def update(self, uid, params):
        """
        Update the specified resource with the parameters given
        """
        uri = '{}/{}/'.format(self.uri, uid)
        response = self.request('PUT', uri, params)
        data = response.json()
        resource = self.json_to_entity(data)
        return resource

    def json_to_entity(self, data):
        """
        Takes json and returns an entity (resource).
        SmartPager resources must implement this function.
        :param data: json data
        :return: an instance of a SmartPagerResource
        """
        raise NotImplementedError


class SmartPagerUser(SmartPagerResource):

    id = None
    username = ''
    title = ''
    first_name = ''
    last_name = ''
    email = ''
    is_active = False
    ringtone = ''
    user_type = ''
    appear_offline = False
    device_type = ''
    photo = ''
    user_timezone = ''
    mobile_number = ''
    home_number = ''
    user_permissions = []
    groups = []
    account = None
    routing_policy = None
    alerting_policy = None
    is_online = None

    def __init__(self, base_url, auth, timeout=None):
        super(SmartPagerUser, self).__init__(base_url, auth, timeout)

    def json_to_entity(self, data):
        """
        Converts JSON to an entity (resource) - Overridden function from SmartPagerResource
        :param data: json data containing a dictionary of the parameters for a SmartPagerUser entity
        :return: a SmartPagerUser entity
        """
        entity = SmartPagerUser(self.base_url, self.auth, self.timeout)

        if 'id' not in data:
            raise SmartPagerResourceParseError('Missing ID')

        entity.id = data.get('id')
        entity.username = data.get('username')
        entity.title = data.get('title')
        entity.first_name = data.get('first_name')
        entity.last_name = data.get('last_name')
        entity.email = data.get('email')
        entity.is_active = True if (data.get('is_active') == 'true') else False
        entity.ringtone = data.get('ringtone')
        entity.user_type = data.get('user_type')
        entity.appear_offline = True if (data.get('appear_offline') == 'true') else False
        entity.device_type = data.get('device_type')
        entity.photo = data.get('photo')
        entity.user_timezone = data.get('user_timezone')
        entity.mobile_number = data.get('mobile_number')
        entity.home_number = data.get('home_number')
        entity.user_permissions = data.get('user_permissions')
        entity.groups = data.get('groups')
        entity.account = data.get('account')
        entity.routing_policy = data.get('routing_policy')
        entity.alerting_policy = data.get('alerting_policy')
        entity.is_online = data.get('is_online')

        return entity


class SmartPagerGroup(SmartPagerResource):

    name = ''
    account = None
    permissions = []

    def __init__(self, base_url, auth, timeout=None):
        super(SmartPagerGroup, self).__init__(base_url, auth, timeout)

    def json_to_entity(self, data):
        entity = SmartPagerGroup(self.base_url, self.auth, self.timeout)
        entity.name = data.get('name')
        entity.account = data.get('account')
        entity.permissions = data.get('permissions')

        return entity


class SmartPagerPagingGroup(SmartPagerResource):

    name = ''
    id = None
    type = ''
    users = []
    account = None

    polymorphic_ctype = None
    escalation_policy = None

    # Schedule-Specific
    fail_over_user = None
    calendar = None
    occurrences = []

    def __init__(self, base_url, auth, timeout=None):
        super(SmartPagerPagingGroup, self).__init__(base_url, auth, timeout)

    def json_to_entity(self, data):

        entity = SmartPagerPagingGroup(self.base_url, self.auth, self.timeout)

        entity.name = data.get('name')
        entity.id = data.get('id')
        entity.type = data.get('type')
        entity.users = data.get('users')
        entity.polymorphic_ctype = data.get('polymorphic_ctype')

        ep = data.get('escalation_policy')
        entity.escalation_policy = ep if not ep == 'null' else None

        fou = data.get('fail_over_user')
        entity.fail_over_user = fou if not fou == 'null' else None

        entity.calendar = data.get('calendar')
        entity.occurrences = data.get('occurrences')

        entity.account = data.get('account')

        return entity


class SmartPagerAccount(SmartPagerResource):

    id = None
    name = ''
    routing_policy = None
    alerting_policy = None
    default_timezone = ''
    partners = []

    dispatch_user = None
    details = ''
    open_communication = False
    assignable_message_types = False
    failover_user = None

    secure_sms_template = None
    insecure_sms_template = None
    secure_email_subject = None
    insecure_email_subject = None
    secure_email_body = None
    insecure_email_body = None
    country_code = None

    def __init__(self, base_url, auth, timeout=None):
        super(SmartPagerAccount, self).__init__(base_url, auth, timeout)

    def json_to_entity(self, data):

        entity = SmartPagerAccount(self.base_url, self.auth, self.timeout)

        if 'id' not in data:
            raise SmartPagerResourceParseError('Missing ID')

        entity.id = data.get('id')
        entity.name = data.get('name')
        entity.routing_policy = data.get('routing_policy')
        entity.alerting_policy = data.get('alerting_policy')
        entity.default_timezone = data.get('default_timezone')
        entity.partners = data.get('partners')

        entity.dispatch_user = data.get('dispatch_user')
        entity.details = data.get('details')

        oc = data.get('open_communication')
        entity.open_communication = oc if oc else False

        amt = data.get('assignable_message_types')
        entity.assignable_message_types = amt if amt else False

        entity.failover_user = data.get('failover_user')
        entity.secure_sms_template = data.get('secure_sms_template')
        entity.insecure_sms_template = data.get('insecure_sms_template')
        entity.secure_email_subject = data.get('secure_email_subject')
        entity.insecure_email_subject = data.get('insecure_email_subject')
        entity.secure_email_body = data.get('secure_email_body')
        entity.insecure_email_body = data.get('insecure_email_body')
        entity.country_code = data.get('country_code')

        return entity


class SmartPagerMessage(SmartPagerResource):

    id = None
    data = []
    sender_name = ''
    user_is_sender = False
    sender = None
    thread = None
    message_type = None
    message_body = ''
    created = None
    modified = None

    def __init__(self, base_url, auth, timeout=None):
        super(SmartPagerMessage, self).__init__(base_url, auth, timeout)

    def json_to_entity(self, data):
        entity = SmartPagerMessage(self.base_url, self.auth, self.timeout)

        if 'id' not in data:
            raise SmartPagerResourceParseError('Missing ID')

        entity.id = data.get('id')
        entity.data = data.get('data')
        entity.sender_name = data.get('sender_name')
        entity.user_is_sender = True if (data.get('user_is_sender') == 'true') else False
        entity.sender = data.get('sender')
        entity.thread = data.get('thread')
        entity.message_type = data.get('message_type')
        entity.message_body = data.get('message_body')

        #iso8601 datetime string
        if 'created' in data:
            entity.created = parser.parse(data.get('created'))

        if 'modified' in data:
            entity.modified = parser.parse(data.get('modified'))

        return entity


class SmartPagerMessageType(SmartPagerResource):

    id = None
    fields = []
    response_type = ''
    name = ''
    account = None
    alerting_policy = None
    attachments_allowed = False
    response_options = False
    requires_confirm = False
    apply_escalations = False
    telephone_friendly = False

    def __init__(self, base_url, auth, timeout):
        super(SmartPagerMessageType, self).__init__(base_url, auth, timeout)

    def json_to_entity(self, data):
        entity = SmartPagerMessageType(self.base_url, self.auth, self.timeout)

        if 'id' not in data:
            raise SmartPagerResourceParseError('Missing ID')

        entity.id = data.get('id')
        entity.fields = [SPMessageTypeField(**mtfield) for mtfield in data.get('fields')]
        entity.response_type = data.get('response_type')
        entity.name = data.get('name')
        entity.account = data.get('account')
        entity.alerting_policy = data.get('alerting_policy')
        entity.attachments_allowed = True if (data.get('attachments_allowed') == 'true') else False
        entity.response_options = True if (data.get('response_options') == 'true') else False
        entity.requires_confirm = True if (data.get('requires_confirm') == 'true') else False
        entity.apply_escalations = True if (data.get('apply_escalations') == 'true') else False
        entity.telephone_friendly = True if (data.get('telephone_friendly') == 'true') else False

        return entity


class SPMessageTypeField(object):
    """
    IS NOT a resource; simply provides a formatted way to deal with the fields given to the message type.
    """

    read_only = False
    field_type = ''
    default_value = None
    is_callback = False
    required = False
    order = 0
    choices = []
    label = ''
    slug = ''

    def __init__(self, **kwargs):
        self.read_only = kwargs.get('read_only', False)
        self.field_type = kwargs.get('field_type', '')
        self.default_value = kwargs.get('default_value', None)
        self.is_callback = kwargs.get('is_callback', False)
        self.required = kwargs.get('required', False)
        self.order = kwargs.get('order', 0)
        self.choices = kwargs.get('choices', [])
        self.label = kwargs.get('label', '')
        self.slug = kwargs.get('slug', '')

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'{} - {}, Required: {}'.format(self.label, self.slug, self.required)


class SmartPagerOnCall(SmartPagerResource):

    id = None
    user = None
    event = None

    start = None
    end = None
    original_start = None
    original_end = None
    escalation_policy = None

    title = ''
    description = ''
    cancelled = False

    def __init__(self, base_url, auth, timeout):
        super(SmartPagerOnCall, self).__init__(base_url, auth, timeout)

    def json_to_entity(self, data):

        entity = SmartPagerOnCall(self.base_url, self.auth, self.timeout)

        entity.id = int(data.get('id')) if data.get('id') else -1

        entity.user = int(data.get('user'))
        entity.event = int(data.get('event'))

        entity.title = data.get('title', '')
        entity.description = data.get('description', '')
        entity.cancelled = True if data.get('cancelled', '') == 'true' else False

        entity.start = parser.parse(data.get('start'))
        entity.end = parser.parse(data.get('end'))
        entity.original_start = parser.parse(data.get('original_start'))
        entity.original_end = parser.parse(data.get('original_end'))

        return entity


























