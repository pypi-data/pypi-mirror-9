#-*- coding : utf-8 -*-

import json
import urllib
import requests
import uuid
import os
import platform
import hashlib
import urlparse

from   bae.config.constants import ONEKEY_ENTRY, API_ENTRY, VERSION, PROG_NAME
from   bae.errors           import *
from   bae.cli.messages     import g_messager
RETRY = 3
TIMEOUT = 30
class BaeRest:
    def __init__(self, auth_tool = None, debug = False):
        self._debug = debug
        if debug:
            try:
                import urllib3
                urllib3.connectionpool.HTTPSConnection.debuglevel = 1
                urllib3.connectionpool.HTTPConnection.debuglevel  = 1
            except ImportError:
                try:
                    requests.packages.urllib3.connectionpool.HTTPSConnection.debuglevel = 1
                    requests.packages.urllib3.connectionpool.HTTPConnection.debuglevel  = 1
                except ImportError:
                    g_messager.bug("You havn't install python-requests or urllib3, debug mode will DOWN")
        self._auth_tool = auth_tool

    def _get_user_agent(self):
        try:
            plat = "%s %s" %(platform.platform(), platform.version())
        except Exception:
            plat = "unknown"

        if os.environ.has_key("BAE_LOCALENV_VERSION"):
            plat = "LOCALENV : %s" %(os.environ["BAE_LOCALENV_VERSION"])

        return 'BAE CLI %s "%s"' %(VERSION, plat)

    def on_response(self, response, **kw):
        g_messager.debug(u"Server returns {0}".format(response.text))
        pass

    def post(self, path, data = None, require_code = False, timeout = TIMEOUT):
        self._auth_tool.set_method("POST")
        self._auth_tool.set_uri(urlparse.urlparse(path).path)
        url_path = path
        return self._request('POST', url_path, json.dumps(data), require_code = require_code,
                             headers = {'Content-Type': 'application/json'}, timeout = timeout)

    def get(self, path = '/', data = None, require_code = False, require_token = True, timeout = TIMEOUT):
        self._auth_tool.set_method("GET")
        self._auth_tool.set_uri(urlparse.urlparse(path).path)
        self._auth_tool.set_query(data)
        if data:
            url_path = path + "?" + urllib.urlencode(data)
        else:
            url_path = path

        return self._request('GET', url_path, data = None, require_code = require_code, timeout = timeout)
    
    #Developer center not support session right now
    def _session(self):
        if not hasattr(self, "session") or not self.session:
            headers = {'Accept' : 'application/json',
                       'User-Agent' : self._get_user_agent(),
                       'X-Bce-Service-Id': 'bae.bj.baidubce.com'
            }
            self.session         = requests.session()
            self.session.headers = headers
            self.hooks = {
                'response' : self.on_response
                }
        return self.session

    def _request(self, method, path, data = None, require_code = False, **kw):
        def _server_error():
            g_messager.exception()
            errmsg = u"Can't understand servers infomation "
            errmsg += unicode(res.text)
            print errmsg
            raise BaeRestError(bae_codes.api_error, errmsg)
        
        def _bae_msg(obj):
            if obj.has_key("requestId") and obj.has_key("code"):
                if obj["code"] == "Auth Error":
                    return "AK \ SK is invalid"
                else:
                    return obj["message"]
            if g_messager.use_cn and obj.has_key("message"):
                return obj["message"]["global"].encode("utf-8")
            elif obj.has_key("message_eng") and obj["message_eng"]:
                return obj["message_eng"]["global"]
            elif obj.has_key("error_msg"):
                return obj["error_msg"]
            else:
                return obj["message"]["global"]


        for i in range(0, RETRY):
            session =  self._session()
            headers = {}
            if method == "POST":
                headers["Content-length"] = str(len(data))
                session.headers["Content-length"] = str(len(data))
                headers["Content-type"] = 'application/json'
                session.headers["Content-type"] = 'application/json'
            url_res = urlparse.urlparse(path)
            if url_res.port:
                headers["Host"] = url_res.hostname + ":{port}".format(port=url_res.port)
            else:
                headers["Host"] = url_res.hostname
            headers["X-Bce-Service-Id"] = "bae.bj.baidubce.com"
            self._auth_tool.set_CanonicalHeaders(headers)
            auth = self._auth_tool.genAuth()
            session.headers["Authorization"] = auth
            res = session.request(method, path,
                                          data = data, hooks = self.hooks, **kw)
            self.session.close()
            self.session.headers = {'Accept' : 'application/json',
                       'User-Agent' : self._get_user_agent(),
                       'X-Bce-Service-Id': 'bae.bj.baidubce.com'
            }
            try:
                obj = json.loads(res.text)
                if not obj.has_key("success"):
                    pass
                elif obj["success"]:
                    if obj.has_key("page"):
                        return obj["page"]["result"]
                    else:
                        return obj["result"]
                msg = _bae_msg(obj)
                raise BaeRestError(-1, msg)
            except KeyError:
                _server_error()
            except ValueError:
                _server_error()
