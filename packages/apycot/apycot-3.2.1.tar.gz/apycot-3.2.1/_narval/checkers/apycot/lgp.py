import os
import logging
from glob import glob

import apycotlib as apycot
from checkers.apycot import BaseChecker, AbstractFilteredFileChecker

from logilab.devtools.lgp import *

class FilePath(object):
    def __init__(self, path, host=None, **kwargs):
        self.path = path
        self.host = host
        self.__dict__.update(kwargs)

class LgpLogHandler(logging.Handler):
    def __init__(self, writer):
        logging.Handler.__init__(self)
        self.writer = writer
        self.path = None
        self.status = apycot.SUCCESS

    def emit(self, record):
        if record.levelno >= logging.CRITICAL:
            f = self.writer.fatal
            self.status = apycot.FAILURE
        elif record.levelno >= logging.ERROR:
            f = self.writer.error
            self.status = apycot.FAILURE
        elif record.levelno >= logging.WARNING:
            f = self.writer.warning
        elif record.levelno >= logging.INFO:
            f = self.writer.info
        else:
            f = self.writer.debug
        message = record.getMessage()
        f(message, path=self.path)
        self.writer.refresh_log()


class LgpCheckChecker(BaseChecker):
    """run tests on a project with lgp"""

    id = 'lgp.check'
    command = 'check'
    options_def = {
    }

    def do_check(self, test):
        status = apycot.SUCCESS
        cwd = os.getcwd()
        os.chdir(test.project_path())
        cmd = LGP.get_command(self.command)
        self.writer.debug(cmd)
        handler = LgpLogHandler(self.writer)
        cmd.logger.addHandler(handler)
        exit_status = cmd.main_run(['-vv'], LGP.rcfile)
        if exit_status:
            self.writer.fatal('lgp %s exited with status %s', self.command, exit_status)
            self.set_status(apycot.ERROR)
        os.chdir(cwd)
        return handler.status

apycot.register('checker', LgpCheckChecker)

class LgpBuildChecker(BaseChecker):
    """build debian packages with lgp"""

    id = 'lgp.build'
    command = 'build'
    options_def = {
        'lgp_build_distrib': {
            'type': 'csv',
            'help': ('comma-separated list of distributions to build against'),
        },
        'lgp_sign': {
            'help': ('whether to sign packages'),
            'default': 'no',
        },
        'lgp_suffix': {
            'help': ('append vcs revision to the package version'),
        },
    }

    def display_logs(self, build_folder):
        self.writer.info('begin scanning for log files ')
        for filename in glob(os.path.join(build_folder, '*', '*.log')):
            if os.path.isfile(filename):
                log_file = open(filename, 'r')
                self.writer.info('printing {0}: {1}'.format(filename,
                    '\n'.join(list(log_file))))

    def do_check(self, test):
        dist = self.options.get('lgp_build_distrib') or ['all']
        sign = self.options.get('lgp_sign')
        suffix = self.options.get('lgp_suffix')
        build_folder = os.path.join(test.project_path(), '..')
        cwd = os.getcwd()
        os.chdir(test.project_path())
        repo = test.apycot_repository()
        try:
            handler = LgpLogHandler(self.writer)
            cmd = LGP.get_command(self.command)
            cmd.logger.addHandler(handler)
            args = ['-v', '-s', sign, '-d', ','.join(dist), '-r', build_folder ]
            if suffix:
                args += ['--suffix', '~rev%s' % repo.revision()]
            exit_status = cmd.main_run(args, LGP.rcfile)
            self.debian_changes = [f for f in cmd.packages if f.endswith('.changes')]
            if exit_status:
                self.writer.fatal('lgp %s exited with status %s', self.command, exit_status)
                self.set_status(apycot.ERROR)
        finally:
            if handler.status is not apycot.SUCCESS:
                self.display_logs(build_folder)
            os.chdir(cwd)
        return handler.status

apycot.register('checker', LgpBuildChecker)
