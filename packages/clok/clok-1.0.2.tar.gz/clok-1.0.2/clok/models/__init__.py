#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from .base import Base, AttributeRequired
from .webradio import Webradio
from .alarm import Alarm, AlarmEvent, NoAlarms

__all__ = ['Webradio', 'Alarm', 'AlarmEvent', 'NoAlarms', 'setup_db', 'AttributeRequired']


def setup_db(db):
    Base.db = db
