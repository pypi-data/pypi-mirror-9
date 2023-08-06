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
"""cubicweb-prov site customizations"""

from cubicweb.xy import xy


xy.register_prefix('prov', 'http://www.w3.org/ns/prov#')

xy.add_equivalence('Agent', 'prov:Agent')

xy.add_equivalence('Activity', 'prov:Activity')
xy.add_equivalence('Activity type', 'prov:type')
xy.add_equivalence('Activity description', 'prov:label')
xy.add_equivalence('Activity start', 'prov:startedAtTime')
xy.add_equivalence('Activity end', 'prov:endedAtTime')
xy.add_equivalence('Activity associated_with', 'prov:wasAssociatedWith')
xy.add_equivalence('Activity generated', 'prov:generated')
xy.add_equivalence('Activity used', 'prov:used')
