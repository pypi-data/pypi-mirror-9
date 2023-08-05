# -*- coding: utf-8 -*-

"""Enforce HTTP Strict Transport Security (see e.g.: `#`_).
  
  _`#`: http://www.imperialviolet.org/2012/07/19/hope9talk.html
"""

import logging
logger = logging.getLogger(__name__)

import os

try:
    import urlparse
except ImportError: #py3
    import urllib.parse as urlparse

from pyramid.events import NewRequest
from pyramid.events import NewResponse
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.request import Request
from pyramid.settings import asbool

DEFAULT_SETTINGS = {
    'max_age': os.environ.get('HSTS_MAX_AGE', 10886400),
    'preload': os.environ.get('HSTS_PRELOAD', True),
    'include_subdomains': os.environ.get('HSTS_INCLUDE_SUBDOMAINS', True),
    'protocol_header': os.environ.get('HSTS_PROTOCOL_HEADER', None),  
}

def hsts_redirect_to_https(event, secure_url=None):
    """Redirects `http://` GET requests to `https://` and blocks non `https://`
      requests to other request methods.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_event = Mock()
          >>> mock_event.request = mock_request
      
      Noop if the request is over https://
      
          >>> mock_request.scheme = 'https'
          >>> hsts_redirect_to_https(mock_event)
      
      Or if the value of the configured ``hsts.protocol_header`` is https::
      
          >>> mock_request.scheme = 'http'
          >>> mock_request.registry.settings = {'hsts.protocol_header': 'Foo'}
          >>> mock_request.headers = {'Foo': 'https'}
          >>> hsts_redirect_to_https(mock_event)
      
      Otherwise if a GET request, redirects to the https equivalent::
      
          >>> mock_request.scheme = 'http'
          >>> mock_request.registry.settings = {'hsts.protocol_header': 'Foo'}
          >>> mock_request.headers = {'Foo': 'http'}
          >>> mock_request.method = 'GET'
          >>> mock_request.url = 'http://foo.com'
          >>> try:
          ...     hsts_redirect_to_https(mock_event)
          ... except Exception as err:
          ...     assert err.status_int == 302
      
      Otherwise forbidden::
      
          >>> mock_request.method = 'POST'
          >>> try:
          ...     hsts_redirect_to_https(mock_event)
          ... except Exception as err:
          ...     assert err.status_int == 403
      
    """
    
    # Compose.
    if secure_url is None:
        secure_url = ensure_secure_url
    
    # Unpack the event.
    request = event.request
    settings = request.registry.settings
    
    # Exit if this is https (or any secure protocol).
    if request.scheme.endswith('s'):
        return
    
    # E.g.: on Heroku, they pass the protocol though using `X-Forwarded-Proto`.
    protocol_header = settings.get('hsts.protocol_header', None)
    if protocol_header:
        protocol = request.headers.get(protocol_header)
        if protocol and protocol.endswith('s'):
            return
    
    # If this is an insecure GET request, then redirect.
    if request.method == 'GET' or request.method == 'HEAD':
        raise HTTPFound(location=secure_url(request.url))
    
    # Otherwise refuse the request.
    raise HTTPForbidden()

def set_hsts_header(event):
    """Add a ``Strict-Transport-Security`` header to the response.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_response = Mock()
          >>> mock_event = Mock()
          >>> mock_event.request = mock_request
          >>> mock_event.response = mock_response
      
      Sets ``Strict-Transport-Security`` header::
      
          >>> mock_request.registry.settings = {}
          >>> set_hsts_header(mock_event)
          >>> mock_response.headers.add.assert_called_with('Strict-Transport-Security',
          ...         'max-age=8640000; includeSubDomains; preload')
          >>> mock_request.registry.settings = { 
          ...     'hsts.max_age': 12,
          ...     'hsts.include_subdomains': 'false',
          ...     'hsts.preload': 'false',
          ... }
          >>> set_hsts_header(mock_event)
          >>> mock_response.headers.add.assert_called_with('Strict-Transport-Security',
          ...         'max-age=12')
      
    """
    
    # Unpack the event.
    request = event.request
    response = event.response
    settings = request.registry.settings
    
    # Unpack the settings.
    max_age = settings['hsts.max_age']
    include_subdomains = asbool(settings.get('hsts.include_subdomains', True))
    preload = asbool(settings.get('hsts.preload', True))

    # Build and set a `Strict-Transport-Security` header.
    value = 'max-age={0}'.format(max_age)
    if include_subdomains:
        value += '; includeSubDomains'
    if preload:
        value += '; preload'
    response.headers.add('Strict-Transport-Security', value)

