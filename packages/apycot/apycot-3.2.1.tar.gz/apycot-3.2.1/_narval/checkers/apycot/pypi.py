#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import exists, join, abspath

import apycotlib

from checkers.apycot import BaseChecker
from preprocessors.apycot.distutils import pyversions

class PypiUploader(BaseChecker):
    id = 'pypi.upload'

    options_def = {
        'verbose': {
            'type': 'int', 'default': False,
            'help': 'set verbose mode'
            },
        }

    def do_check(self, test):
        """run the distutils 'setup.py register sdist upload' command

        The user running the narval bot must have a properly filled
        .pypirc file
        """
        path = test.project_path()
        if not exists(join(path, 'setup.py')):
            raise apycotlib.SetupException('No file %s' % abspath(join(path, 'setup.py')))
        python = pyversions(test)[0]
        cmdargs = [python, 'setup.py', 'register', 'sdist', 'upload']
        if not self.options.get('verbose'):
            cmdargs.append('--quiet')
        cmd = apycotlib.Command(self.writer, cmdargs, raises=True, cwd=path)
        cmdstatus = cmd.run()
        if cmdstatus == apycotlib.SUCCESS:
            self.writer.info('uploaded tarball to pypi')
        return cmdstatus

apycotlib.register('checker', PypiUploader)
