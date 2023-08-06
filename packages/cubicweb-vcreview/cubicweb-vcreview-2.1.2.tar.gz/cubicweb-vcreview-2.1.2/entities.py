# copyright 2011-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-vcreview entity's classes"""

from datetime import datetime

from logilab.common.decorators import monkeypatch

from cubicweb.entities import AnyEntity
from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance

from cubes.comment import entities as comment
from cubes.task import entities as task

from cubes.vcreview import users_by_author

class InsertionPoint(AnyEntity):
    __regid__ = 'InsertionPoint'
    @property
    def parent(self):
        return self.point_of[0]

_TIP_MOST_REVS = ('Any TIP, H '
                  'ORDERBY H ASC, TIP DESC'
                  'WHERE P eid %(p)s, '
                  '      P patch_revision TIP, '
                  '      TIP hidden H, '
                  '      NOT EXISTS(R obsoletes TIP, '
                  '                 P patch_revision R)')

class Patch(AnyEntity):
    __regid__ = 'Patch'

    def dc_title(self):
        return self.patch_name

    @property
    def repository(self):
        return self.patch_revision[0].from_repository[0]

    @property
    def revisions(self):
        return sorted(self.patch_revision, key=lambda x: x.revision)

    def patch_files(self):
        return set(vc.file.path for vc in self.patch_revision)

    def tip(self):
        return self._cw.entity_from_eid(self.all_tips()[0][0])

    def all_tips(self):
        return list(self._cw.execute(_TIP_MOST_REVS, {'p': self.eid}))

    final_states = set( ('folded', 'applied', 'rejected') )

    @property
    def is_final(self):
        return self.cw_adapt_to('IWorkflowable').state in self.final_states

    def email_export(self, size=None):
        """Return an export of patch possibly truncated at `size` for email
        embedding.
        """
        patch = self.tip().export().decode(self.repository.encoding, 'replace')
        if size is not None and len(patch) > size:
            patch = patch[:size] + '\n@@ truncated patch @@'
        return patch


@monkeypatch(task.Task, 'activity_of')
@property
def activity_of(self):
    return self.reverse_has_activity and self.reverse_has_activity[0]


@monkeypatch(task.Task, 'patch')
@property
def patch(self):
    """The patch associated with this Task"""
    concerned = self.activity_of
    if not concerned:
        return None
    if concerned.cw_etype == 'Patch':
        return concerned
    else:
        return concerned.point_of[0]


class CommentITreeAdapter(comment.CommentITreeAdapter):
    def path(self):
        path = super(CommentITreeAdapter, self).path()
        rootrset = self._cw.eid_rset(path[0])
        if rootrset.description[0][0] == 'InsertionPoint':
            path.insert(0, rootrset.get_entity(0, 0).parent.eid)
        return path


class PatchReviewBehaviour(EntityAdapter):
    __regid__ = 'IPatchReviewControl'
    __select__ = is_instance('Patch')

    def reviewers_rset(self):
        # ensure patch author can't review his own patch
        return self._cw.execute(
            'Any U, MAX(D) GROUPBY U '
            'WHERE P eid %(p)s, '
            '      P patch_revision RE, '
            '      RE from_repository R, '
            '      NOT P created_by U, '
            '      U in_state S, NOT S name "deactivated", '
            '      X? patch_reviewer U, '
            '      X creation_date D, '
            '      EXISTS(R use_global_groups TRUE, U in_group G, G name "reviewers") '
            '      OR EXISTS(R repository_reviewer U)',
            {'p': self.entity.eid})

    def set_reviewers(self):
        if self.entity.patch_reviewer:
            return
        # look for patch authors, so we don't ask them to review their own patch
        authors = set()
        for rev in self.entity.patch_revision:
            authors.update(users_by_author(self._cw.execute, rev.author))

        for ueid,_ in sorted(self.reviewers_rset(), key=lambda row: row[1] or datetime.min):
            if ueid in authors:
                continue
            self._cw.execute('SET P patch_reviewer U WHERE P eid %(p)s, U eid %(u)s',
                             {'p': self.entity.eid, 'u': ueid})
            break


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (CommentITreeAdapter,))
    vreg.register_and_replace(CommentITreeAdapter, comment.CommentITreeAdapter)