def ensure_secure_url(url, parse_url=None):
    """Add an ``s`` to the ``url`` protocol, if necessary."""
    
    if parse_url is None:
        parse_url = urlparse.urlparse
    
    # If it's not secure, append an ``s`` to the protocol.
    parsed = parse_url(url)
    protocol = parsed.scheme
    netloc = parsed.netloc
    host = netloc.split(':')[0] if netloc else netloc
    if protocol and not protocol.endswith('s') and not host == 'localhost':
        original_protocol = '{0}://'.format(protocol)
        secure_protocol = '{0}s://'.format(protocol)
        url = url.replace(original_protocol, secure_protocol, 1)
    return url

def secure_request_url(request, method_name, request_cls=None, secure_url=None):
    """Overrides ``getattr(request, method_name)`` to make sure the
      return value has a secure protocol.
    """
    
    # Test jig.
    if request_cls is None:
        request_cls = Request
    if secure_url is None:
        secure_url = ensure_secure_url
    
    # Cache the original request method or property.
    original = getattr(request_cls(request.environ), method_name)
    
    # If the value isn't callable, it's a property, so secure that.
    if not callable(original):
        return secure_url(original)
    
    # Otherwise return a secured method.
    return lambda *args, **kwargs: secure_url(original(*args, **kwargs))

def secure_host_url(request, secure_url=None):
    """Overrides ``host_url`` to make sure the protocol is secure."""
    
    # Test jig.
    if secure_url is None:
        secure_url = secure_request_url
    
    return secure_url(request, 'host_url')

def secure_application_url(request, secure_url=None):
    """Overrides ``application_url`` to make sure the protocol is secure."""
    
    # Test jig.
    if secure_url is None:
        secure_url = secure_request_url
    
    return secure_url(request, 'application_url')

def secure_resource_url(request, secure_url=None):
    """Overrides ``resource_url`` to make sure the link is secure."""
    
    # Test jig.
    if secure_url is None:
        secure_url = secure_request_url
    
    return secure_url(request, 'resource_url')

def secure_route_url(request, secure_url=None):
    """Overrides ``route_url`` to make sure the link is secure."""
    
    # Test jig.
    if secure_url is None:
        secure_url = secure_request_url
    
    return secure_url(request, 'route_url')

def secure_redirect_tween(handler, registry, join_url=None, secure_url=None):
    """Pyramid tween factory that ensures that, if the response is a redirect
      with a relative path, we join it to a url that's secured. (If we don't do
      this the the webob base library will expand it using the request environ
      which may lead to expansion into an insecure url).
    """
    
    # Compose.
    if join_url is None:
        join_url = urlparse.urljoin
    if secure_url is None:
        secure_url = ensure_secure_url
    
    def tween(request):
        """If the response is a redirect, then make sure the location is a
          full url that's been passed to our ``secure_url`` function.
        """
        
        response = handler(request)
        if 300 <= response.status_code < 400:
            if response.location is not None:
                response.location = secure_url(response.location)
        return response
    
    return tween

def includeme(config):
    """Allow developers to use ``config.include('pyramid_hsts')``."""
    
    # Apply the default settings.
    settings = config.registry.settings
    for key, value in DEFAULT_SETTINGS.items():
        nskey = 'hsts.{0}'.format(key)
        settings.setdefault(nskey, value)

    # Config event subscrtibers.
    config.add_subscriber(hsts_redirect_to_https, NewRequest)
    config.add_subscriber(set_hsts_header, NewResponse)
    
    # Patch request methods.
    config.set_request_property(secure_host_url, 'host_url', reify=True)
    config.set_request_property(secure_application_url, 'application_url', reify=True)
    config.set_request_property(secure_resource_url, 'resource_url', reify=True)
    config.set_request_property(secure_route_url, 'route_url', reify=True)
    
    # Secure redirects.
    config.add_tween('pyramid_hsts.secure_redirect_tween')
