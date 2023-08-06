# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-vcreview facets to filter patches"""

__docformat__ = "restructuredtext en"

from rql import nodes

from cubicweb.web import facet
from cubicweb.predicates import is_instance

class PatchRepositoryFacet(facet.RQLPathFacet):
    __regid__ = 'vcreview.patch_repository'
    __select__ = is_instance('Patch')
    path = ['X patch_revision RE', 'RE from_repository R', 'R title T']
    title = 'Repository'
    filter_variable = 'R'
    label_variable = 'T'


class PatchReviewerFacet(facet.RelationFacet):
    __regid__ = 'vcreview.patch_reviewer'
    rtype = 'patch_reviewer'
    role = 'subject'
    target_attr = 'login'


class PatchAuthorFacet(facet.RQLPathFacet):
    __regid__ = 'vcreview.patch_author'
    __select__ = is_instance('Patch')
    title = 'Author'
    path = ['X patch_revision RE', 'RE author A']
    filter_variable = 'A'

class PatchBranchFacet(facet.RQLPathFacet):
    __regid__ = 'vcreview.patch_branch'
    __select__ = is_instance('Patch')
    title = 'Branch'
    path = ['X patch_revision RE', 'RE branch B']
    filter_variable = 'B'

class PatchCommitterFacet(facet.RelationFacet):
    __regid__ = 'vcreview.patch_committer'
    rtype = 'patch_committer'
    role = 'subject'
    target_attr = 'login'


class PatchHasTodoTask(facet.HasRelationFacet):
    """Filter out patches with todo tasks"""
    __regid__ = 'vcreview.open_task'
    __select__ = is_instance('Patch')
    title = _('has open task')

    def add_rql_restrictions(self):
        value = self._cw.form.get(self.__regid__)
        if not value: # no value sent for this facet
            return
        exists_node1 = nodes.Exists()
        exists_node2 = nodes.Exists()
        self.select.add_restriction(nodes.Or(exists_node1, exists_node2))
        self.fill_exists(exists_node1,
                         [('has_activity', 'subject'), ('in_state', 'subject')])
        self.fill_exists(exists_node2,
                         [('patch_revision', 'subject'), ('point_of', 'object'),
                          ('has_activity', 'subject'), ('in_state', 'subject')])

    def fill_exists(self, node, rtypes_roles):
        """Fill a node with relation restrictions from a sequence of rtypes
        and roles
        """
        pvar = self.filtered_variable
        for rtype, role in rtypes_roles:
            var = self.select.make_variable()
            if role == 'subject':
                node.add_relation(pvar, rtype, var)
            else:
                node.add_relation(var, rtype, pvar)
            pvar = var
        node.add_constant_restriction(pvar, 'name', 'todo', 'String')
