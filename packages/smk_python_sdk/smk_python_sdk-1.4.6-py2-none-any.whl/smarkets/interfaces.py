from __future__ import absolute_import, division, print_function, unicode_literals

from collections import namedtuple

from injector import Key

RedisConfiguration = namedtuple('RedisConfiguration', 'host port db')

Redis = Key('Redis')
