#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from ..cron import CronService, Process
from ..models import Alarm


def test_update(mocker):
    m_cancel_alarm = mocker.patch.object(CronService, 'cancel_alarm')
    m_next_event_overall = mocker.patch.object(Alarm, 'next_event_overall')
    m_start = mocker.patch.object(Process, 'start')

    cron = CronService()
    cron.update()

    m_cancel_alarm.assert_called_with()
    m_next_event_overall.assert_called_with()
    m_start.assert_called_with()
