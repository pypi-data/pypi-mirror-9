#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from collections import namedtuple
from uuid import uuid4

from tinydb import where


class AttributeRequired(Exception):
    pass


Field = namedtuple('Field', ['default'])


class Base(object):
    db = None  # must be overwritten
    tablename = None  # must be overwritten
    fields = None  # must be overwritten

    @classmethod
    def required_fields(cls):
        return [f for f, v in cls.fields.items() if v.default is None]

    @classmethod
    def get_table(cls):
        return cls.db.table(cls.tablename)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        for name, field in self.fields.items():
            if field.default is not None and not hasattr(self, name):
                setattr(self, name, field.default)

    def __eq__(self, other):
        return self.uuid == other.uuid

    @classmethod
    def from_dict(cls, obj, instance=None):
        instance = instance or cls()
        for k, v in obj.items():
            setattr(instance, k, v)
        setattr(instance, 'eid', obj.eid)
        return instance

    def to_dict(self):
        found = self.get_table().get(eid=self.eid)
        if found:
            return found.copy()

    def save(self):
        fields = self.fields.keys()
        if not hasattr(self, 'eid'):
            try:
                doc = {f: getattr(self, f) for f in fields if getattr(self, f) is not None}
            except AttributeError:
                raise AttributeRequired()
            doc['uuid'] = str(uuid4())
            self.eid = self.get_table().insert(doc)
            self.uuid = doc['uuid']
        else:
            old = self.get_table().get(eid=self.eid)
            dirty_fields = {
                f: getattr(self, f)
                for f in fields
                if getattr(self, f) != old.get(f)
            }
            self.get_table().update(dirty_fields, where("uuid") == self.uuid)
        return self

    def refresh(self):
        in_db = self.get_table().get(eid=self.eid)
        return self.from_dict(in_db, self)

    @classmethod
    def get(cls, eid=None, uuid=None):
        if uuid is None:
            found = cls.get_table().get(eid=eid)
            return cls.from_dict(found) if found else None
        found = cls.filter(where('uuid') == uuid)
        return found[0] if found else None

    @classmethod
    def all(cls, to_dict=False):
        ret = [cls.from_dict(o) for o in cls.get_table().all()]
        return ret if to_dict is False else [o.to_dict() for o in ret]

    @classmethod
    def filter(cls, query, to_dict=False):
        ret = [cls.from_dict(o) for o in cls.get_table().search(query)]
        return ret if to_dict is False else [o.to_dict() for o in ret]

    @classmethod
    def count(cls, query):
        return cls.get_table().count(query)

    @classmethod
    def remove(cls, query):
        cls.get_table().remove(query)

    @classmethod
    def update(cls, affectations, query):
        cls.get_table().update(affectations, query)
