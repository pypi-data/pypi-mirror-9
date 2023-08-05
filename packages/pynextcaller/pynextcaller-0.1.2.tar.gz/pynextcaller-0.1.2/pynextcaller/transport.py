from __future__ import unicode_literals
import json
import logging
import requests
from .constants import *


__all__ = (
    'api_request',
    'make_http_request',
)


def prepare_logger():
    log = logging.getLogger('nextcaller.transport')
    handler = logging.StreamHandler()
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    log.propagate = False
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return log


logger = prepare_logger()


def _to_json(content):
    try:
        return json.loads(content)
    except (TypeError, ValueError):
        return content


def _debug_log(value, debug=True):
    if debug:
        logger.debug(value)


def _prepare_request_data(
        data=None, headers=None, method='GET',
        timeout=None, ssl_verify=True):
    if headers is None:
        headers = {}
    kwargs = {}
    if timeout is None:
        timeout = DEFAULT_REQUEST_TIMEOUT
    kwargs['timeout'] = timeout
    if method == 'POST':
        kwargs['data'] = data
    if method == 'GET':
        kwargs['params'] = data
    kwargs['headers'] = headers
    kwargs['allow_redirects'] = True
    kwargs['verify'] = ssl_verify
    return kwargs


def api_request(url, data=None, headers=None, method='GET',
                timeout=None, ssl_verify=True, debug=False):
    kwargs = _prepare_request_data(
        data=data, headers=headers, method=method,
        timeout=timeout, ssl_verify=ssl_verify)
    response = requests.request(method, url, **kwargs)
    _debug_log('Request url: {0}'.format(response.url), debug)
    if method == 'POST':
        _debug_log('Request body: {0}'.format(response.request.body), debug)
    status_code = response.status_code
    if status_code >= 400:
        response.raise_for_status()
    return response.text


def _build_headers(auth, user_agent=None, content_type=None):
    headers = auth.get_headers()
    headers['Connection'] = 'Keep-Alive'
    if content_type is not None:
        headers['Content-Type'] = content_type
    if user_agent is not None:
        headers['User-Agent'] = user_agent
    return headers


def make_http_request(auth, url, data=None, method='GET', user_agent=None,
                      content_type=None, debug=False):
    if data is None:
        data = {}
    if user_agent is None:
        user_agent = DEFAULT_USER_AGENT
    headers = _build_headers(
        auth, user_agent=user_agent, content_type=content_type)
    requests_kwargs = {
        'method': method,
        'headers': headers,
        'data': data,
        'debug': debug
    }
    response = api_request(url, **requests_kwargs)
    return response
