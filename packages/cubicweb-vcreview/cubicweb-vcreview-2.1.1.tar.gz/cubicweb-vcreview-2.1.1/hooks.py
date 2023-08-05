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
"""cubicweb-vcreview specific hooks and operations"""

__docformat__ = "restructuredtext en"

import binascii
import os.path as osp
from email.Utils import parseaddr

from cubicweb import RegistryException
from cubicweb.server import hook
from cubicweb.predicates import is_instance, on_fire_transition, has_related_entities
from cubicweb.hooks import notification

from cubes.vcsfile.entities.adapters import HGRepo
from cubes.vcreview import users_by_author, compare_patches

HGRepo.configs = ['extensions.pruned=%s/hgext/pruned.py' % osp.dirname(__file__),
                  'diff.unified=5']

def dead_revision(rev):
    # check more than hidden to protect against instability (e.g. obsolete
    # draft with alive children)
    if rev.hidden:
        return True
    if rev.phase == 'public':
        return False
    return bool(rev.reverse_obsoletes)


class PhaseUpdate(hook.Hook):
    """detect phase/visibility changes to a changeset"""
    __regid__ = 'vcreview.phase'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_update_entity',)

    def __call__(self):
        repo = self.entity.repository
        if getattr(repo, 'has_review', False): # not there during migration
            rev = self.entity
            if rev.cw_edited.get('phase') == 'public':
                operation = AttachToPatchesOp.get_instance(self._cw)
                operation.add_data((repo.eid, rev.eid))
            elif (rev.cw_edited.get('hidden', False)
                  and rev.reverse_patch_revision):
                patch = rev.reverse_patch_revision[0]
                operation = PatchLifeCheckOp.get_instance(self._cw)
                operation.add_data((repo.eid, patch.eid, rev.eid))


class RevisionAdded(hook.Hook):
    """detect new revision"""
    __regid__ = 'vcreview.auto-link-to-patch'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_add_entity',)

    def __call__(self):
        repo = self.entity.repository
        if getattr(repo, 'has_review', False): # not there during migration
            operation = AttachToPatchesOp.get_instance(self._cw)
            operation.add_data((repo.eid, self.entity.eid))


class RevisionObsoleteHook(hook.Hook):
    """detect new obsolete revision"""
    __regid__ = 'vcreview.obsolete_rev'
    __select__ = hook.Hook.__select__ & hook.match_rtype('obsoletes')
    events = ('after_add_relation',)

    def __call__(self):
        rev = self._cw.entity_from_eid(self.eidfrom)
        if rev.reverse_patch_revision:
            return
        repo = rev.repository
        if getattr(repo, 'has_review', False):
            operation = AttachToPatchesOp.get_instance(self._cw)
            operation.add_data((repo.eid, rev.eid))


class RevisionDeleted(hook.Hook):
    """When deleting a revision, delete the associated patch if it has
    no other revisions
    """
    __regid__ = 'vcreview.revision_gone'
    __select__ = (hook.Hook.__select__ & is_instance('Revision') &
                  has_related_entities('patch_revision', role='object'))
    events = ('before_delete_entity',)

    def __call__(self):
        patch = self.entity.reverse_patch_revision[0]
        DeletedRevisionCheckOp.get_instance(self._cw).add_data(patch.eid)


