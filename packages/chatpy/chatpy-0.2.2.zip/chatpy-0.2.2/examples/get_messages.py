# chatpy
# Copyright 2013-2015 aqn
# See LICENSE for details.
# coding:utf-8
from __future__ import unicode_literals
from chatpy import API, TokenAuthHandler
token = 'bc7a5db63354b524b251381f58a6be64'

auth = TokenAuthHandler(token)
api = API(auth)
me = api.me()
rooms = api.rooms()
print rooms[0]