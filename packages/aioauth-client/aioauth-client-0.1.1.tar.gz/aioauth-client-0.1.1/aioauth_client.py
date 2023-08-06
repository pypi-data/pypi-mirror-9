""" Support OAuth for AIOHTTP. """

import logging
import aiohttp
from aiohttp import web
import hmac
import base64
import asyncio
import time
from random import SystemRandom
from urllib.parse import urlencode, urljoin, quote, parse_qsl, urlsplit, urlunsplit
from hashlib import sha1


__version__ = "0.1.1"
__project__ = "aioauth-client"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


random = SystemRandom().random


class Signature(object):

    """ Abstract base class for signature methods. """

    name = None

    def _escape(self, s):
        bs = s.encode('utf-8')
        return quote(bs, '~').encode('utf-8')

    def _remove_qs(self, url):
        """ Remove a query string from a URL. """
        scheme, netloc, path, query, fragment = urlsplit(url)

        return urlunsplit((scheme, netloc, path, '', fragment))

    def sign(self, consumer_secret, method, url, oauth_token_secret=None, **params):
        """ Abstract method. """
        raise NotImplementedError


class HmacSha1Signature(Signature):

    """ HMAC-SHA1 Signature Method. """

    name = 'HMAC-SHA1'

    def sign(self, consumer_secret, method, url, oauth_token_secret=None, **params):
        """ Create a signature using HMAC-SHA1. """
        params = "&".join("%s=%s" % (k, quote(str(value), '~'))
                          for k, value in sorted(params.items()))
        method = method.upper()
        url = self._remove_qs(url)

        signature = b"&".join(map(self._escape, (method, url, params)))

        key = self._escape(consumer_secret) + b"&"
        if oauth_token_secret:
            key += self._escape(oauth_token_secret)

        hashed = hmac.new(key, signature, sha1)
        return base64.b64encode(hashed.digest()).decode()


class PlaintextSignature(Signature):

    """ PLAINTEXT Signature Method. """

    name = 'PLAINTEXT'

    def sign(self, consumer_secret, method, url, oauth_token_secret=None, **params):
        """ Create a signature using PLAINTEXT. """
        key = self._escape(consumer_secret) + b'&'
        if oauth_token_secret:
            key += self._escape(oauth_token_secret)
        return key.decode()


class ClientRegistry(type):

    """ Register OAUTH clients. """

    clients = {}

    def __new__(mcs, name, bases, params):
        """ Save a created client in self. """
        cls = super().__new__(mcs, name, bases, params)
        if cls.name:
            mcs.clients[cls.name] = cls
        return cls


class Client(object, metaclass=ClientRegistry):

    """ Abstract Client class. """

    name = None
    base_url = None
    authorize_url = None
    access_token_url = None
    access_token_key = 'access_token'

    def __init__(self, base_url=None, authorize_url=None, access_token_key=None,
                 access_token_url=None, logger=None):
        """ Initialize the Client. """
        self.base_url = base_url or self.base_url
        self.authorize_url = authorize_url or self.authorize_url
        self.access_token_key = access_token_key or self.access_token_key
        self.access_token_url = access_token_url or self.access_token_url
        self.logger = logger or logging.getLogger('OAuth: %s' % self.name)

    def _get_url(self, url):
        if self.base_url and not url.startswith(('http://', 'https://')):
            return urljoin(self.base_url, url)
        return url

    def __str__(self):
        """ String representation. """
        return "%s %s" % (self.name.title(), self.base_url)

    __repr__ = lambda s: "<%s>" % str(s)