class AttachToPatchesOp(hook.DataOperationMixIn, hook.LateOperation):
    """Attach new revision to a Patch entity

    Create new Patches as necessary.
    """
    def precommit_event(self):
        for eid_repo, eid_rev in sorted(self.get_data()):
            # sorted for topological ordering
            # Helps to have more correct result (but no guarantee)
            repo = self.cnx.entity_from_eid(eid_repo)
            rev = self.cnx.entity_from_eid(eid_rev)
            operation = PatchLifeCheckOp.get_instance(self.cnx)
            patch = None
            if rev.reverse_patch_revision:
                patch = rev.reverse_patch_revision[0]
            else:
                patches = self.related_patch(rev)
                if patches:
                    patch = patches[0]
                    rev.cw_set(reverse_patch_revision=patch.eid)
                    for folded in patches[1:]:
                        operation.add_data((repo.eid, folded.eid, rev.eid))
                elif rev.phase != 'public':
                    patch = self.create_patch(rev)
            if patch is not None:
                # none if new public revison spawn unrelated to any patch
                users = users_by_author(self.cnx.execute, rev.author)
                if users:
                    self.cnx.execute('SET P owned_by U WHERE P eid %%(p)s, U eid IN (%s), NOT P owned_by U' %
                                     ','.join([str(u) for u in users]),
                                     {'p': patch.eid})
                operation.add_data((repo.eid, patch.eid, rev.eid))

    def related_patch(self, rev):
        patches = []
        for prec in sorted(rev.obsoletes, key=lambda e: e.eid):
            if prec.reverse_patch_revision:
                patch = prec.reverse_patch_revision[0]
                if patch.is_final:
                    continue
                # is every revision dead?
                tip = patch.tip()
                dead_tip = True
                if tip is None or dead_revision(tip):
                    patches.append(patch)
                else:
                    msg = '%s: %s not attached to Patch %i. %s is still alive'
                    self.info(msg, rev.repository.dc_title(),
                                   rev.changeset,
                                   patch.eid,
                                   tip.changeset)

        return patches


    def create_patch(self, rev):
        name = (rev.description.splitlines() or [rev.dc_title()])[0]
        kwargs = {'patch_name': name, 'patch_revision': rev}
        users = users_by_author(self.cnx.execute, rev.author)
        if users:
            kwargs['created_by'] = users[0]
        patch = self.cnx.create_entity('Patch', **kwargs)
        msg = '%s: New patch %i for new draft revision %s'
        self.info(msg, rev.repository.dc_title(), patch.eid, rev.changeset)
        return patch


class DeletedRevisionCheckOp(hook.DataOperationMixIn, hook.Operation):
    """Delete patches with no remaining revision"""
    def precommit_event(self):
        for patch_eid in self.get_data():
            rset = self.cnx.execute(
                    'DELETE Patch P WHERE P eid %(eid)s,'
                    '                     NOT EXISTS(P patch_revision R)',
                    {'eid': patch_eid})
            if rset:
                self.info('Deleted patch %s, no revisions left', rset[0][0])


