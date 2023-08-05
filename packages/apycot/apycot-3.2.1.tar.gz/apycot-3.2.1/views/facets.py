"""some facets to filter test configurations / executions

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from cubicweb.predicates import is_instance
from cubicweb.web import facet

class TestConfigEnvFacet(facet.RelationFacet):
    __regid__ = 'apycot.tc.env'
    __select__ = facet.RelationFacet.__select__ & is_instance('TestConfig')
    rtype = 'use_environment'
    target_attr = 'name'

class TestConfigNameFacet(facet.AttributeFacet):
    __regid__ = 'apycot.tc.name'
    __select__ = facet.AttributeFacet.__select__ & is_instance('TestConfig')
    rtype = 'name'
    i18nable = False

class TestConfigStartModeFacet(facet.AttributeFacet):
    __regid__ = 'apycot.tc.startmode'
    __select__ = facet.AttributeFacet.__select__ & is_instance('TestConfig')
    rtype = 'computed_start_mode'

class TestConfigStartRevDepsFacet(facet.AttributeFacet):
    __regid__ = 'apycot.tc.startrev'
    __select__ = facet.AttributeFacet.__select__ & is_instance('TestConfig')
    rtype = 'start_rev_deps'


class TestExecutionStatusFacet(facet.AttributeFacet):
    __regid__ = 'apycot.te.status'
    __select__ = facet.AttributeFacet.__select__ & is_instance('TestExecution')
    rtype = 'status'
    order = 1

class TestExecutionConfigFacet(facet.RelationAttributeFacet):
    __regid__ = 'apycot.te.config'
    __select__ = facet.RelationFacet.__select__ & is_instance('TestExecution')
    rtype = 'using_config'
    target_attr = 'name'
    order = 2

class TestExecutionBranchFacet(facet.AttributeFacet):
    __regid__ = 'apycot.te.branch'
    __select__ = facet.AttributeFacet.__select__ & is_instance('TestExecution')
    rtype = 'branch'
    i18nable = False
    order = 3

#TODO bring this back with a slider widget
#class TestExecutionStarttimeFacet(facet.RQLPathFacet):
#    __regid__ = 'apycot.te.starttime'
#    __select__ = facet.RQLPathFacet.__select__ & is_instance('TestExecution')
#    order = 4
#    path = ['TI wf_info_for X', 'TI by_transition T', 'T name "start"', 'TI creation_date D']
#    filter_variable = 'D'

class TestExecutionArchiveFileFacet(facet.HasRelationFacet):
    __regid__ = 'apycot.te.archivefile'
    __select__ = facet.HasRelationFacet.__select__ & is_instance('TestExecution')
    rtype = 'execution_archive'
    order = 5
