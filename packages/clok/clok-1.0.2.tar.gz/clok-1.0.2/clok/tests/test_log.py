#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals, absolute_import

from ..log import Logger, logging


def test_logger(mocker):
    m_getLogger = mocker.patch('clok.log.logging.getLogger', autospec=True)
    m_logger = m_getLogger.return_value

    l = Logger('test')

    m_getLogger.assert_called_with('test')

    # Default setup
    m_StreamHandler = mocker.patch('clok.log.logging.StreamHandler', autospec=True)
    m_Formatter = mocker.patch('clok.log.logging.Formatter', autospec=True)
    m_formatter = m_Formatter.return_value
    m_handler = m_StreamHandler.return_value

    l.setup(level='info')

    m_handler.setLevel.assert_called_with(logging.INFO)
    m_handler.setFormatter.assert_called_with(m_formatter)
    m_Formatter.assert_called_with(Logger.DEFAULT_FORMAT)
    m_logger.setLevel.assert_called_with(logging.INFO)
    m_logger.addHandler.assert_called_with(m_handler)

    # File-logging setup
    m_FileHandler = mocker.patch('clok.log.logging.FileHandler', autospec=True)
    m_handler = m_FileHandler.return_value

    l.setup(type='file', filename='foo.test')

    m_FileHandler.assert_called_with('foo.test')
    m_handler.setLevel.assert_called_with(logging.INFO)

    # Syslog setup
    m_SysLogHandler = mocker.patch('clok.log.logging.handlers.SysLogHandler', autospec=True)
    m_handler = m_SysLogHandler.return_value

    l.setup(level='error', type='syslog')

    m_SysLogHandler.assert_called_with(address=Logger.DEFAULT_SYSLOG_ADDRESS)
    m_handler.setLevel.assert_called_with(logging.ERROR)