class PatchLifeCheckOp(hook.DataOperationMixIn, hook.SingleLastOperation):
    """Put patches in the right state

    invoke it with:

        (repository-eid, patch-eid, revision-eid)

    The revision has "some new activity" and is related to the patch.  There is
    usually a PATCH patch_revision REVISION relation between them except in the
    folded case.
    """

    FOLDED = ('Any OLD '
              'WHERE P eid %(p)s, '
              '      R eid %(r)s, '
              '      NOT P patch_revision R, '
              '      P patch_revision OLD, '
              '      R obsoletes OLD')

    def precommit_event(self):
        cnx = self.cnx
        for eid_repo, eid_patch, eid_rev in sorted(self.get_data()):
            patch = cnx.entity_from_eid(eid_patch)
            wfable = patch.cw_adapt_to('IWorkflowable')
            ### Case 1: patch is already in final state
            # nothing to be done on it anymore
            if patch.is_final:
                continue
            rev = cnx.entity_from_eid(eid_rev)
            assert rev.reverse_patch_revision
            ### Case 2: patch has just been applied
            if (rev.phase == 'public'
                and rev.reverse_patch_revision[0].eid == patch.eid):
                # there is one applied version related to this patch
                wfable.fire_transition('apply', u'applied as %s'
                                       % rev.changeset)
                continue
            # get the patch's tips
            data = {'p': eid_patch, 'r': rev.eid}
            tips_rset = patch.all_tips()
            visible_tips = set(r[0] for r in tips_rset if not r[1])
            if visible_tips:
                # pre-existing revisions are likely just set to hidden=True
                # in this transaction. We do not want them to affect patch
                # state if we have a new visible tip (or even newer revision).
                if not (cnx.added_in_transaction(eid_rev)
                        or eid_rev in visible_tips):
                    continue
                same_patch, ancestor = self.compare_with_ancestor(
                    rev, wfable.state)
                if same_patch:
                    continue
                ### Case 3: new version of the patch
                name = (rev.description.splitlines() or [rev.dc_title()])[0]
                if name != patch.patch_name:
                    patch.cw_set(patch_name=name)
                name, email = parseaddr(rev.author)
                auto = cnx.execute('Any V WHERE U primary_email E, '
                                   'E address ILIKE %(email)s, '
                                   'P for_user U, '
                                   'P pkey "vcreview.autoreview", '
                                   'P value V',
                                   {'email': email.decode('ascii')})
                # defaults to auto ask review
                autoreview = auto and auto[0][0] == "1"
                if autoreview:
                    if wfable.state != 'pending-review':
                        wfable.fire_transition('ask review', u'new version %s'
                                               % rev.changeset)
                else:
                    if wfable.state == 'outdated':
                        wfable.fire_transition('reopen', u'new version %s'
                                               % rev.changeset)
                    elif wfable.state == 'reviewed':
                        msg = u'new version %s' % rev.changeset
                        if ancestor is not None:
                            msg += u' (different from :eid:`%d:%s`)' % (
                                    ancestor.eid, ancestor.changeset)
                        wfable.fire_transition('ask review', msg, u'text/rest')
            # patch has no visible tip
            elif cnx.execute(self.FOLDED, data):
                ### Case 4: Patch is now folded somewhere else
                wfable.fire_transition('fold', u'folded into %s'
                                       % rev.changeset)
            else:
                # all tips are hidden otherwise we would have walked in the
                # visible_tips conditional
                if eid_rev not in set(r[0] for r in tips_rset):
                    # we do not care about this revision
                    continue
                if rev.reverse_obsoletes:
                    # the patch will need a fold later
                    continue
                repo = cnx.entity_from_eid(eid_repo)
                succ = None
                for tip_eid, _ in tips_rset:
                    tip = cnx.entity_from_eid(tip_eid)
                    succ = self.has_successors(repo, tip)
                    if succ:
                        break
                if not succ:
                    ### Case 5: All tips are plain pruned. reject
                    wfable.fire_transition('reject', u'all versions pruned')
                elif wfable.state != 'outdated':
                    ### Case 6: Patch has a new version somewhere else
                    msg = u'outdated'
                    wfable.fire_transition('obsolete', msg)

    def has_successors(self, repo, rev):
        """return true if there is a final successor recorded in evolution history"""
        with repo.cw_adapt_to('VCSRepo').hgrepo() as localrepo:
            return bool(localrepo.log(revrange='%s and not pruned()' % rev.changeset))

    def compare_with_ancestor(self, rev, patch_state):
        """Compare specified revision with its most recent ancestor and return
        (True, None) if they are similar else (False, ancestor). If the
        revision has no ancestor, (False, None) is returned.

        TODO: this only works when the current patch state is not "outdated",
        though it might make sense to restore outdated patches in their
        previous state.
        """
        rset = self.cnx.execute('Any R ORDERBY MD DESC LIMIT 1 WHERE'
                                ' X obsoletes R, R modification_date MD,'
                                ' X eid %(x)s', {'x': rev.eid})
        if rset:
            if patch_state in ('in-progress', 'pending-review', 'reviewed'):
                ancestor = rset.get_entity(0, 0)
                if not compare_patches(ancestor.export(), rev.export()):
                    return False, ancestor
                return True, None
        return False, None


class InitPatchCreatorHook(hook.Hook):
    """automatically add people to nosy list

    Revision added to a patch should add the author to nosy list if it's known.

    This is done by searching author's email, then searching for a user
    associated to this email.
    """
    __regid__ = 'vcreview.auto-nosy'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_revision')
    events = ('after_add_relation',)
    category = 'metadata'

    def __call__(self):
        patch = self._cw.entity_from_eid(self.eidfrom)
        author = self._cw.entity_from_eid(self.eidto).author
        ueids = users_by_author(self._cw.execute, author)
        for ueid in ueids:
            self._cw.execute(
                'SET P nosy_list U WHERE P eid %(p)s, U eid %(u)s,'
                'NOT P nosy_list U', {'p': patch.eid, 'u': ueid})
        # legacy code about created by. dropped for now.
        # self._cw.add_relations([('created_by', relations),
        #                         ('owned_by', relations)])




