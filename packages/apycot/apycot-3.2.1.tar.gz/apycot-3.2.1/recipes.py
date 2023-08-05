"""functions to create defaut apycot recipes"""

quick_script = u'''
from checkers.apycot import python # trigger registration
from apycotlib import narvalactions as na
# `plan`

with na.apycot_environment(plan) as test:
    na.install_environment(test)
    checker, status = test.run_checker('pyunit')
'''
def create_quick_recipe(session):
    return session.create_entity('Recipe', name=u'apycot.recipe.quick',
                                 script=quick_script)

full_script = u'''
from checkers.apycot import python # trigger registration
from apycotlib import registered, narvalactions as na
from apycotlib import ERROR
# `plan`

with na.apycot_environment(plan) as test:
    na.install_environment(test)
    if registered('checker', 'pylint'): # pylint may not be available
        checker, status = test.run_checker('pylint')
    checker, status = test.run_checker('pyunit', pycoverage=True)
    if status > ERROR:
        checker, status = test.run_checker('pycoverage',
                                            coverage_data=checker.coverage_data)

'''
def create_full_recipe(session):
    return session.create_entity('Recipe', name=u'apycot.recipe.full',
                                 script=full_script)

scenario_runner_script = u'''
from checkers.apycot.scenarios import ScriptRunner
from apycotlib import narvalactions as na

class ScenarioChecker(ScriptRunner):
    id = "scenario_checker"
    def filename_filter(self, dirpath, dirnames, filenames):
        """
        this function takes parameters from os.walk and has two objectives:
          - from the dirnames, prune folders you do not want to explore
            using dirnames.remove(x)
          - remove all the filenames which should not be run from filenames in
            the same way.
        """
        for dirname in dirnames[:]:
            if dirname in ('.hg', '.git', '.svn'):
                dirnames.remove(dirname)
        for filename in filenames[:]:
            if not (filename.endswith('.py') and filename.startswith('scenario_')):
                filenames.remove(filename)

register('checker', ScenarioChecker)

with na.apycot_environment(plan) as test:
    na.install_environment(test)
    checker, status = test.run_checker('scenario_checker')
'''

def create_scenrario_filter_recipe(session):
    return session.create_entity('Recipe', name=u'apycot.recipe.scenario_runner',
                                 script=scenario_runner_script)


pypi_script = u'''
# A simple recipe that uploads a project on pypi (if unit tests are OK)

from checkers.apycot import pypi # must be first (trigger registration)
from apycotlib import narvalactions as na
# `plan`

with na.apycot_environment(plan) as test:
    test.checkout(plan)
    checker, status = test.run_checker('pyunit')
    if status > ERROR:
        checker, status = test.run_checker('pypi.upload')
'''
