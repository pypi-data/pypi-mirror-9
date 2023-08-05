# postcreate script. You could setup a workflow here for example

wf = add_workflow(u'Test configuration workflow', 'TestConfig')
activated = wf.add_state(_('activated'), initial=True)
deactivated = wf.add_state(_('deactivated'))
wf.add_transition(_('deactivate'), activated, deactivated,
                  requiredgroups=('managers',))
wf.add_transition(_('activate'), deactivated, activated,
                  requiredgroups=('managers',))

# workflows don't consider schema inheritance, so we need to set it explicitly
rql('SET WF workflow_of TE, TE default_workflow WF WHERE WF workflow_of P, P name "Plan", TE name "TestExecution"')
commit()

from cubes.apycot import recipes
recipes.create_quick_recipe(session)
recipes.create_full_recipe(session)
commit()
