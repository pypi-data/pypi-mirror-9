"""subpackage containing base checkers (mostly for python code and packaging
standard used at Logilab)
"""

__docformat__ = "restructuredtext en"

from os import walk
from os.path import splitext, split, join

from logilab.common.textutils import splitstrip
from logilab.common.proc import RESOURCE_LIMIT_EXCEPTION

try:
    import apycotlib
except ImportError: # allow to run from sources
    from cubes.apycot import _apycotlib as apycotlib
    import sys
    sys.modules['apycotlib'] = apycotlib

from apycotlib import SUCCESS, NODATA, ERROR, TestStatus, ApycotObject

class BaseChecker(ApycotObject):
    id = None
    __type__ = 'checker'
    need_preprocessor = None

    _best_status = None

    def check(self, test):
        self.status = None
        try:
            setup_status = self.setup_check(test)
            self.set_status(setup_status)
            if setup_status is None or setup_status:
                self.set_status(self.do_check(test))
                self.version_info()
        finally:
            self.set_status(self.tear_down_check(test))
        # do it last to let checker do whatever they want to do.
        new_status = self.merge_status(self.status, self.best_status)
        if new_status is not self.status:
            self.writer.info("Configuration's setting downgrade %s checker status '\
                        'from <%s> to <%s>" , self.id, self.status, new_status)
            self.set_status(new_status)
        return self.status

    def _get_best_status(self):
        best_status = self._best_status
        if best_status is None:
            return None
        if not isinstance(best_status, TestStatus):
            best_status = TestStatus.get(best_status)
        return best_status

    def _set_best_status(self, value):
        if not isinstance(value, TestStatus):
            value = TestStatus.get(value)
        self._best_status = value

    best_status = property(_get_best_status, _set_best_status)

    def version_info(self):
        """hook for checkers to add their version information"""

    def do_check(self, test):
        """actually check the test"""
        raise NotImplementedError("%s must defines a do_check method" % self.__class__)

    def setup_check(self, test):
        pass

    def tear_down_check(self, test):
        pass


class AbstractFilteredFileChecker(BaseChecker):
    """check a directory file by file, with an extension filter
    """
    checked_extensions =  None
    options_def = {
        'ignore': {
            'type': 'csv', 'default': ['CVS', '.hg', '.git','.svn'],
            'help': 'comma separated list of files or directories to ignore',
            },
        }

    def filename_filter(self, dirpath, dirnames, filenames):
        """Prune unwanted directories from dirnames (in place) and remove
        unwanted files from filenames (inplace). The dirpath argument is provided to
        enable more complex dirname/filename matching.
        """
        for dirname in dirnames[:]:
            if self.ignored and join(dirpath,dirname).endswith(tuple(self.ignored)):
                dirnames.remove(dirname)
        for filename in filenames[:]:
            if not ((self.extensions is None or
                     filename.endswith(tuple(self.extensions))) and not
                     join(dirpath, filename).endswith(tuple(self.ignored))):
                filenames.remove(filename)

    def __init__(self, writer, options=None, extensions=None):
        super(AbstractFilteredFileChecker, self).__init__(writer, options)
        self.extensions = extensions or self.checked_extensions
        if isinstance(self.extensions, basestring):
            self.extensions = (self.extensions,)
        self._res = None
        self._safe_dir = set()

    def files_root(self, test):
        return test.project_path(subpath=True)

    def do_check(self, test):
        """run the checker against <path> (usually a directory)

        return true if the test succeeded, else false.
        """
        self.set_status(SUCCESS)
        self._nbanalyzed = 0
        self.ignored = self.options.get('ignore')
        files_root = self.files_root(test)
        self.writer.raw('file root', files_root)
        for dirpath, dirnames, filenames in walk(self.files_root(test)):
            #inplace pruning of dirnames and filenames
            self.filename_filter(dirpath, dirnames, filenames)
            for filename in filenames:
                try:
                    self.set_status(self.check_file(join(dirpath, filename)))
                except RESOURCE_LIMIT_EXCEPTION:
                    raise
                except Exception, ex:
                    self.writer.fatal(u"%s", ex, path=filename, tb=True)
                    self.set_status(ERROR)
                self._nbanalyzed += 1
        self.writer.raw('total files analyzed', self._nbanalyzed)
        if self._nbanalyzed <= 0:
            self.set_status(NODATA)
        return self.status

    def check_file(self, path):
        raise NotImplementedError()
