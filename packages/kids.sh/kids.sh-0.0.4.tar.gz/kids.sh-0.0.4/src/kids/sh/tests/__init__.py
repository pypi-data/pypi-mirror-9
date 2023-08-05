# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import os

from kids.test import Test
from kids.cache import cache


class BaseShTest(Test):

    COMMAND = ""
    DEFAULT_ENV = {
    }

    @cache
    @property
    def cmd(self):
        from .. import cmd
        return set_env(**self.DEFAULT_ENV)(cmd)

    @cache
    @property
    def w(self):
        from .. import w
        return set_env(**self.DEFAULT_ENV)(w)
