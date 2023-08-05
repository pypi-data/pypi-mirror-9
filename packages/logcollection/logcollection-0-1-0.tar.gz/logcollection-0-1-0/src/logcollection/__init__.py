# -*- coding: utf-8 -*-
"""
- Slack -> ok
- Hipchat -> ok
- Chatwork
- Skype
- LINE
- Fluentd -> ok
- Facebook
- Goolge Chat
- Lingr
- Email
- Twitter
- Github Issues
- Butbicket Issues
- Redmine Issues -> ok
- Pastebin
- Errbit
"""
import json
import logging

import requests
import zope.dottedname.resolve
import zope.interface
from zope.interface import (
    implementer,
    Interface,
    )
import fluent.sender


class RedmineSender(object):
    def __init__(self, url, username, password, project_id=None,
                 tracker_id=None, status_id=None, assigned_to_id=None):
        self._url = url
        self._username = username
        self._password = password
        self._project_id = project_id
        self._tracker_id = tracker_id
        self._status_id = status_id
        self._assgined_to_id = assigned_to_id
        self._conn = None

    def connect(self):
        import redmine
        if not self._conn:
            self._conn = redmine.Redmine(
                self._url,
                self._username,
                self._password,
                )

    def build(self, msg, record=None):
        issue = self._conn.issue.new()
        issue.proejct_id = self._project_id
        issue.tracker_id = self._tracker_id
        issue.status_id = self._status_id
        issue.assigned_to_id = self._assigned_to_id

        issue.subject = u'error'
        issue.description = '''
        <pre>
          {}
        </pre>'''.format(msg)
        return issue

    def send(self, *args, **kwds):
        req = self.build(*args, **kwds)
        return req.save()


class SlackAPIChatPostMessageSender(object):
    api_url = 'https://slack.com/api/chat.postMessage'

    def __init__(self, token, channel, username, icon_emoji=':gohst'):
        self._token = token
        self._url = self.api_url
        self._channel = channel
        self._username = username
        self._icon_emoji = icon_emoji

    def connect(self):
        pass

    def build(self, msg, record=None):
        return {
            'token': self._token,
            'channel': self._channel,
            'username': self._username,
            'icon_emoji': self._icon_emoji,
            'text': msg,
            }

    def send(self, *args, **kwds):
        req = self.build(*args, **kwds)
        return requests.post(self._url, params=req, verify=False)

    def close(self):
        pass


class SlackIncomingWebHookSender(object):
    api_url = 'https://{}/services/hooks/incoming-webhook?token={}'

    def __init__(self, domain, token, channel, username, icon_emoji=':gohst'):
        self._url = self.api_url.format(domain, token)
        self._channel = channel
        self._username = username
        self._icon_emoji = icon_emoji

    def connect(self):
        pass

    def build(self, msg, record=None):
        return json.dumps({
            'channel': self._channel,
            'username': self._username,
            'icon_emoji': self._icon_emoji,
            'text': msg,
            })

    def send(self, *args, **kwds):
        req = self.build(*args, **kwds)
        return requests.post(self._url, req, verify=False)

    def close(self):
        pass


class HipChatSender(object):
    def __init__(self,
                 token,
                 room_id,
                 timeout=10,
                 notify=0,
                 message_format='text',
                 api='rooms/messages',
                 method='POST',
                 ):
        self._api = api
        self._method = method
        self._timeout = timeout
        self._notify = notify
        self._conn = None

    def connect(self):
        import hipchat
        if not self._conn:
            self._conn = hipchat.HipChat(token=self._token)

    def build(self, msg, record=None):
        return {
            'room_id': self._room_id,
            'from': 'dummy',
            'message': msg,
            'message_format': self._message_format,
            'notify': self._notify,
            }

    def send(self, *args, **kwds):
        req = self.build(*args, **kwds)
        self._send(req)
        return self._conn.method(
            self._api,
            self._method,
            req,
            timetout=self._timetout,
            )

    def close(self):
        pass


class FluentSender(fluent.sender.FluentSender):
    def connect(self):
        self._reconnect()

    def build(self, msg, record=None):
        label = None
        timestamp = None
        return self._make_packet(label, timestamp, msg)

    def send(self, *args, **kwds):
        req = self.build(*args, **kwds)
        return self._send(req)

    def close(self):
        self._close()

key_sender = {
    'slack-webhook': SlackIncomingWebHookSender,
    'slack-api': SlackAPIChatPostMessageSender,
    'hipcaht': HipChatSender,
    'fluent': FluentSender,
    'redmine': RedmineSender,
    }


class LogCollectionHandler(logging.Handler):
    def __init__(self, sender_name, *args, **kwds):
        super(LogCollectionHandler, self).__init__()
        self._sender_name = sender_name
        self._args = args
        self._kwds = kwds
        self._conn = None
        self.connect()

    def connect(self):
        if not self._conn:
            klass = key_sender.get(self._sender_name, None) or \
                zope.dottedname.resolve.resolve(self._sender_name)
            self._conn = klass(*self._args, **self._kwds)
        self._conn.connect()

    def emit(self, record):
        msg = self.format(record)
        self._conn.send(msg, record)

    def close(self):
        self.aquire()
        try:
            self._conn.close()
            super(LogCollectionHandler, self).close()
        finally:
            self.release()
