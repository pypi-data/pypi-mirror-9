import os
from commands import getstatusoutput
from apycotlib import SUCCESS, FAILURE, ERROR
from apycotlib import register

from checkers.apycot import AbstractFilteredFileChecker

class ScriptRunner(AbstractFilteredFileChecker):
    """
    run files accepted by the filter
    """
    id = 'script_runner'
    def do_check(self, test):
        if self.options.get('filename_filter') is not None:
            self.filename_filter = self.options.get('filename_filter')
        super(ScriptRunner, self).do_check(test)

    def check_file(self, filepath):
        try:
            self.writer.debug("running : " + filepath, path=filepath)
            status, out = getstatusoutput(filepath)
            if status != 0:
                self.writer.error(out, path=filepath)
                return FAILURE
            self.writer.info(out, path=filepath)
            return SUCCESS
        except Exception, error:
            self.writer.error(error.msg, path=filepath)
            return ERROR

register('checker', ScriptRunner)


