# -*- coding: utf-8 -*-

import redis


class Redis(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.client = redis.StrictRedis()


    def __getattr__(self, item):
        return getattr(self.client, item)
