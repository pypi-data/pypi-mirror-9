# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import locale
import textwrap
import collections

from subprocess import Popen, PIPE

from kids.txt import indent


ShellOutput = collections.namedtuple('ShellOutput', ["out", "err", "errlvl"])


class ShellError(Exception):

    def __init__(self, msg, command=None, env=None, outputs=None):
        self.command = command
        self.outputs = outputs
        self.env = env
        self.message = msg

    def __str__(self):
        out, err, errlvl = self.outputs
        formatted = []
        if "\n" in self.command:
            formatted.append("command:\n%s" % indent(self.command, "| "))
        else:
            formatted.append("command: %r" % self.command)
        formatted.append("errlvl: %d" % errlvl)
        if out:
            if out.endswith('\n'):
                out = out[:-1]
            formatted.append("stdout:\n%s" % indent(out, "| "))
        if err:
            if err.endswith('\n'):
                err = err[:-1]
            formatted.append("stderr:\n%s" % indent(err, "| "))
        formatted = '\n'.join(formatted)

        return "%s\n%s" % (self.message, indent(formatted, prefix="  "))


def cmd(command, env=None):
    """Execute a shell command and return (stdout, stdin, errlvl) tuple.

    This command is synchronous.

    """
    p = Popen(command, shell=True,
              stdin=PIPE, stdout=PIPE, stderr=PIPE,
              close_fds=True, env=env,
              universal_newlines=False)
    stdout, stderr = p.communicate()
    return ShellOutput(
        stdout.decode(locale.getpreferredencoding()),
        stderr.decode(locale.getpreferredencoding()),
        p.returncode)


def wrap(command, ignore_errlvls=[0], env=None, strip=True):
    """Execute a shell command and return stdout as a string

    Please note that it'll also cast an exception on unexpected errlvl::

        >>> wrap('builtin lsdjflk')  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ShellError: Wrapped command returned with unexpected errorlevel.
          command: 'builtin lsdjflk'
          errlvl: 127
          stderr:
          | /bin/sh: 1: builtin: not found


    The command is passed as-is to the underlying default shell, so you can use
    builtins, pipes and all the machinery available in your shell::

        >>> print(wrap('echo hello | cat'),  end='')
        hello

    """

    res = cmd(command, env=env)

    if res.errlvl not in ignore_errlvls:
        raise ShellError(
            msg="Wrapped command returned with unexpected errorlevel.",
            command=command, env=env, outputs=res)
    return res.out.strip() if strip else res.out


def swrap(command, **kwargs):
    """Same as ``wrap(...)`` but strips the output."""

    return wrap(command, **kwargs).strip()


def set_env(**se_kwargs):

    def decorator(f):

        def _wrapped(*args, **kwargs):
            kenv = kwargs.get("env", {})
            env = dict(kenv or os.environ)
            for key, value in se_kwargs.items():
                if key not in kenv:
                    env[key] = value
            kwargs["env"] = env
            return f(*args, **kwargs)
        return _wrapped
    return decorator
