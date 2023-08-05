# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from .sh import wrap, cmd, ShellError, swrap, set_env


from kids.test import Test
from kids.cache import cache


class BaseShTest(Test):

    COMMAND = ""
    DEFAULT_ENV = {
    }

    @cache
    @property
    def cmd(self):
        return set_env(**self.DEFAULT_ENV)(cmd)

    @cache
    @property
    def w(self):
        return set_env(**self.DEFAULT_ENV)(wrap)

