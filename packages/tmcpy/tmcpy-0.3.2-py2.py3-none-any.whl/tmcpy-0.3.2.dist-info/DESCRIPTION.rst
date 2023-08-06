tmcpy
=======================

淘宝平台消息服务python版本

Usage:
```python
import logging

from tmcpy import TmcClient

logging.basicConfig(level=logging.DEBUG)

tmc = TmcClient('ws://mc.api.tbsandbox.com/', 'appkey', 'appsecret', 'default',
    query_message_interval=50)


def print1():
    print 'on_open'


tmc.on("open", print1)
try:
    ioloop.IOLoop.instance().start()
except KeyboardInterrupt:
    pass
finally:
    tmc.close()
```



