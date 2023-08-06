"""
Implementation core of txpx
"""
import sys
import os
import signal
from os.path import basename
import shlex
import errno

from twisted.internet import protocol, reactor
from twisted.internet.error import ProcessDone, ProcessTerminated
from twisted.internet.defer import Deferred
from twisted.python import failure, usage
from twisted.python.procutils import which
from twisted.protocols import basic



def defaultLogger(message, **kw):
    print message.format(**kw)

log_info = log_error = log_debug = defaultLogger

def registerLoggers(info, error, debug):
    """
    Add logging functions to this module.

    Functions will be called on various severities (log, error, or debug
    respectively).

    Each function must have the signature:
        fn(message, **kwargs)

    If Python str.format()-style placeholders are in message, kwargs will be
    interpolated.
    """
    global log_info
    global log_error
    global log_debug

    log_info = info
    log_error = error
    log_debug = debug


class DayCare(set):
    """
    Give me your children to handle.

    If anyone wants to know who they are, I'll tell them.

    If you disappear, I'll kill them for you.
    """
    def killall(self):
        """
        Kill all children
        """
        for pid in set(self):
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError, e: # pragma: nocover
                if e.errno == errno.ESRCH:
                    "Process previously died on its own"
            self.remove(pid)

daycare = DayCare()
killall = daycare.killall


class EchoProcess(protocol.ProcessProtocol):
    """
    Run the process, and echo its output

    Pass in the name of the process being logged, and filters to apply to the
    logging (optional)
    """
    def __init__(self, name, outFilter=None, errFilter=None, deferred=None):
        self.name = name
        log_info("<<< {name} >>> Running.", name=name)
        self.outFilter = outFilter if outFilter else lambda x: x
        self.errFilter = errFilter if errFilter else lambda x: x
        self.lineReceiver = LineGlueProtocol(self)
        self.deferred = deferred

    def processEnded(self, reason):
        """
        Connected process shut down
        """
        log_debug("{name} process exited", name=self.name)
        if self.deferred:
            if reason.type == ProcessDone:
                self.deferred.callback(reason.value.exitCode)
            elif reason.type == ProcessTerminated:
                self.deferred.errback(reason)
        return self.deferred

    def outReceived(self, data):
        """
        Connected process wrote to stdout
        """
        self.lineReceiver.dataReceived(data)

    def errReceived(self, data):
        """
        Connected process wrote to stderr
        """
        lines = data.splitlines()
        for line in lines:
            log_error("*** {name} stderr *** {line}", 
                    name=self.name,
                    line=self.errFilter(line))

    def outLineReceived(self, line):
        """
        Handle data via stdout linewise. This is useful if you turned off
        buffering.

        In your subclass, override this if you want to handle the line as a
        protocol line in addition to logging it. (You may upcall this function
        safely.)
        """
        log_debug('<<< {name} stdout >>> {line}', 
                name=self.name,
                line=self.outFilter(line))


def background(cl, proto=EchoProcess, **kw):
    """
    Use the reactor to run a process in the background.

    Keep the pid around.

    ``proto'' may be any callable which returns an instance of ProcessProtocol
    """
    if isinstance(cl, basestring):
        cl = shlex.split(cl)

    if not cl[0].startswith('/'):
        path = which(cl[0])
        assert path, '%s not found' % cl[0]
        cl[0] = path[0]

    d = Deferred()
    proc = reactor.spawnProcess(
            proto(name=basename(cl[0]), deferred=d),
            cl[0],
            cl,
            env=os.environ,
            **kw)

    daycare.add(proc.pid)
    return d


class Tee(object):
    """
    Write to two files.
    """
    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2

    def write(self, *a, **kw):
        """
        Write to both files

        If either one has an error, try writing the error to the other one.
        """
        fl = None
        try:
            self.file1.write(*a, **kw)
            self.file1.flush()
        except IOError:
            badFile, fl = 1, failure.Failure()

        try:
            self.file2.write(*a, **kw)
            self.file2.flush()
        except IOError:
            badFile, fl = 2, failure.Failure()

        if fl:
            out = self.file2 if badFile == 1 else self.file1
            out.write(str(fl) + '\n')
            out.flush()
            fl.raiseException()

    def flush(self):
        """
        Empty buffers into the files
        """
        self.file1.flush()
        self.file2.flush()


def runner(Options, buffering=True):
    """
    Return a standard "run" function that wraps an Options class

    If buffering=False, turn off stdout/stderr buffering for this process
    """
    def run(argv=None):
        if not buffering:
            sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
            sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

        if argv is None:
            argv = sys.argv
        o = Options()
        try:
            o.parseOptions(argv[1:])
        except usage.UsageError, e:
            if hasattr(o, 'subOptions'):
                print str(o.subOptions)
            else:
                print str(o)
            print str(e)
            return 1

        return 0

    return run


class LineGlueProtocol(basic.LineReceiver):
    """
    Glue - helps your ProcessProtocol convert stdio data into a line-buffered
    protocol.
    """
    delimiter = '\n'
    MAX_LENGTH = 999

    def __init__(self, processProto): 
        self.processProto = processProto

    def lineReceived(self, line):
        self.processProto.outLineReceived(line)


