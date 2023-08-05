# -*- coding: utf-8 -*-

from urlparse import urljoin
import requests

import qiniu.conf
import qiniu.rs
import qiniu.io

class Qiniu(object):

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        qiniu.conf.ACCESS_KEY = self.app.config['QINIU_ACCESS_KEY']
        qiniu.conf.SECRET_KEY = self.app.config['QINIU_SECRET_KEY']


        self.bucket = self.app.config['QINIU_BUCKET']
        self.base_url = 'http://%s.qiniudn.com/' % self.bucket or self.app.config.get('QINIU_BASIC_URL', None)
        self.get_policy = qiniu.rs.GetPolicy()
        self.put_policy = qiniu.rs.PutPolicy(self.bucket)

    @property
    def rs(self):
        return qiniu.rs

    @property
    def io(self):
        return qiniu.io

    def public_url(self, key, suffix=None):
        if not key or key.startswith('http://'):
            return key

        if suffix:
            key += suffix

        return urljoin(self.base_url, key)

    def private_url(self, key, suffix=None):
        if not key or key.startswith('http://'):
            return key

        if suffix:
            key += suffix

        url = urljoin(self.base_url, key)
        return self.get_policy.make_request(url)

    def upload_with_stream(self, file_stream, key):
        uptoken = self.put_policy.token()
        ret, err = qiniu.io.put(uptoken, key, file_stream)
        if err is not None:
            raise UploadError(err)

    def upload_with_url(self, file_url, key):
        r = requests.get(file_url, stream=True)
        return self.upload_with_stream(r.content, key)


class UploadError(Exception):
    pass
