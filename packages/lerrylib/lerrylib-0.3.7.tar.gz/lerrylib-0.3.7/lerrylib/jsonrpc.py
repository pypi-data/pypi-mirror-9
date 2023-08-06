#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, traceback
from uuid import uuid4
import requests
from ujson import dumps, loads

class JSONClient(object):
    def __init__(self, url):
        self.url = url
        self.request = requests.Session()

    def _make_data(self, method, *args, **kwargs):
        if kwargs:
            params = kwargs
            if args:
                params["__args"] = args
        else:
            params = args
        return {
            "method": unicode(method),
            "id": unicode(uuid4()),
            "jsonrpc": "2.0",
            "params": params
        }

    def _fetch(self, method, *args, **kwargs):
        data = self._make_data(method, *args, **kwargs)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        try:
            print "return\n", data
            req = self.request.post(self.url, data=dumps(data), headers=headers, timeout=20)
            if req.status_code == 200:
                return self._parse_result(data, req.text)
            else:
                msg = "\n\nError: %s\n %s" % (req.status_code, req.content)
                sys.stderr.write(msg)
        except:
            traceback.print_exc(file=sys.stderr)

    def _parse_result(self, request, text):
        try:
            data = loads(text)
            if request["id"] != data["id"]:
                msg = "Error: id not match"
            elif data["error"]:
                msg = data["error"]
            else:
                print "get\n", data["result"]
                return data["result"]
            sys.stderr.write(msg)
        except:
            traceback.print_exc(file=sys.stderr)

    def __getattr__(self, method):
        def _(*args, **kwargs):
            return self._fetch(method, *args, **kwargs)
        return _