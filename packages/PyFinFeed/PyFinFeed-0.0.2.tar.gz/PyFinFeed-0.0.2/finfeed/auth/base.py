#! /usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

import requests

class AuthenticationMixinBase(object):

    def call_grant(self, path, data):

        assert self.app_info[0] is not None and self.app_info[1] is not None

        resp = self.post(path,
            auth=self.app_info,
            jsonify=False,
            data=data)

        return resp.status_code, resp.headers, resp.json()
