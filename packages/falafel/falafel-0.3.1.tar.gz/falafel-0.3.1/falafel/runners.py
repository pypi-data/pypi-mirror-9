import logging
import unittest
import os
import sys
import inspect
import re

if sys.version_info[0] > 2:
    from io import StringIO
else:
    from StringIO import StringIO


from .redgreenrunner import RedGreenTextTestResult
from .redgreenrunner import RedGreenTextTestRunner
from .redgreenrunner import WARNING
from .redgreenrunner import FAIL
from .logger import Formatter
from .logger import nocolors


class ResultStream(object):

    def __init__(self, orig_stream):
        self.orig_stream = orig_stream
        self.logfile = None
        self.logger = None  # is set in the TestRunner class
        self.debug = False
        self.ansi_escape = re.compile(r'\x1b[^m]*m')
        self.nocolfmt = Formatter(pre=nocolors, lenstrip=None, contline=None)
        self.colfmt = Formatter()

    def flush(self):
        self.orig_stream.flush()
        if self.logfile:
            self.logfile.flush()

    def write(self, text):
        self.orig_stream.write(text)
        if self.logfile:
            self.logfile.write(self.ansi_escape.sub('', text))

    def before_test(self, logfilename, warnstream):
        if logfilename:
            self.logfile = open(logfilename, "w")
        if self.logger is None:
            return

        if self.debug:
            # write to orig_stream and to logfile (if specified)
            hdl = logging.StreamHandler(self)
            hdl.setFormatter(self.colfmt)
        elif self.logfile:
            # log messages are only written to the logfiles and to
            # orig-stream. The ansi escape sequences in the redgreentest
            # output get removed from the logfile (`self.ansi_escape`)
            hdl = logging.StreamHandler(self.logfile)
            hdl.setFormatter(self.nocolfmt)
        else:
            # no logfile output + no logger output to orig_stream. exception:
            # the warnings/errors summary at the end of each test is written
            # to orig_stream
            hdl = logging.NullHandler()
        self.logger.addHandler(hdl)
        hdl = logging.StreamHandler(warnstream)
        hdl.setLevel(logging.WARNING)
        hdl.setFormatter(self.nocolfmt)
        self.logger.addHandler(hdl)

    def after_test(self):
        if self.logfile:
            self.logfile.close()
            self.logfile = None

        if self.logger is None:
            return

        # handler for warnstream
        self.logger.removeHandler(self.logger.handlers[-1])
        # stream or nullhandler
        self.logger.removeHandler(self.logger.handlers[-1])


class ResultHandler(RedGreenTextTestResult):

    ipdb = False
    width = 80
    logdirectory = None

    def startTest(self, test):
        # increments the number of run tests counter
        unittest.TestResult.startTest(self, test)

        tname = '%s.%s' % (test.__class__.__name__, test._testMethodName)
        module = test.__class__.__module__
        desc = ' %s in %s ' % (tname, module)

        test.warningserrors = StringIO()
        
        logfile = None
        if self.logdirectory:
            test._logdir = self.logdirectory
            logfile = os.path.join(self.logdirectory,
                                   '%s.log' % (tname.replace('.', '_')))
        self.stream.before_test(logfile, test.warningserrors)
        self.stream.writeln(desc.center(self.width, '-'))
        self.stream.flush()

    def stopTest(self, test):
        if getattr(test, 'created_files', False):
            self.stream.writeln("Created files:")
            for fn in sorted(test.created_files):
                self.stream.writeln("\t%s" % fn)
        if getattr(test, 'data', False):
            self.stream.writeln("Created data:")
            for e in sorted(test.data.items()):
                self.stream.writeln("%s:\t%s" % e)

        warnings = test.warningserrors.getvalue()
        test.warningserrors.close()
        if len(warnings):
            self.stream.writeln("Errors and Warnings logged:", WARNING)
            s = warnings.split('\n')
            s = ('\t' + line for line in s)
            self.stream.writeln('\n'.join(s), WARNING)

        self.stream.writeln(self.separator2)
        self.stream.after_test()
        self.stream.writeln('')

    def addError(self, test, err):
        super(ResultHandler, self).addError(test, err)
        self.print_current_error()
        if self.ipdb:
            self.debug(err)

    def addFailure(self, test, err):
        super(ResultHandler, self).addFailure(test, err)
        self.print_current_failure()
        if self.ipdb:
            self.debug(err)

    def debug(self, err):
        import IPython
        ec, ev, tb = err
        stdout = sys.stdout
        sys.stdout = sys.__stdout__
        try:
            # The IPython API changed a bit so we should
            # support the new version
            if hasattr(IPython, 'InteractiveShell'):
                if hasattr(IPython.InteractiveShell, 'instance'):
                    shell = IPython.InteractiveShell.instance()
                    p = IPython.core.debugger.Pdb(shell.colors)
                else:
                    shell = IPython.InteractiveShell()
                    ip = IPython.core.ipapi.get()
                    p = IPython.core.debugger.Pdb(ip.colors)
            # and keep support for older versions
            else:
                shell = IPython.Shell.IPShell(argv=[''])
                ip = IPython.ipapi.get()
                p = IPython.Debugger.Pdb(ip.options.colors)

            p.reset()
            # inspect.trace() returns a list of frame information from this
            # frame to the one that raised the exception being treated
            frame, filename, line, func_name, ctx, idx = inspect.trace()[-1]
            p.interaction(frame, tb)
        finally:
            sys.stdout = stdout

    def print_current_error(self):
        cerr = self.errors[-1:]
        self.printErrorList('ERROR', cerr, WARNING)

    def print_current_failure(self):
        cfail = self.failures[-1:]
        self.printErrorList('FAIL', cfail, FAIL)

    def printErrors(self):
        # this prevents that all errors/failures a printed after all tests
        # were ran
        pass


class FalafelTestRunner(RedGreenTextTestRunner):

    def __init__(self, *args, **kwargs):
        """
        Parameters
        ----------
        logdirectory : str, optional
            If set, specifies the directory where all logfiles are stored.
            Otherwise, test output is only written to stdout.
        debug : bool
            Write debug log messages to stdout. Note that debug messages are
            per default written to the logfiles given that `logdirectory` was
            specified. Only has an effect if a python logger was set.
        logger : python logger instance, str, optional
        """
        # TODO add more kwargs to control the behavior of the ResultHandler
        # class and of the ResultStream class

        if 'stream' not in kwargs:
            kwargs["stream"] = ResultStream(sys.stderr)
        kwargs["resultclass"] = ResultHandler
        ResultHandler.logdirectory = kwargs.pop('logdirectory')
        if ResultHandler.logdirectory and not os.path.exists(
                ResultHandler.logdirectory):
            print("creating logdirectory: '%s'" % ResultHandler.logdirectory)
            os.makedirs(ResultHandler.logdirectory)

        logger = kwargs.pop('logger', None)
        if logger is not None and isinstance(kwargs['stream'], ResultStream):
            if isinstance(logger, str):
                logger = logging.getLogger(logger)
                logger.setLevel(logging.DEBUG)
                logger.propagate = False
            kwargs['stream'].logger = logger
            kwargs['stream'].debug = kwargs.pop('debug', False)

        super(FalafelTestRunner, self).__init__(*args, **kwargs)
