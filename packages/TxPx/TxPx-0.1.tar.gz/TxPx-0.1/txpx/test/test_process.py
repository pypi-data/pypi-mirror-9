"""
Test process spawning and utilities
"""
import sys
import re
import os
from contextlib import contextmanager
from cStringIO import StringIO
from tempfile import mkstemp
import shlex

from twisted.trial import unittest
from twisted.python import usage

from mock import patch, call

from txpx import process



class EchoProcessTest(unittest.TestCase):
    """
    Tests of the base process used by many of our tools
    """
    def test_io(self):
        """
        Do I capture I/O as it's thrown at me?
        """
        proto = process.EchoProcess(name='hello')

        pDebug = patch.object(process, 'log_debug')
        pError = patch.object(process, 'log_error')
        with pDebug as mDebug, pError as mError:
            proto.outReceived("asdf\nasdf\n")
            calls = mDebug.mock_calls
            self.assertEqual(calls, [
                call('<<< {name} stdout >>> {line}', name='hello', line='asdf'),
                call('<<< {name} stdout >>> {line}', name='hello', line='asdf'),
                ])

            proto.errReceived("** asdf\n** asdf\n")
            calls = mError.mock_calls
            self.assertEqual(calls, [
                call('*** {name} stderr *** {line}', name='hello', line='** asdf'),
                call('*** {name} stderr *** {line}', name='hello', line='** asdf'),
                ])

    def test_ioFiltered(self):
        """
        Do I filter I/O as it's thrown at me?
        """
        proto = process.EchoProcess(name='hello', 
                outFilter=lambda x: x.upper(),
                errFilter=lambda x: x.title()
                )

        pDebug = patch.object(process, 'log_debug')
        pError = patch.object(process, 'log_error')
        with pDebug as mDebug, pError as mError:
            proto.outReceived("asdf asdf\n")
            mDebug.assert_called_once_with('<<< {name} stdout >>> {line}', 
                    line='ASDF ASDF', name='hello')

            proto.errReceived("** asdf asdf\n")
            mError.assert_called_once_with('*** {name} stderr *** {line}',
                    line='** Asdf Asdf', name='hello')


class FnTest(unittest.TestCase):
    """
    Tests of top-level functions in process
    """
    def createProcessFixture(self, contents):
        """
        => Create an exe in the current dir and patch the PATH to find it
        """
        open('dummy', 'w').write('#!/bin/bash\n%s' % contents)
        self.addCleanup(os.remove, 'dummy')
        os.chmod('dummy', 0755)
        oldPath = os.environ['PATH']
        pPATH = patch.dict(os.environ, {'PATH': os.getcwd() + ':' + oldPath})
        pPATH.start()
        self.addCleanup(pPATH.stop)

    def test_backgroundGoodExit(self):
        """
        Do I spawn a dummy process through the reactor?
        """
        self.createProcessFixture('true')

        d = process.background('dummy')
        d.addCallback(self.assertEqual, 0)
        return d

    def test_backgroundBadExit(self):
        """
        If a job fails do I get an errback?
        """
        self.createProcessFixture('exit 19')

        d = process.background('dummy')
        d.addCallback(self.assertEqual, "fail")
        d.addErrback(lambda f: self.assertEqual(f.value.exitCode, 19))
        return d


class TeeTest(unittest.TestCase):
    """
    Does Tee really write to two files?
    """
    def setUp(self):
        io1 = self.io1 = StringIO()
        io2 = self.io2 = StringIO()
        self.tee = process.Tee(io1, io2)

    def test_write(self):
        """
        Do I write 2 time?
        """
        self.tee.write('wassup')
        self.assertEqual(self.io1.getvalue(), 'wassup')
        self.assertEqual(self.io2.getvalue(), 'wassup')

    def test_writeError(self):
        """
        If a file isn't writeable, do I write to the remaining file AND raise
        an exception?
        """
        _io1 = self.io1
        self.tee.file1 = open('/dev/zero', 'r')
        self.assertRaises(IOError, self.tee.write, 'wassup')
        self.assertRegexpMatches(self.io2.getvalue(), r'wassup.*File not open for writing')
        self.tee.file2 = self.tee.file1
        self.tee.file1 = _io1
        _io1.seek(0)
        _io1.flush()
        self.assertRaises(IOError, self.tee.write, 'wassup')
        self.assertRegexpMatches(self.io1.getvalue(), r'wassup.*File not open for writing')

    def test_flush(self):
        """
        Do I empty buffers?
        """
        (handle, path) = mkstemp()
        self.addCleanup(os.remove, path)
        self.tee.file1 = open(path, 'w')
        file1r = open(path, 'r')
        self.tee.file1.write('zz')
        self.assertEqual(file1r.read(), '')
        self.tee.flush()
        file1r.seek(0) # because mac os is dumb and not a real os
        self.assertEqual(file1r.read(), 'zz')


class DayCareTest(unittest.TestCase):
    """
    Tests that the DayCare object manages processes
    """
    def setUp(self):
        self.daycare = process.DayCare()

    def test_killall(self):
        """
        Do I attempt to kill all my child pids?
        """
        self.daycare.add(12345)
        self.daycare.add(45678)
        with patch.object(os, 'kill') as mKill:
            self.daycare.killall()
        
        mKill.assert_any_call(12345, 15)
        mKill.assert_any_call(45678, 15)


class FunTest(unittest.TestCase):
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
            process.runner(UO, buffering=False)(sys.argv)
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
            run = process.runner(O)

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
