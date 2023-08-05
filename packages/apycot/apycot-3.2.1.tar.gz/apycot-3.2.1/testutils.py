import sys
import shutil
import os
from datetime import datetime
from os.path import join, dirname, abspath

from logilab.common.testlib import mock_object

from cubicweb.devtools import BASE_URL
from cubicweb.devtools.testlib import CubicWebTC

from cubes.vcsfile.testutils import init_vcsrepo
from cubes.narval.testutils import NarvalBaseTC
from cubes.apycot.recipes import quick_script

try:
    import apycotlib
except:
    from cubes.apycot import _apycotlib as apycotlib
sys.modules['apycotlib'] = apycotlib

import narvalbot
if narvalbot.MODE == 'dev':
    PLUGINSDIR = join(dirname(__file__), '_narval')
else:
    from cubes.narval.__pkginfo__ import NARVAL_DIR
    PLUGINSDIR = join(narvalbot.INSTALL_PREFIX, NARVAL_DIR)
sys.path.append(PLUGINSDIR)

from apycotlib.writer import CheckDataWriter, BaseDataWriter


class DummyStack(object):

    def __init__(self):
        self.msg = None
        self.clear()

    def __getitem__(self, idx):
        return self

    def __len__(self):
        return 0

    def clear(self):
        self.msg = []
        self.append = self.msg.append


class MockBaseWriter(BaseDataWriter):

    def __init__(self):
        super(MockBaseWriter, self).__init__(MockConnection('narval0'), None)

    def skip(self, *args, **kwargs):
        pass

    def _debug(self, *args, **kwargs):
        print args, kwargs

    def set_exec_status(self, status):
        self._logs.append('<internal> SETTING EXEC STATUS: %s' % status)

    raw = execution_info = skip
    close = skip


class MockTestWriter(MockBaseWriter):
    """fake apycot.IWriter class, ignore every thing"""

    def make_check_writer(self):
        return MockCheckWriter()

    link_to_revision = MockBaseWriter.skip


class MockCheckWriter(MockBaseWriter):
    """fake apycot.IWriter class, ignore every thing"""

    def start(self, checker):
        self._logs.append('<internal>STARTING %s' % checker.id)

    def clear_writer(self):
        self._log_stack = DummyStack()


class MockTest(object):
    """fake apycot.Test.Test class"""
    def __init__(self, repo=None):
        self.repo = repo
        self.tmpdir = 'data'
        self.environ = {}
        self.checkers = []
        self._apycot_config = {}

    def project_path(self, subpath=False):
        return self.repo.co_path

    @property
    def tconfig(self):
        return mock_object(testconfig={}, name='bob', subpath=None)

    def apycot_config(self, something=None):
        return self._apycot_config


class MockVCSFile(dict):
    def __init__(self, _type, source_url=None, path=None):
        super(MockVCSFile, self).__init__(
                type=_type, source_url=source_url, path=path, local_cache=None)


class MockRepository:
    """fake apycot.IRepository class"""
    branch = None
    def __init__(self, attrs=None, **kwargs):
        self.__dict__.update(kwargs)
        self.co_path = self.path

    def co_command(self):
        return self.command

    def co_move_to_branch_command(self):
        return None

    def __repr__(self):
        return '<MockRepository %r>' % self.__dict__

    def revision(self):
        pass


class MockConnection(object):
    """fake HTTP handler"""
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.instance_url = BASE_URL

    def http_get(self, url, **params):
        pass
    def http_post(self, url, **params):
        pass
    def pending_plans(self):
        return ()
    def plan(self, eid):
        pass

class ApycotBaseTC(NarvalBaseTC):

    recipescript = quick_script

    def setup_database(self):
        """ self.repo: used to get the session to connect to cw
            self.vcsrepo: new entity
        """
        with self.admin_access.repo_cnx() as cnx:
            self.lgce = cnx.create_entity(
                'ProjectEnvironment', name=u'lgce',
                check_config=u'install=python_setup\nenv-option=value',
                check_environment=u'SETUPTOOLS=1\nDISPLAY=:2.0'
                ).eid
            self.vcsrepo = cnx.create_entity('Repository', type=u'mercurial',
                                             # use path to avoid clone attempt when using url
                                             source_url=u'file://' + unicode(self.datapath('project')),
                                             reverse_local_repository=self.lgce).eid
            self.pyp = cnx.create_entity('TestConfig', name=u'PYTHONPACKAGE',
                                         check_config=u'python_lint_treshold=7\n'
                                         'python_lint_ignore=thirdparty\n'
                                         'python_test_coverage_treshold=70\n',
                                         check_environment=u'NO_SETUPTOOLS=1\nDISPLAY=:1.0').eid
            self.recipe = cnx.execute('Recipe X WHERE X name "apycot.recipe.quick"')[0][0]
            # reset vcsrepo (using the session )
            init_vcsrepo(self.repo)
            # reset recipe content
            cnx.execute('SET X script %(script)s WHERE X eid %(recipe)s',
                        {'recipe': self.recipe,
                         'script': self.recipescript})
            self.lgc = self.add_test_config(cnx, u'lgc', env=self.lgce, group=self.pyp, use_recipe=self.recipe).eid
            cnx.commit()

            self.repo.threaded_task = lambda func: func() # XXX move to cw

    def add_test_config(self, cnx, name,
                        check_config=u'python_lint_treshold=8\npouet=5',
                        env=None, group=None, **kwargs):
        """add a TestConfig instance"""
        if group is not None:
            kwargs['refinement_of'] = group
        if env is not None:
            kwargs['use_environment'] = env
        return cnx.create_entity('TestConfig', name=name,
                                 check_config=check_config, **kwargs)

    def dumb_execution(self, cnx, ex, check_defs, setend=True):
        """add a TestExecution instance"""
        for name, status in check_defs:
            cr = cnx.create_entity('CheckResult', name=unicode(name), status=unicode(status))
            cnx.execute('SET X during_execution Y WHERE X eid %(x)s, Y eid %(e)s',
                        {'x': cr.eid, 'e': ex.eid})
        if setend:
            cnx.execute('SET X status "success" '
                        'WHERE X eid %(x)s', {'x': ex.eid})
