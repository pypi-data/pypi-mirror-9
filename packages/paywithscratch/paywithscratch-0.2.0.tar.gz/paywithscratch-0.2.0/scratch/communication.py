from json import loads as json_decode, dumps as json_encode
from logging import getLogger
from openid.consumer.consumer import FAILURE, SUCCESS, Consumer
from openid.oidutil import autoSubmitHTML
from os import environ
from requests import get, post
from requests_oauthlib import OAuth1
from urlparse import urlparse, urlunparse

from .extension import Auth_OpenID_Scratch

class ScratchException(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class ScratchApi(object):
    server = environ.get("SCRATCH_SERVER", "https://paywithscratch.com/")
    api_key = environ.get("SCRATCH_KEY")
    secret = environ.get("SCRATCH_SECRET")
    path = None
    
    def __init__(self, path=None, api_key=None, secret=None, server=None):
        if path:
            self.path = path
        if api_key:
            self.api_key = api_key
        if secret:
            self.secret = secret
        if server:
            self.server = server
    
    def get(self, **params):
        path = self.path
        if params:
            path = path.format(**params)
        return self.call(get, path)
    
    def post(self, **params):
        return self.call(post, data=params)
    
    def call(self, method, path=None, **data):
        assert self.server and self.api_key and self.secret and self.path
        uri = self.server + (path or self.path)
        auth = OAuth1(self.api_key, self.secret)
        response = method(uri, auth=auth, **data)
        
        # Check for common error conditions.
        # 400 Bad Request: Usually a missing or incorrect parameter.
        # 401 Unauthorized: Incorrect or deactivated API key or secret.
        # 405 Method Not Allowed: Tried to GET a POST-only API.
        if response.status_code in (400, 401, 405):
            self.fail(response)
        
        return response
    
    def fail(self, response):
        if response.content.startswith("{"):
            result = response.json()
            message = result.get("error") or result.get("reference") or response.reason
        else:
            message = response.reason
        log = getLogger("scratch." + self.__class__.__name__)
        log.error("%s %s: %s", response.status_code, message, response.content)
        raise ScratchException(message)

class StartTransaction(ScratchApi):
    path = "payments/start/"
    
    def __init__(self, storage=None, **kwargs):
        super(StartTransaction, self).__init__(**kwargs)
        self.storage = storage
    
    def post(self, redirect, transaction, refid=None, cancel=None, registered=False, optimistic=False, inline=False):
        # Collect and sanitize parameters.
        assert redirect.startswith("http")
        params = {"redirect": redirect}
        if refid is not None:
            params["refid"] = refid
        if cancel is not None:
            assert cancel.startswith("http")
            params["cancel"] = cancel
        if registered:
            params["registered"] = True
        if optimistic:
            params["optimistic"] = True
        if inline:
            params["inline"] = True
        for key in transaction.params:
            value = transaction.params[key]
            if value is not None:
                params[key] = value
        
        # Post to Scratch.
        response = super(StartTransaction, self).post(**params)
        
        # Check for error conditions.
        if response.status_code != 200:
            self.fail(response)
        
        # Extract the JSON parameters.
        result = response.json()
        if self.storage is not None:
            # Save the transaction identifier for the finalization step.
            self.storage[result.get("transaction")] = False
        
        return result

class CompleteTransaction(ScratchApi):
    path = "payments/finalize/{token}/"
    
    def __init__(self, storage=None, **kwargs):
        super(CompleteTransaction, self).__init__(**kwargs)
        self.storage = storage
    
    def get(self, token):
        if self.storage is not None:
            # Determine whether we even need to check.
            completed = self.storage.get(token)
            if completed:
                # Already done; return the cached results.
                return completed
            if completed is None:
                # Not a transaction in progress; ignore it.
                return None
        
        # Post to Scratch.
        response = super(CompleteTransaction, self).get(token=token)
        
        # Check for normal cancellations.
        # 404 responses could mean someone changing the transaction token.
        if response.status_code in (402, 404):
            if self.storage is not None:
                self.storage[token] = None
            return None
        
        # Check for error conditions.
        if response.status_code not in (200, 208):
            self.fail(response)
        
        # Extract the JSON parameters.
        result = response.json()
        if self.storage is not None:
            # Cache the result, in case it gets requested again.
            self.storage[token] = result
        
        return result

class ScratchPage(object):
    default_site = environ.get("SCRATCH_SERVER", "https://paywithscratch.com/")
    
    def __init__(self, session, store, scratch_site=None):
        self.session = session
        self.store = store
        self.server = scratch_site or self.default_site
    
    def begin(self, redirect, transaction, refid, api_key, secret):
        consumer = Consumer(self.session, self.store)
        auth_request = consumer.begin(self.server)
        auth_request.addExtension(Auth_OpenID_Scratch(transaction, refid, api_key, secret))
        fields = urlparse(redirect)
        realm = urlunparse((fields.scheme, fields.netloc, '/', '', '', ''))
        message = auth_request.getMessage(realm, redirect)
        return ScratchVars(auth_request.endpoint.server_url, message)
    
    def complete(self, params, location):
        # On Success, return the validated Scratch parameters.
        # On Failure, return None.
        # On Error, raise an exception.
        
        consumer = Consumer(self.session, self.store)
        response = consumer.complete(params, location)
        result = None
        
        if response.status == SUCCESS:
            result = response.message.getArgs(Auth_OpenID_Scratch.ns_uri)
        elif response.status == FAILURE:
            raise ScratchException(response.message)
        
        return result

class ScratchVars(object):
    def __init__(self, server, message):
        self.server = server
        self._msg = message
    
    def params(self):
        return self._msg.toPostArgs()
    
    def form(self):
        # This is the main reason to keep the Message around.
        # No need to duplicate logic just yet...
        return self._msg.toFormMarkup(self.server)
    
    def html(self):
        return autoSubmitHTML(self.form())
    
    def json(self):
        return json_encode(self.params())
