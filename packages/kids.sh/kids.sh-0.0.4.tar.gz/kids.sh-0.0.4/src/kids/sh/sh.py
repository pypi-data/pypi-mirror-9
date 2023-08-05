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

    def __init__(self, msg, errlvl=None, command=None, out=None, err=None):
        self.errlvl = errlvl
        self.command = command
        self.out = out
        self.err = err
        super(ShellError, self).__init__(msg)


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

        >>> wrap('builtin lsdjflk') # doctest: +ELLIPSIS +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ...
        ShellError: Wrapped command '/tmp/lsdjflk' exited with errorlevel 127.
          stderr:
          | /bin/sh: .../tmp/lsdjflkjf: not found

    The command is passed as-is to the underlying default shell, so you can use
    builtins, pipes and all the machinery available in your shell::

        >>> print(wrap('echo hello | cat'),  end='')
        hello

    """

    out, err, errlvl = cmd(command, env=env)

    if errlvl not in ignore_errlvls:

        ## XXXvlab: shouldn't we include all this in the repr of ShellError
        ## so we could only raise the ShellError(namedtuple) ?
        formatted = []
        if out:
            if out.endswith('\n'):
                out = out[:-1]
            formatted.append("stdout:\n%s" % indent(out, "| "))
        if err:
            if err.endswith('\n'):
                err = err[:-1]
            formatted.append("stderr:\n%s" % indent(err, "| "))
        formatted = '\n'.join(formatted)

        raise ShellError("Wrapped command %r exited with errorlevel %d.\n%s"
                         % (command, errlvl,
                            indent(formatted, prefix="  ")),
                         errlvl=errlvl, command=command, out=out, err=err)
    return out.strip() if strip else out


def swrap(command, **kwargs):
    """Same as ``wrap(...)`` but strips the output."""

    return wrap(command, **kwargs).strip()


def set_env(**se_kwargs):

    def decorator(f):

        def _wrapped(*args, **kwargs):
            kwargs["env"] = dict(kwargs.get("env") or os.environ)
            for key, value in se_kwargs.items():
                if key not in kwargs["env"]:
                    kwargs["env"][key] = value
            return f(*args, **kwargs)
        return _wrapped
    return decorator
