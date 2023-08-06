# coding: utf-8

from __future__ import unicode_literals


class Behavior(object):
    def __init__(self, db_session):
        super(Behavior, self).__init__()
        self._db_session = db_session
