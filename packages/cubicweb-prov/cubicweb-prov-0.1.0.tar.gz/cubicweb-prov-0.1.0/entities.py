# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-prov entity's classes"""

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.view import EntityAdapter
from cubicweb.predicates import relation_possible


class Activity(AnyEntity):
    __regid__ = 'Activity'
    fetch_attrs, cw_fetch_order = fetch_config(('start', 'end', 'type',
                                                'description', 'description_format'),
                                               order='DESC')


class IRecordable(EntityAdapter):
    """Adapter for entities whose changes should be recorded using prov's Activity"""
    __regid__ = 'IRecordable'
    __select__ = relation_possible('generated', role='object')

    def add_activity(self, **kwargs):
        """Return a new Activity with `generated` and `used` relations on this Entity.
        """
        kwargs.setdefault('used', self.entity)
        kwargs.setdefault('generated', self.entity)
        return self._cw.create_entity('Activity', **kwargs)
