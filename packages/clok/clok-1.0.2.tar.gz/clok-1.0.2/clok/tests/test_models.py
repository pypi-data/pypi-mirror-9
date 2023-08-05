#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from datetime import datetime

from tinydb import where

from ..models import Alarm, NoAlarms, AlarmEvent, Webradio, setup_db, AttributeRequired


def test_webradio(test_db):
    setup_db(test_db)
    radio = Webradio(name="Lulz", url="http://example.com")
    assert not hasattr(radio, 'uuid')
    radio.save()
    assert isinstance(radio.uuid, str)
    assert repr(radio) == '<Webradio name=Lulz url=http://example.com>'
    assert radio.to_dict() == {
        'name': 'Lulz',
        'url': 'http://example.com',
        'uuid': radio.uuid
    }


def test_alarm_humanize(mock, mocker):
    a = Alarm(
        days=[0, 1, 2, 3, 4],
        start=7*3600,
        duration=30*60,
        webradio='aze',
        disabled=False,
    )

    webradio = mock.Mock()
    webradio.configure_mock(name="Lulz Radio")
    assert webradio.name == 'Lulz Radio'

    m_get_webradio = mocker.patch.object(a, 'get_webradio')
    m_get_webradio.return_value = webradio

    assert a.humanize() == '[Lulz Radio] : Lu-Ma-Me-Je-Ve (7:00 -> 7:30)'
    m_get_webradio.assert_called_with()


def test_alarm_save(test_db):
    setup_db(test_db)
    a = Alarm(days=[0, 2], start=8*3600 + 60, duration=3600, webradio='aze').save()

    assert a.eid == 1
    assert a.start == 8*3600 + 60
    assert a.disabled is False
    assert repr(a) == '<Alarm start=8:01>'

    a.days.append(1)
    a.save()

    assert a.eid == 1
    assert sorted(a.days) == [0, 1, 2]


def test_alarm_crud(test_db):
    setup_db(test_db)
    a = Alarm(days=[0, 2], start=7*3600, webradio='aze').save()
    assert Alarm.all() == [a]
    b = Alarm(days=[0], start=0, webradio='aze').save()
    assert Alarm.filter(where('start') == 0) == [b]
    Alarm.update({'webradio': 'qsd'}, where('webradio') == 'aze')
    assert Alarm.count(where('webradio') == 'qsd') == 2
    assert b.webradio == 'aze'  # not refreshed yet
    assert b.refresh().webradio == 'qsd'
    assert Alarm.get(eid=1) == a
    assert Alarm.get(uuid=b.uuid) == b
    Alarm.remove(where('start') == 0)
    assert Alarm.get(eid=2) is None


def test_alarm_get_webradio(test_db):
    setup_db(test_db)
    radio = Webradio(name="Lulz", url="http://example.com").save()
    a = Alarm(days=[], start=0, webradio=radio.uuid).save()
    assert a.eid == 1  # not affected by 'test_alarm_save'
    assert a.get_webradio().eid == radio.eid


def test_next_alarm_overall(test_db):
    setup_db(test_db)
    now = datetime.now()
    start = now.hour * 3600 + now.minute * 60 + now.second
    Alarm(days=range(7), start=start + 10, webradio='aze', disabled=True).save()  # will not ring (disable)
    a20 = Alarm(days=range(7), start=start + 20, webradio='aze').save()  # will ring in 20s : next one !
    Alarm(days=range(7), start=start + 30, webradio='aze').save()  # will ring in 30s
    assert Alarm.next_event_overall().alarm == a20
    assert Alarm.next_event_overall().type == AlarmEvent.START


def test_next_alarm_overall_failure(test_db, assert_raises):
    setup_db(test_db)
    with assert_raises(NoAlarms):
        Alarm.next_event_overall()


def test_required_fields():
    assert sorted(Alarm.required_fields()) == ['days', 'start', 'webradio']


def test_missing_fields(assert_raises):
    with assert_raises(AttributeRequired):
        Alarm(start=0).save()