class SetReviewerHook(hook.Hook):
    """register an operation to set a reviewer when the 'ask review' transition
    is fired
    """
    __regid__ = 'vcreview.set-reviewer'
    __select__ = hook.Hook.__select__ & on_fire_transition('Patch', 'ask review')
    events = ('after_add_entity',)

    def __call__(self):
        SetReviewerOp.get_instance(self._cw).add_data(self.entity)


class SetReviewerOp(hook.DataOperationMixIn, hook.Operation):

    def precommit_event(self):
        for trinfo in self.get_data():
            patch = trinfo.for_entity
            patch.cw_adapt_to('IPatchReviewControl').set_reviewers()


class ReviewerSetHook(hook.Hook):
    """send a notification when a user is assigned to review a patch and ensure
    he is in the patch nosy-list
    """
    __regid__ = 'vcreview.reviewer-set'
    __select__ = hook.Hook.__select__ & hook.match_rtype('patch_reviewer')
    events = ('after_add_relation',)

    def __call__(self):
        # send notification
        rset = self._cw.eid_rset(self.eidfrom)
        try:
            view = self._cw.vreg['views'].select(
                'vcreview.notifications.reviewer-set', self._cw,
                rset=rset, user=self._cw.eid_rset(self.eidto).get_entity(0, 0))
        except RegistryException:
            # view unregistered or unselectable
            return
        notification.notify_on_commit(self._cw, view=view)
        # ensure user is in the nosy-list
        self._cw.execute('SET P nosy_list U '
                         'WHERE P eid %(p)s, U eid %(u)s, NOT P nosy_list U',
                         {'p': self.eidfrom, 'u': self.eidto})


class AddTaskAuthorToPatchNosylistHook(hook.Hook):
    """Add the author of a task to the patch's nosylist"""
    __regid__ = 'vcreview.add-task-author-to-patch-nosylist'
    __select__ = (hook.Hook.__select__ &
                  hook.match_rtype('has_activity'))
    events = ('after_add_relation',)

    def __call__(self):
        patch = self._cw.entity_from_eid(self.eidto).patch
        AddUserToPatchNosyListOp.get_instance(self._cw).add_data(
            (patch.eid, self.eidto))


class AddTaskCommenterToPatchNosylistHook(hook.Hook):
    """Add users commenting a task to the patch's nosylist"""
    __regid__ = 'vcreview.add-task-commenter-to-patch-nosylist'
    __select__ = (hook.Hook.__select__ &
                  hook.match_rtype('comments', toetypes=('Task', 'Comment')))
    events = ('after_add_relation',)

    def __call__(self):
        comment = self._cw.entity_from_eid(self.eidfrom)
        comment_root = comment.cw_adapt_to('ITree').root()
        if comment_root.cw_etype != 'Task':
            return
        patch = comment_root.patch
        if not patch:
            return
        # `created_by` relation may not be set, so proceed in an operation
        AddUserToPatchNosyListOp.get_instance(self._cw).add_data(
            (patch.eid, comment.eid))


class AddUserToPatchNosyListOp(hook.DataOperationMixIn, hook.Operation):
    """Add the creator of a task/comment to the patch nosylist"""

    def precommit_event(self):
        for patch_eid, task_or_comment_eid in self.get_data():
            self.cnx.execute('SET P nosy_list U '
                             'WHERE P eid %(p)s, NOT P nosy_list U,'
                             '      TC created_by U, TC eid %(tc)s',
                             {'p': patch_eid, 'tc': task_or_comment_eid})


from cubes.nosylist import hooks as nosylist
nosylist.S_RELS |= set(('has_activity', 'patch_revision'))
nosylist.O_RELS |= set(('point_of', 'comments'))
