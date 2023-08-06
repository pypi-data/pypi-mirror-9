# -*- encoding: utf-8 -*-
"""Testing Unittest facilities offered.


This doesn't test 'wrap' command, but the 'self.w' provided to
tests inheriting BaseShTest.

"""


from .. import ShellError, BaseShTest


class WrapSimpleTest(BaseShTest):

    def test_shell_call(self):
        out = self.w("true")
        self.assertEquals(out, "")

    def test_full_bash_construct(self):
        out = self.w("(false || true) && test -z "" > /dev/null")
        self.assertEquals(out, "")

    def test_fail(self):
        self.assertRaises(ShellError, self.w, ("false", ))


class WrapEnvTest(BaseShTest):

    DEFAULT_ENV = {"MYVALUE": "XYXY"}

    def test_shell_env(self):
        out = self.w("echo $MYVALUE")
        self.assertEquals(out, "XYXY")

    def test_shell_inherit_main_process_env(self):
        import os
        os.environ["MYVALUE2"] = "ABAB"
        out = self.w("echo $MYVALUE2")
        self.assertEquals(out, "ABAB")