class OAuth1Client(Client):

    """ Implement OAuth. """

    name = 'oauth1'
    access_token_key = 'oauth_token'
    request_token_url = None
    version = '1.0'

    def __init__(self, consumer_key, consumer_secret, base_url=None, authorize_url=None,
                 params=None, oauth_token=None, oauth_token_secret=None, request_token_url=None,
                 access_token_url=None, access_token_key=None, logger=None, signature=None):
        """ Initialize the clients. """
        super().__init__(base_url, authorize_url, access_token_key, access_token_url, logger)

        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.request_token_url = request_token_url or self.request_token_url
        self.params = params
        self.signature = signature or HmacSha1Signature()

    def get_authorize_url(self, request_token=None, **params):
        """ Return a formatted authorize URL. """
        params.update({'oauth_token': request_token or self.oauth_token})
        return self.authorize_url + '?' + urlencode(params)

    def request(self, method, url, params=None, headers=None):
        """ Request OAuth resouce. """
        oparams = {
            'oauth_consumer_key': self.consumer_key,
            'oauth_nonce': sha1(str(random()).encode('ascii')).hexdigest(),
            'oauth_signature_method': self.signature.name,
            'oauth_timestamp': int(time.time()),
            'oauth_version': self.version,
        }
        oparams.update(params or {})

        if self.oauth_token:
            oparams['oauth_token'] = self.oauth_token

        url = self._get_url(url)

        oparams['oauth_signature'] = self.signature.sign(
            self.consumer_secret, method, url,
            oauth_token_secret=self.oauth_token_secret, **oparams)
        self.logger.debug("%s %s" % (url, oparams))
        return aiohttp.request(method, url, params=oparams, headers=headers)

    @asyncio.coroutine
    def get_request_token(self, **params):
        """ Get a request_token and request_token_secret from OAuth provider. """
        response = yield from self.request('GET', self.request_token_url, params=params)
        if response.status / 100 > 2:
            raise web.HTTPBadRequest(
                reason='Failed to obtain OAuth 1.0 request token. HTTP status code: %s'
                % response.status)
        data = yield from response.text()
        data = dict(parse_qsl(data))
        self.oauth_token = data.get('oauth_token')
        self.oauth_token_secret = data.get('oauth_token_secret')
        return self.oauth_token, self.oauth_token_secret

    @asyncio.coroutine
    def get_access_token(self, oauth_verifier, request_token=None, **params):
        """ Get an access_token from OAuth provider. """
        if request_token and self.oauth_token != request_token:
            raise web.HTTPBadRequest(
                reason='Failed to obtain OAuth 1.0 access token. Request token is invalid')

        response = yield from self.request('POST', self.access_token_url, params={
            'oauth_verifier': oauth_verifier, 'oauth_token': request_token})

        data = yield from response.text()
        data = dict(parse_qsl(data))

        self.oauth_token = data.get('oauth_token')
        self.oauth_token_secret = data.get('oauth_token_secret')

        return self.oauth_token, self.oauth_token_secret


