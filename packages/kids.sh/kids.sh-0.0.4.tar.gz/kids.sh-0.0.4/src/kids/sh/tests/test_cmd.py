# -*- encoding: utf-8 -*-
"""Testing Unittest facilities offered.


This doesn't test ``cmd`` command, but the ``self.cmd`` provided to
tests inheriting ``BaseShTest``.

"""


from . import BaseShTest
from .. import ShellError


class CmdSimpleTest(BaseShTest):

    def test_shell_call(self):
        res = self.cmd("true")
        self.assertEquals(res.out, "")
        self.assertEquals(res.err, "")
        self.assertEquals(res.errlvl, 0)

    def test_full_bash_construct(self):
        res = self.cmd("(false || true) && test -z "" > /dev/null")
        self.assertEquals(res.out, "")
        self.assertEquals(res.err, "")
        self.assertEquals(res.errlvl, 0)

    def test_fail(self):
        res = self.cmd("false")
        self.assertEquals(res.out, "")
        self.assertEquals(res.err, "")
        self.assertEquals(res.errlvl, 1)

    def test_fail_and_out_err_catching(self):
        res = self.cmd("echo -n 1 >&1 ; echo -n 2 >&2 ; exit 12")
        self.assertEquals(res.out, "1")
        self.assertEquals(res.err, "2")
        self.assertEquals(res.errlvl, 12)


class CmdEnvTest(BaseShTest):

    DEFAULT_ENV = {"MYVALUE": "XYXY"}

    def test_shell_env(self):
        res = self.cmd("echo -n $MYVALUE")
        self.assertEquals(res.out, "XYXY")

    def test_shell_inherit_main_process_env(self):
        import os
        os.environ["MYVALUE2"] = "ABAB"
        res = self.cmd("echo -n $MYVALUE2")
        self.assertEquals(res.out, "ABAB")
