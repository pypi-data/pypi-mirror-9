import os
import os.path as osp
import subprocess
import shutil

from logilab.common.testlib import unittest_main
import cubicweb.devtools
import cubes.apycot.testutils as utils

from cubes.apycot.recipes import full_script

HERE = osp.abspath(osp.dirname(__file__))

import narvalbot
narvalbot._CW_SOURCES_FILE = osp.join(HERE, 'data', 'narval-cw-sources.ini')

os.environ['HGRCPATH'] = os.devnull

def setUpModule():
    ppath = osp.join(HERE, 'data', 'project')
    if osp.isdir(osp.join(ppath, '.hg')):
        shutil.rmtree(osp.join(ppath, '.hg'))
    subprocess.check_call(['hg', 'init', '-q', ppath])
    subprocess.check_call(['hg', 'addremove', '-q', '-R', ppath])
    subprocess.check_call(['hg', 'commit', '-q', '-R', ppath, '-m', 'ze rev', '-u', 'narval'])
    subprocess.check_call(['hg', 'phase', '-p', '.', '-q', '-R', ppath])

def tearDownModule():
    shutil.rmtree(osp.join(HERE, 'data', 'project', '.hg'))

class ApycotTC(utils.ApycotBaseTC):

    def test_quick_recipe(self):
        with self.admin_access.client_cnx() as cnx:
            lgc = cnx.entity_from_eid(self.lgc)
            lgce = cnx.entity_from_eid(self.lgce)
            te = lgc.start(lgce)
            cnx.commit()
            self.run_plan(te)
            self.assertEqual(dict((checker.name, checker.status) for checker in te.checkers),
                             {'pyunit': 'nodata'})

    def test_full_recipe(self):
        with self.admin_access.client_cnx() as cnx:
            lgce = cnx.entity_from_eid(self.lgce)
            recipe = cnx.execute('Recipe X WHERE X name "apycot.recipe.full"').get_entity(0, 0)
            # reset recipe content
            recipe.cw_set(script=full_script)
            tc = self.add_test_config(cnx, u'full config', env=self.lgce, group=self.pyp,
                                      use_recipe=recipe)
            te = tc.start(lgce)
            cnx.commit()
            self.run_plan(te)
            exp = {u'pycoverage': u'error', u'pyunit': u'nodata'}
            try:
                from pylint import checkers as pycheckers
                from pylint.lint import PyLinter
                from pylint.__pkginfo__ import version as pylint_version
                from pylint.interfaces import IReporter
                from pylint.reporters import BaseReporter
                exp['pylint'] = u'error'
            except:
                pass
            self.assertDictEqual(exp,
                                 dict((checker.name, checker.status) for checker in te.checkers),
                                 )

if __name__ == '__main__':
    unittest_main()
