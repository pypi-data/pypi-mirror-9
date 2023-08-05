
import requests
import platform
import logging

from .. import __version__
from . import InvalidRestMethodException, SmartPagerRestException, RestParams


log = logging.getLogger(__name__)


def make_smartpager_request(method, url, auth, **kwargs):
    """
    Make a smartpager request to the given url.
    :param method:
    :param url:
    :param auth: (string) smartpager auth token
    :param kwargs
    :return:
    """
    mthd = str(method).upper()

    if mthd not in RestParams.AllowedRESTMethods:
        raise InvalidRestMethodException('{} is not a valid REST method.'.format(mthd))

    if not auth:
        raise SmartPagerRestException('No auth specified.')

    headers = kwargs.get('headers', {})

    user_agent = "smartpager-python/{} (Python {})".format(__version__, platform.python_version())
    headers['User-Agent'] = user_agent
    headers['Accept-Charset'] = 'utf-8'

    if mthd == 'POST' and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    if 'Accept' not in headers:
        headers['Accept'] = 'application/json'

    if 'Authorization' not in headers:
        headers['Authorization'] = auth

    kwargs['headers'] = headers

    try:
        response = make_http_request(mthd, url, **kwargs)
    except requests.ConnectionError:
        raise SmartPagerRestException(503, message='Could not connect to service.')

    if response.status_code >= 400:
        try:
            resp_json = response.json()
            message = resp_json['message']
        except (ValueError, KeyError):
            message = response.content

        raise SmartPagerRestException(response.status_code, url, message=message, method=mthd)

    return response


def make_http_request(method, url, data=None, headers=None, timeout=None,
                      redirects_allowed=True, params=None):
    """
    Make a REST request to the given url with the given parameters.
    :param method: (string) the HTTP method to be used
    :param url: (string) where the request will be sent
    :param data: (dict, bytes, file) data that is to be included in the request
    :param headers: (dict) HTTP headers
    :param timeout: (float) amount of time (in seconds) to wait for response
    :param params: (dict) parameters to be added to query string
    :return:
    """
    response = requests.request(method, url,
                                data=data,
                                headers=headers,
                                timeout=timeout,
                                allow_redirects=redirects_allowed,
                                params=params)

    return response
