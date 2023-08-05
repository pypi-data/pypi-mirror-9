
for step in rql('RecipeStep RS WHERE RS target %(target)s', {'target': u'apycot.get_dependancies'}).entities():
    step.cw_set(target=u'apycot.get_dependencies')

rql('DELETE Recipe R WHERE R name IN ("apycot.recipe.debian", "apycot.recipe.experimental")')

commit()
