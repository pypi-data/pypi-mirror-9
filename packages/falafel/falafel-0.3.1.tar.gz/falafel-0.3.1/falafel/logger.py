import sys
import logging
import datetime as dt

rank = ''
try:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    if comm.size > 1:
        rank = '-%02d- ' % comm.rank
except ImportError:
    pass


CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

logcolors = {
    CRITICAL: '31',  # critical/fatal
    ERROR:    '31;01',
    WARNING:  '33',
    WARN:     '33',
    INFO:     '32',
    DEBUG:    '35',
    NOTSET:    '0'
}

logcolorsextralen = {
    CRITICAL: 10,  # critical/fatal
    ERROR:    13,
    WARNING:  10,
    WARN:     10,
    INFO:     10,
    DEBUG:    10,
    NOTSET:    9
}

logbase = {
    CRITICAL: 'CRITICAL',  # critical/fatal
    ERROR:    'ERROR',
    WARNING:  'WARNING',
    WARN:     'WARN',
    INFO:     'INFO',
    DEBUG:    'DEBUG',
    NOTSET:   'BLANK'
}

def colorize(text, color):
    return "\x1b[%sm%s\x1b[00m" % (color, text)


mycolors = {k: colorize('|%9s | ' % v, logcolors[k])
            for k, v in logbase.items()}
mycolorscontline = {k: "\x1b[%sm| \x1b[00m" % v
                    for k, v in logcolors.items()}
nocolors = {k: "|%9s | " % (v) for k, v in logbase.items()}


class PercentStyle(object):

    default_format = '%(message)s'
    asctime_format = '%(asctime)s'
    asctime_search = '%(asctime)'

    def __init__(self, fmt):
        self._fmt = fmt or self.default_format

    def usesTime(self):
        return self._fmt.find(self.asctime_search) >= 0

    def format(self, record):
        return self._fmt % record.__dict__


class Formatter(logging.Formatter):
    # converter = dt.datetime.utcfromtimestamp
    converter = dt.datetime.fromtimestamp

    def __init__(self, *args, **kwargs):
        self.pre = kwargs.pop('pre', mycolors)

        # due to ansi escape sequences (len() returns differnt length if
        # string contains escape sequences)
        self.lenstrip = kwargs.pop('lenstrip', logcolorsextralen)

        # custom continuation line
        self.contline = kwargs.pop('contline', mycolorscontline)

        # output timestamps in log messages
        self.no_datetime = kwargs.pop('no_datetime', False)

        self.no_date = kwargs.pop('no_date', False)

        super(Formatter, self).__init__(*args, **kwargs)

        if self.no_date:
            self.datefmt = '%H:%M:%S.%f'
        else:
            self.datefmt = '%d %b %Y %H:%M:%S.%f'

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        s = ct.strftime(datefmt)[:-3]  # only show milliseconds
        return s

    def format(self, record):
        prefix = ''
        prefix_collen = 0
        lvlno = record.levelno
        if rank:
            prefix = rank
            # TODO use differnt colors for different ranks ??
            # TODO make colorized output optional
            if lvlno in logcolors:
                prefix = colorize(rank, logcolors[lvlno])
                prefix_collen = 10

        if not self.no_datetime:
            prefix += '[%(asctime)s] '

        self._fmt = (prefix + "%(name)-6s" +
                     self.pre.get(lvlno, ' unknown lvl') +
                     "%(message)s")
        if sys.version_info[0] > 2:
            self._style = PercentStyle(self._fmt)
            self._fmt = self._style._fmt
        logstr = logging.Formatter.format(self, record)
        # see http://www.velocityreviews.com/forums/t737197-re-python-logging-handling-multiline-log-entries.html
        # and see also
        # http://stackoverflow.com/questions/2186919/getting-correct-string-length-in-python-for-strings-with-ansi-color-codes
        try:
            header, _ = logstr.split(record.message)
            hlen = len(header) - 2  # -2 strips the last to chars needed to
                                    # add "| "
            if self.lenstrip is not None and lvlno in self.lenstrip:
                hlen -= self.lenstrip.get(lvlno, 0)
            hlen -= prefix_collen
            contline = '| ' if self.contline is None or \
                       lvlno not in self.contline else \
                       self.contline[lvlno]
            logstr = logstr.replace('\n', '\n' + ' ' * hlen + contline)
        except:
            pass
        return logstr
