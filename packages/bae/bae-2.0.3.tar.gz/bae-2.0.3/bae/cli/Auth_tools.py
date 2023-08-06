__author__ = 'luofan'

import hmac
import hashlib
import urllib
import datetime
from   bae.errors           import *
from messages import g_messager
class authTools:
    def stringkey(self,ak,sk,time_stamp,expiration):
        password = "bce-auth-v{version}/{accessKeyId}/{timestamp}/{expirationPeriodInSeconds}" \
            .format(version = 1,accessKeyId = ak, timestamp = self.get_canonical_time(time_stamp), expirationPeriodInSeconds = expiration)
        hm = hmac.new(sk, str.encode(password), hashlib.sha256)
        self.auth_token_prefix=password
        self.time_stamp = time_stamp
        self.expiration = expiration
        self.ak = ak
        self.sk = sk
        self.string_key =  hm.hexdigest()
        return self.string_key

    def genAuth(self, CanonicalHeaders = None ,uri = None, http_method = None, query = None):
        if CanonicalHeaders is None:
            if not hasattr(self, 'CanonicalHeaders'):
                raise BaeCliError("Get no header")
            else:
                CanonicalHeaders = self.CanonicalHeaders
        if uri is None:
            if not hasattr(self, 'uri'):
                uri = "/"
            else:
                uri = self.uri
        if http_method is None:
            if not hasattr(self,'http_method'):
                http_method = "GET"
            else:
                http_method =  self.http_method

        if query is None:
            if not hasattr(self,'query'):
                query = {}
            else:
                query =  self.query

        string_content = str.upper(http_method)
        string_content += "\n"
        if uri is None:
            return False
        uri_tuples = str.strip(uri,"/").split("/")
        string_content+="/"
        for uri_tuple  in uri_tuples:
            string_content += urllib.quote(uri_tuple.encode("utf-8")) + "/"
        string_content = string_content[:-1]
        string_content += "\n"
        if not query is None and isinstance(query,dict):
            string_content  +=  urllib.urlencode([(key, query[key].encode("utf-8")) for key in sorted(query.keys())])
            string_content += "\n"
        if CanonicalHeaders is None or not isinstance(CanonicalHeaders,dict) \
            or not CanonicalHeaders.has_key("Host"):
            raise BaeCliError("CanonicalHeaders is bad")
        header_keys = CanonicalHeaders.keys()
        header_keys.sort(key = lambda header : urllib.quote(str.lower(header)))
        for key in header_keys:
            string_content += urllib.quote(key.lower()) + ":"
            string_content += urllib.quote(CanonicalHeaders[key].encode("utf-8"),"") + "\n"
        string_content = string_content.strip()
        auth_token = self.auth_token_prefix
        auth_token += "/" + ";".join([k.lower() for k in header_keys])
        #g_messager.output("auth_info:\n{stringkey}\n{string_content}".format(stringkey = self.string_key, string_content =  string_content))
        h = hashlib.md5()
        h.update(string_content.encode())
        #g_messager.output("string_content md5 is:{md5}".format(md5=h.hexdigest()))

        hm = hmac.new(self.string_key, string_content.encode(), hashlib.sha256)
        auth_token += "/" + hm.hexdigest()
        '''
        res = bce_v1_signer.sign(
            credentials = bce_credentials.BceCredentials(self.ak,self.sk),
            http_method = http_method,
            path = uri,
            headers = CanonicalHeaders,
            params = {},
            timestamp = self.time_stamp,
            expiration_in_seconds = self.expiration,
            headers_to_sign = [k.lower() for k in header_keys]
        )

        g_messager.output("bce auth is %s" %res)
        g_messager.output("my auth is %s"%auth_token)
        '''
        return auth_token
    def set_method(self, method):
        self.http_method = method or "get"
    def set_query(self,query):
        self.query = query or {}
    def set_CanonicalHeaders(self, CanonicalHeaders):
        self.CanonicalHeaders = CanonicalHeaders or {}
    def set_uri(self,uri):
        self.uri = uri or "/"
    def get_canonical_time(self,timestamp=0):
        if timestamp == 0:
            utctime = datetime.datetime.utcnow()
        else:
            utctime = datetime.datetime.utcfromtimestamp(timestamp)
        return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (
            utctime.year, utctime.month, utctime.day,
            utctime.hour, utctime.minute, utctime.second)
authTool = authTools()