class OAuth2Client(Client):

    """ Implement OAuth2. """

    name = 'oauth2'

    def __init__(self, client_id, client_secret, base_url=None, authorize_url=None, params=None,
                 access_token=None, access_token_url=None, access_token_key=None, logger=None):
        """ Initialize the client. """
        super().__init__(base_url, authorize_url, access_token_key, access_token_url, logger)

        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.params = params or {}

    def get_authorize_url(self, **params):
        """ Return a formatted authorize URL. """
        params = dict(self.params, **params)
        params.update({'client_id': self.client_id})
        return self.authorize_url + '?' + urlencode(params)

    def request(self, method, url, params=None, headers=None):
        """ Request OAuth2 resource. """
        url = self._get_url(url)
        params = params or {}

        if self.access_token:
            params[self.access_token_key] = self.access_token

        headers = headers or {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        return aiohttp.request(method, url, params=params, headers=headers)

    @asyncio.coroutine
    def get_access_token(self, code, **params):
        """ Get access token from OAuth provider. """
        params.update({
            'client_id': self.client_id, 'client_secret': self.client_secret,
            'code': code
        })
        response = yield from self.request('POST', self.access_token_url, params=params)
        data = yield from response.json()
        try:
            self.access_token = data['access_token']
        except Exception:
            raise web.HTTPBadRequest(
                reason='Failed to obtain OAuth access token.')
        return self.access_token


class BitbucketClient(OAuth1Client):

    """ Support Bitbucket. """

    access_token_url = 'https://bitbucket.org/!api/1.0/oauth/access_token'
    authorize_url = 'https://bitbucket.org/!api/1.0/oauth/authenticate'
    base_url = 'https://api.bitbucket.org/1.0/'
    name = 'bitbucket'
    request_token_url = 'https://bitbucket.org/!api/1.0/oauth/request_token'


class Flickr(OAuth1Client):

    """ Support Flickr. """

    access_token_url = 'http://www.flickr.com/services/oauth/request_token'
    authorize_url = 'http://www.flickr.com/services/oauth/authorize'
    base_url = 'https://api.flickr.com/'
    name = 'flickr'
    request_token_url = 'http://www.flickr.com/services/oauth/request_token'


class Meetup(OAuth1Client):

    """ Support Meetup. """

    access_token_url = 'https://api.meetup.com/oauth/access/'
    authorize_url = 'http://www.meetup.com/authorize/'
    base_url = 'https://api.meetup.com/2/'
    name = 'meetup'
    request_token_url = 'https://api.meetup.com/oauth/request/'


class Plurk(OAuth1Client):

    """ Support Plurk. """

    access_token_url = 'http://www.plurk.com/OAuth/access_token'
    authorize_url = 'http://www.plurk.com/OAuth/authorize'
    base_url = 'http://www.plurk.com/APP/'
    name = 'plurk'
    request_token_url = 'http://www.plurk.com/OAuth/request_token'


class TwitterClient(OAuth1Client):

    """ Support Twitter. """

    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'
    base_url = 'https://api.twitter.com/1.1/'
    name = 'twitter'
    request_token_url = 'https://api.twitter.com/oauth/request_token'


class TumblrClient(OAuth1Client):

    """ Support Tumblr. """

    access_token_url = 'http://www.tumblr.com/oauth/access_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    base_url = 'https://api.tumblr.com/v2/'
    name = 'tumblr'
    request_token_url = 'http://www.tumblr.com/oauth/request_token'


class VimeoClient(OAuth1Client):

    """ Support Vimeo. """

    access_token_url = 'https://vimeo.com/oauth/access_token'
    authorize_url = 'https://vimeo.com/oauth/authorize'
    base_url = 'https://vimeo.com/api/rest/v2/'
    name = 'vimeo'
    request_token_url = 'https://vimeo.com/oauth/request_token'


class YahooClient(OAuth1Client):

    """ Support Yahoo. """

    access_token_url = 'https://api.login.yahoo.com/oauth/v2/get_token'
    authorize_url = 'https://api.login.yahoo.com/oauth/v2/request_auth'
    base_url = 'https://query.yahooapis.com/v1/'
    name = 'yahoo'
    request_token_url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'


class AmazonClient(OAuth2Client):

    """ Support Amazon. """

    access_token_url = 'https://api.amazon.com/auth/o2/token'
    authorize_url = 'https://www.amazon.com/ap/oa'
    base_url = 'https://api.amazon.com/'
    name = 'amazon'


class EventbriteClient(OAuth2Client):

    """ Support Eventbrite. """

    access_token_url = 'https://www.eventbrite.com/oauth/token'
    authorize_url = 'https://www.eventbrite.com/oauth/authorize'
    base_url = 'https://www.eventbriteapi.com/v3/'
    name = 'eventbrite'


class FacebookClient(OAuth2Client):

    """ Support Facebook. """

    access_token_url = 'https://graph.facebook.com/oauth/access_token'
    authorize_url = 'https://www.facebook.com/dialog/oauth'
    base_url = 'https://graph.facebook.com/me'
    name = 'facebook'


class GithubClient(OAuth2Client):

    """ Support Github. """

    access_token_url = 'https://github.com/login/oauth/access_token'
    authorize_url = 'https://github.com/login/oauth/authorize'
    base_url = 'https://api.github.com'
    name = 'github'


class GoogleClient(OAuth2Client):

    """ Support Google. """

    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    base_url = 'https://www.googleapis.com/plus/v1'
    name = 'google'


class YandexClient(OAuth2Client):

    """ Support Yandex. """

    access_token_url = 'https://oauth.yandex.com/token'
    access_token_key = 'oauth_token'
    authorize_url = 'https://oauth.yandex.com/authorize'
    base_url = 'https://login.yandex.ru/info'
    name = 'google'
