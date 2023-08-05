# -*- coding: utf-8 -*-
from __future__ import absolute_import

from ConfigParser import SafeConfigParser
from urllib import urlencode
from decimal import Decimal
import requests
import json
import re
import os

def json_encode_decimal(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(repr(obj) + " is not JSON serializable")


class Client(object):
    def __init__(self, app_key=None, app_token=None, sandbox=True):
        self.app_key = app_key
        self.app_token = app_token
        self.sandbox = sandbox

        parser = SafeConfigParser()
        parser.read(os.path.dirname(os.path.abspath(__file__))+'/config.ini')

        self.PRODUCTION_URL = parser.get('config', 'production_url')
        self.SANDBOX_URL = parser.get('config', 'sandbox_url')
        self.SDK_VERSION = parser.get('config', 'sdk_version')

    @property
    def url(self):
    	return self.SANDBOX_URL if self.sandbox else self.PRODUCTION_URL

    @property
    def _auth(self):
    	return requests.auth.HTTPBasicAuth(self.app_key, self.app_token)

    def get(self, path, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        response = requests.get(self.make_path(path), params=urlencode(params), headers=headers, auth=self._auth)
        return response

    def post(self, path, body=None, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if body:
            body = json.dumps(body, default=json_encode_decimal)
        response = requests.post(self.make_path(path), data=body, params=urlencode(params), headers=headers)
        return response

    def put(self, path, body=None, params={}):
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if body:
            body = json.dumps(body, default=json_encode_decimal)
        response = requests.put(self.make_path(path), data=body, params=urlencode(params), headers=headers)
        return response

    def make_path(self, path):
        if not (re.search("^http", path)):
            if not (re.search("^\/", path)):
                path = "/" + path
            path = self.url + path
        return path