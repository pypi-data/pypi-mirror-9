# copyright 2010-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.web.views import json
from cubicweb.predicates import is_instance, match_form_params


class GetDependencies(json.JsonEntityView):
    __regid__ = 'apycot.get_dependencies'
    __select__ = is_instance('TestExecution')

    def call(self):
        data = []
        for entity in self.cw_rset.entities():
            tconfig = entity.configuration
            env = entity.environment
            data.append(tconfig.dependencies(env) + [env])
        self.wdata(data)

class GetConfiguration(json.JsonEntityView):
    __regid__ = 'apycot.get_configuration'
    __select__ = is_instance('TestConfig') & match_form_params('environment')

    def call(self):
        data = []
        env = self._cw.entity_from_eid(self._cw.form['environment'])
        for tconfig in self.cw_rset.entities():
            data.append(tconfig.apycot_configuration(env))
        self.wdata(data)


