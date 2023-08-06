# coding: utf-8
from __future__ import absolute_import, unicode_literals, print_function
import time
import logging
import hashlib

import six
from tornado import ioloop
from tornado.websocket import websocket_connect

from tmcpy.event import Event
from tmcpy.messageio import reader, writer
from tmcpy.message import Message
from tmcpy.utils import confirm_message, query_message, to_binary

__all__ = ['TmcClient']


logger = logging.getLogger('tmcpy.client')


class TmcClient(Event):

    def __init__(self, url, app_key, app_secret, group_name='default',
                 query_message_interval=50, heartbeat_interval=30,
                 *args, **kwargs):
        super(TmcClient, self).__init__(self)

        logger.info('[%s:%s]WebSocket Connect Success.', url, group_name)

        assert isinstance(url, six.string_types) and len(url) > 0
        assert isinstance(app_key, six.string_types) and len(app_key) > 0
        assert isinstance(app_secret, six.string_types) and len(app_secret) > 0
        assert isinstance(group_name, six.string_types) and len(group_name) > 0
        assert isinstance(query_message_interval, int) and 0 < query_message_interval < 60
        assert isinstance(heartbeat_interval, int) and 0 < heartbeat_interval < 60

        self.url = url
        self.app_secret = app_secret
        self.app_key = app_key
        self.group_name = group_name
        self.query_message_interval = query_message_interval
        self.heartbeat_interval = heartbeat_interval

        self.token = None

        self.ws = None
        self.connect()

        self.fire('on_init')
        self.on('on_handshake_success', self._start_query_loop)
        self.on('on_confirm_message', self._on_confirm_message)

    def create_sign(self, timestamp):
        timestamp = timestamp if timestamp else int(round(time.time() * 1000))
        params = {
            'group_name': self.group_name,
            'app_key': self.app_key,
            'timestamp': timestamp,
        }

        keys = list(params.keys())
        keys.sort()

        params = "%s%s%s" % (
            self.app_secret,
            ''.join('%s%s' % (key, params[key]) for key in keys),
            self.app_secret
        )
        return hashlib.md5(to_binary(params)).hexdigest().upper()

    def connect(self):
        websocket_connect(
            self.url,
            callback=self.on_open,
            on_message_callback=self.on_message
        )

    def close(self):
        logger.info('[%s:%s]TMC Connection Closing.', self.url, self.group_name)
        if self.ws:
            self.ws.close()

    def write_binary(self, message):
        self.ws.write_message(message, True)

    def on_open(self, future):
        self.ws = future.result()
        timestamp = int(round(time.time() * 1000))
        logger.info('[%s:%s]TMC Handshake Start.', self.url, self.group_name)

        params = {
            'timestamp': str(timestamp),
            'app_key': self.app_key,
            'sdk': 'top-sdk-java-201403304',
            'sign': self.create_sign(timestamp),
            'group_name': self.group_name,
        }

        message = writer(Message(2, 0, flag=1, content=params))
        self.write_binary(message)
        self.fire('on_open')

    def on_message(self, data):
        if data is None:
            logger.error('[%s:%s]TMC connection lost.', self.url, self.group_name)
            # reconnect
            # self.connect()

        message = None
        try:
            message = reader(data)
        except Exception:
            logging.exception('[%s:%s]Message Parse Error.', self.url, self.group_name)
            self.fire('parse_message_error')
            raise

        self.fire('received_message')
        logger.debug('[%s:%s]Recevied Message %s', self.url, self.group_name, message)

        if message.message_type == 1:  # 发送连接数据返回
            self.token = message.token
            logger.info('[%s:%s]TMC Handshake Success. The Token Is %s',
                        self.url, self.group_name, message.token)
            self.fire('on_handshake_success', token=self.token)
        elif message.message_type == 2:  # 服务器主动通知消息
            self.fire('on_confirm_message', message_id=message.content.get('id'))
            self.fire('on_message', message=message)
        elif message.message_type == 3:  # 主动拉取消息返回
            pass
        else:
            logger.error('[%s:%s]Unknown message recieved: %s',
                        self.url, self.group_name, message.message_type)

    def _on_confirm_message(self, message_id):
        cm = confirm_message(message_id, self.token)
        logger.debug('[%s"%s]Confirm Message: %s', self.url, self.group_name, message_id)
        self.write_binary(cm)

    def _start_query_loop(self, token=None):
        """ 开启主动拉取消息循环 """

        def _query_message_loop(self, url, group_name, token):
            def _():
                logger.debug('[%s:%s]Send Query Message Request.', url, group_name)
                self.write_binary(query_message(token=token))
            return _

        periodic = ioloop.PeriodicCallback(
            _query_message_loop(self, self.url, self.group_name, self.token),
            self.query_message_interval * 1000
        )

        logger.info('[%s:%s]Start Query Message Interval.', self.url, self.group_name)

        periodic.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ws = TmcClient('ws://mc.api.tbsandbox.com/', '1021700086', 'sandboxfd42495fa4db86f6ad1d4b878', 'default',
        query_message_interval=50)
    def print1():
        print('on_open')
    ws.on("on_open", print1)
    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass
    finally:
        ws.close()
