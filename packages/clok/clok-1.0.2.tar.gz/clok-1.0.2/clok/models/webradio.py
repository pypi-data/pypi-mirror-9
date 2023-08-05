#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from .base import Base, Field


class Webradio(Base):
    tablename = 'webradio'
    fields = {
        'name': Field(default=None),
        'url': Field(default=None),
    }

    def __init__(self, **kwargs):
        super(Webradio, self).__init__(**kwargs)

    def __repr__(self):
        return '<Webradio name=%s url=%s>' % (self.name, self.url)
