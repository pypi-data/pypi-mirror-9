"""
Some common utility functions for cli must be useful
"""
import sys
from cStringIO import StringIO
import shlex
import re
from contextlib import contextmanager
import os

from twisted.trial import unittest
from twisted.python import usage

from mock import patch

from aorta.cli import util


class FunTest(unittest.TestCase):
    def test_doc(self):
        """
        The doc function correctly extracts documentation
        """
        class Cls(object):
            """
            This is the first line of the docstring.

            There is more docstring, also.
            """

        self.assertEqual(util.doc(Cls), "This is the first line of the docstring.")

    def options(self, name='Options'):
        """
        Return a new instance of an Options for testing
        """
        class O(usage.Options):
            optFlags = [['hello', None, 'Say hello']]
            def parseArgs(self, *a):
                self['ret'] = ' '.join(a)

            def postOptions(self):
                if 'error' in self['ret']:
                    raise usage.UsageError("This is an error!")

                print self['ret']

        O.__name__ = name
        return O

    def test_runnerUnbuffered(self):
        """
        If asked, do I turn off buffering?
        """
        UO = self.options('UnbufferedOptions')

        pFDOpen = patch.object(os, 'fdopen')
        pArgv = patch.object(sys, 'argv', ('o',))

        pStdout = patch.object(sys, 'stdout')
        pStderr = patch.object(sys, 'stderr')

        with pStdout as mStdout, pStderr as mStderr, pFDOpen as mFDOpen, pArgv:
            util.runner(UO, buffering=False)(sys.argv)
            self.assertEqual(mFDOpen.call_count, 2)
            mFDOpen.assert_any_call(mStdout.fileno(), 'w', 0)
            mFDOpen.assert_any_call(mStderr.fileno(), 'w', 0)

    @contextmanager
    def patchIO(self):
        """
        Replace stdio streams with a single StringIO
        """
        io = StringIO()
        pStdout = patch.object(sys, 'stdout', io)
        pStderr = patch.object(sys, 'stderr', io)
        with pStdout, pStderr:
            yield io

    def test_runner(self):
        """
        The factory function runner() returns a run() that does command-line shit
        """
        O = self.options('O')

        pArgv = patch.object(sys, 'argv', ('o',))
        with self.patchIO() as io, pArgv:
            run = util.runner(O)

            argv = shlex.split("this is a sandwich")
            exitCode = run(argv)
            self.assertEqual(exitCode, 0)
            ret = io.getvalue().strip()
            self.assertEqual(ret, 'is a sandwich')

        with self.patchIO() as io, pArgv:
            argv = shlex.split("this is an error")
            exitCode = run(argv)
            self.assertEqual(exitCode, 1)
            ret = io.getvalue().strip()
            rx = re.compile(r'Say hello.*This is an error!', re.DOTALL)
            self.assertRegexpMatches(ret, rx)

        with self.patchIO() as io, pArgv:
            exitCode = run()
            self.assertEqual(exitCode, 0)
            ret = io.getvalue().strip()
            self.assertEqual(ret, '')
