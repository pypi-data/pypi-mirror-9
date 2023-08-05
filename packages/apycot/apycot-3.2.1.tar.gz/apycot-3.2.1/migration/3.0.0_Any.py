# -*- coding: utf-8 -*-
from cubicweb import Binary
from cubicweb.server.session import Session

schema.rebuild_infered_relations()

# transform log into log_files
rename_relation_type('log_file','execution_archive')
add_relation_type('log_file')


eids = []
if confirm('Upgrade all log attributes to File objects (if you say no here, execution logs will be lost)?'):
    for i, (eid,) in enumerate(rql('Any X WHERE X is IN (TestExecution, CheckResult), NOT X log NULL')):
        data = rql('Any F WHERE X log F, X eid %(eid)s', {'eid': eid})[0][0]
        rql('INSERT File F: F data_name "log_file.txt", F data %(data)s, '
            'F data_encoding "utf-8", F data_format "text/plain", '
            'X log_file F WHERE X eid %(eid)s',
            {'data': Binary(data.encode('utf-8')), 'eid': eid})

        if not i%1000:
            print i, "..."
            commit(ask_confirm=False)
            print "OK"
    commit(ask_confirm=False)

drop_attribute('CheckResult', 'log')
drop_attribute('TestExecution', 'log')


sync_schema_props_perms('CheckResult')
sync_schema_props_perms('TestExecution')

from cubes.apycot import recipes
r_script_names = {
        u'apycot.recipe.quick': recipes.quick_script,
        u'apycot.recipe.full': recipes.full_script,
        u'apycot.recipe.scenario_runner': recipes.scenario_runner_script,
        }

warning_msg = """
### WARNING, THIS RECIPE SCRIPT WAS ADDED
### DURING A MIGRATION SCRIPT AND MIGHT
### NOT MATCH WHAT IS SHOWN IN THE LOGS
"""

for r_name in r_script_names:
    ## update script in recipe
    rql('SET X script %(script)s WHERE X is Recipe, X script "#to be updated", '
        'X name %(name)s',
        {'script': r_script_names[r_name],
         'name': r_name})
    ## update script for existing TestExecution and Chekresults
    rql('SET X script %(script)s WHERE X execution_of Y, Y name %(name)s',
        {'script': warning_msg + r_script_names[r_name],
         'name': r_name})


