from base64 import b64encode
from hashlib import sha256
from openid.extension import Extension
from openid.store.nonce import mkNonce
from os import environ
from urllib import quote_plus
import hmac

class Auth_OpenID_Scratch(Extension):
    ns_uri = "http://paywithscratch.com/payments/schema/beta"
    ns_alias = "scratch"
    
    def __init__(self, transaction, refid=None, api_key=None, secret=None):
        self.secret = secret or environ["SCRATCH_API_SECRET"]
        self.params = {"merchant": unicode(api_key or environ["SCRATCH_API_KEY"])}
        if refid:
            self.params["refid"] = unicode(refid)
        for key in transaction.params:
            value = transaction.params[key]
            if value is not None:
                self.params[key] = unicode(value)
    
    def getExtensionArgs(self):
        args = dict(self.params)
        args["nonce"] = mkNonce()
        msg = "&".join(key + "=" + quote_plus(args[key].encode("utf-8")) for key in sorted(args))
        args["signature"] = b64encode(hmac.new(str(self.secret), msg, sha256).digest())
        return args
