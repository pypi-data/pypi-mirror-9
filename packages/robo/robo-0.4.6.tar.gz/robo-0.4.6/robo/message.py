# -*- coding: utf-8 -*-
"""
    robo.message
    ~~~~~~~~~~~~

    Message.


    :copyright: (c) 2015 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""


class Message(object):
    def __init__(self, body, match, **kwargs):
        self.body = body
        self.match = match
        self.source = kwargs['source'] if 'source' in kwargs else None
        self.send_from = kwargs['send_from'] if 'send_from' in kwargs else None
        self.to = kwargs['send_to'] if 'send_to' in kwargs else None
        self.docs = kwargs['docs'] if 'docs' in kwargs else None
