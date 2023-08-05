# -*- coding: utf-8 -*-
from unittest import TestCase


class LogCollectionTestCase(TestCase):
    def _target(self, *args, **kwds):
        return

    def _call(self, *args, **kwds):
        target = self._target()
        res = target.fuc(*args, **kwds)
        return res


class SlackIncommingWebHookSenderTest(LogCollectionTestCase):
    def _setting(self):
        from pit import Pit
        setting = {
            'domain': '.slack.com',
            'token': '',
            'channel': '#general',
            'username': '',
            'icon_emoji': ':ghost:',
            }
        return Pit.get(
            'logcollection-test-slack-webhook',
            {'require': setting},
            )

    def _target(self):
        from . import SlackIncomingWebHookSender as sender_class
        setting = self._setting()
        return sender_class(**setting)

    def _call(self, *args, **kwds):
        target = self._target()
        return target.send(*args, **kwds)

    def test_send(self):
        self._call('test message')


class SlackAPIChatPostMessageSenderTest(SlackIncommingWebHookSenderTest):
    def _setting(self):
        from pit import Pit
        setting = {
            'token': '',
            'channel': '#general',
            'username': '',
            'icon_emoji': ':ghost:',
            }
        return Pit.get(
            'logcollection-test-slack-api',
            {'require': setting},
            )

    def _target(self):
        from . import SlackAPIChatPostMessageSender as sender_class
        setting = self._setting()
        return sender_class(**setting)

    def test_send(self):
        self._call('test message')


class LogCollectionHandlerBySlackWebhookTest(SlackIncommingWebHookSenderTest):
    def _target(self):
        from logging import (
            NOTSET,
            Formatter,
            )
        from . import LogCollectionHandler
        setting = self._setting()
        formatter = Formatter(
            '%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s'
            )
        handler = LogCollectionHandler(
            NOTSET,
            'logcollection.SlackIncomingWebHookSender',
            **setting)
        handler.setFormatter(formatter)
        return handler

    def _call(self, *args, **kwds):
        target = self._target()
        return target.emit(*args, **kwds)

    def _record(self):
        from logging import (
            LogRecord,
            WARNING,
            )

        return LogRecord(
            name='testlog',
            level=WARNING,
            pathname='/path/to/src/abs/path',
            lineno=10,
            msg='test message',
            args=[],
            exc_info=None,
            func='caller_func_name',
            )

    def test_it(self):
        record = self._record()
        self._call(record)
