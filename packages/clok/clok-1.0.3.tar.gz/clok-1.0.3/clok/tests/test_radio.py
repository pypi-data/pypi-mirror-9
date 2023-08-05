#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from ..radio import Radio, RadioWrapped


def test_radio(mocker):
    m_Process = mocker.patch('clok.radio.Process', autospec=True)
    m_process = m_Process.return_value
    m_Queue = mocker.patch('clok.radio.Queue', autospec=True)
    m_queue = m_Queue.return_value

    r = Radio()
    r.cmd_queue = m_queue
    r.play()
    r.cmd_queue.put.assert_called_with({
        'type': 'play',
        'url': None,
    })
    r.stop()
    r.pause()
    r.unpause()
    r.toggle_pause()
    r.get_is_playing()
    r.is_playing
    r.get_url()
    r.url
    r.kill()
    m_process.join.assert_called_with()


def test_radiowrapped(mocker):
    m_Log = mocker.patch('clok.radio.Log', autospec=True)
    m_log = m_Log.return_value
    m_MpPlayer = mocker.patch('clok.radio.CustomMpPlayer', autospec=True)
    m_player = m_MpPlayer.return_value
    m_player.isPlaying.return_value = True

    r = RadioWrapped('foourl')
    m_MpPlayer.assert_called_with(m_log)

    r.play()
    m_player.play.assert_called_with('foourl')
    assert r.get_url() == 'foourl'

    r.stop()
    m_player.close.assert_called_with()

    r.pause()
    r.toggle_pause()
    m_player.pause.assert_called_with()

    m_player.isPlaying.return_value = False
    assert r.is_playing() is False
    r.unpause()
