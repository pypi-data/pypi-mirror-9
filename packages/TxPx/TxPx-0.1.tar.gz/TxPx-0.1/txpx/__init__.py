"""
Robust process management for real-world application servers using Twisted

background(commandLine, protocol=EchoProcess, buffering=True)
-------------------------------------------------------------
Run commandLine as a subprocess in the background. Returns a deferred that
will fire (with the exit code, always 0 on Unix systems) or errback when the
process exits. Manage output streams and permit communication with the
process.

Using Twisted's builtin process tools it's hard to get a process which is able
to both communicate and log information to output streams.

It can also be hard to turn off buffering (necessary for immediate error
logging) and still be able to construct a linewise protocol to communicate
with the subprocess. This takes care of that, too.

The process will communicate with the parent process through a ProcessProtocol
class, which you can pass in. By default, this protocol is EchoProcess, which
echoes data to stdout and stderr respectively. You can safely subclass
EchoProcess and combine it with Tee() to get a process which both operates on
stdout and stdin as a protocol, and echoes those streams so the parent process
can include them in its logs.

>>> d = background("myproc")
>>> d.addErrback(log.err)
>>> d.addBoth(lambda x: println("ONO" + str(x)))

daycare and killall()
---------------------

When you run a subprocess using background(), its pid is added to the set
being maintained by the global object txpx.daycare. Call
txpx.killall() in scenarios where you need all child processes to die.

One example would be a scenario where you wish to re-exec the parent process;
exec doesn't kill children, so you might want to kill children before you call
exec().

You can also examine daycare, which is a set, and see what child processes are
still running.

registerLoggers(info, error, debug)
-----------------------------------
Add logging functions to use, other than print.

Tee()
-----
Utility to replace file-like objects with a similar object that writes to two
places at once. Indispensible for setting up debugging/tracing in subprocesses
that communicate using Twisted's ProcessProtocol mechanisms.

runner()
--------
Utility to eliminate very common boilerplate when using usage.Options() in
shell scripts.

Use:
In one of your library modules, define an Options class:

    $ echo > mylib/myoptions.py << EOF
    class MyOptions(usage.Options):
         "stuff"
    run = runner(MyOptions)
    EOF

In your bin/ directory, create an executable file:

    $ echo > bin/myprog << EOF
    #!/usr/bin/env python
    from sys import exit
    from mylib.myoptions import run
    exit(run())
    EOF
    $ chmod +x bin/myprog

Now you can import from your library module OR run it, cutting down on
maintenance. 

"""

from txpx.process import registerLoggers, daycare, killall, EchoProcess, background, Tee, runner

(registerLoggers, daycare, killall, EchoProcess, background, Tee, runner) # for pyflakes
