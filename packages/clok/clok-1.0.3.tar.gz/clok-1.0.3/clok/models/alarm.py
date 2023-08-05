#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from collections import namedtuple
import datetime
from datetime import timedelta

from tinydb import where

from .base import Base, Field
from .webradio import Webradio


AlarmEvent = namedtuple('AlarmEvent', ['time', 'type', 'alarm'])
AlarmEvent.START, AlarmEvent.STOP = range(2)


class NoAlarms(Exception):
    pass


class Alarm(Base):
    tablename = 'alarm'
    fields = {
        'days': Field(default=None),
        'start': Field(default=None),
        'duration': Field(default=30*60),
        'webradio': Field(default=None),
        'disabled': Field(default=False),
    }

    def __init__(self, **kwargs):
        super(Alarm, self).__init__(**kwargs)

    def __repr__(self):
        return '<Alarm start=%d:%02d>' % (self.start / 3600, (self.start % 3600) / 60)

    def get_webradio(self):
        return Webradio.get(uuid=self.webradio)

    def humanize(self):
        """ [Radio Canut] Lu-Ma-Me-Je-Ve (7:00 -> 7:30) """
        s = ['Lu', 'Ma', 'Me', 'Je', 'Ve', 'Sa', 'Di']
        radio = self.get_webradio().name
        jours = '-'.join([s[d] for d in sorted(self.days)])
        debut, fin = self.start, self.start + self.duration
        debut = "%d:%02d" % (debut / 3600, (debut % 3600) / 60)
        fin = "%d:%02d" % (fin / 3600, (fin % 3600) / 60)
        return "[%s] : %s (%s -> %s)" % (radio, jours, debut, fin)

    def _next_event(self, shift=0):
        now = datetime.datetime.now()
        lundi = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=now.weekday())  # ou isoweekday ? (dimanche)
        rings = (
            lundi + timedelta(days=d, seconds=(self.start + shift))
            for d in self.days
        )
        rings = sorted(
            r if r > now else r + timedelta(days=7)
            for r in rings
        )
        return rings[0]

    def next_start(self):
        return AlarmEvent(
            time=self._next_event(),
            type=AlarmEvent.START,
            alarm=self,
        )

    def next_stop(self):
        return AlarmEvent(
            time=self._next_event(shift=self.duration),
            type=AlarmEvent.STOP,
            alarm=self,
        )

    def next_event(self):
        events = [self.next_start(), self.next_stop()]
        return sorted(events, key=lambda e: e.time)[0]

    def to_next_event(self):
        return self.next_event().time - datetime.datetime.now()

    @classmethod
    def next_event_overall(cls):
        """ sort alarms by next_event(), take the first one (raise NoAlarms if empty), take its next event """
        try:
            return sorted(
                cls.filter(where('disabled') == False),
                key=lambda a: a.to_next_event()
            )[0].next_event()
        except IndexError:
            raise NoAlarms
