# -*- coding: utf-8 -*-

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

import os
from os import path as osp
from shutil import rmtree
import re
import tempfile
import tarfile
from subprocess import check_call, Popen, PIPE
import hglib

from logilab.common.decorators import classproperty

from cubicweb.devtools.testlib import MAILBOX, CubicWebTC

from cubes.vcsfile import bridge
from cubes.vcsfile.testutils import init_vcsrepo, HGRCMixin, VCSFileTC
from cubes.vcreview.testutils import HgHelperTC

def revnums(patch):
    return sorted(vc.revision for vc in patch.patch_revision)


class AutoReviewPrefTC(VCSFileTC):
    _repo_path = u'newrepo'

    @classmethod
    def pre_setup_database(cls, cnx, config):
        super(AutoReviewPrefTC, cls).pre_setup_database(cnx, config)
        repo = cnx.entity_from_eid(cls.vcsrepoeid)
        repo.cw_set(has_review=True)
        babar = cls.create_user(cnx, 'Babar', ('users', 'reviewers', 'committers'),
                                email=u'babar@ratax.es')
        victor = cls.create_user(cnx, 'Victor', ('users', 'reviewers'),
                                 email=u'victor@ratax.es')
        arthur = cls.create_user(cnx, 'Arthur', ('users', 'reviewers'),
                                 email=u'arthur@ratax.es')
        cnx.create_entity('CWProperty', pkey=u"vcreview.autoreview", value=u"1",
                          for_user=babar)
        cnx.create_entity('CWProperty', pkey=u"vcreview.autoreview", value=u"0",
                          for_user=victor)
        cnx.commit()

    def test_user_pref(self):
        self.refresh()
        with hglib.open(self.repo_path) as hgrepo:
            root = hgrepo.root()
            for user in 'arthur', 'babar', 'victor':
                fname = osp.join(root, user)
                with open(fname, 'w') as f:
                    f.write(user)
                hgrepo.add(fname)
                hgrepo.commit(message="commit from %s" % user,
                              user="%s <%s@ratax.es>" % (user, user))
        with self.repo.internal_cnx() as cnx:
            repo = cnx.entity_from_eid(self.vcsrepoeid)
            repo.cw_adapt_to('VCSRepo').import_content(commitevery=1)
        # ensure patches exists and are at correct WF status
        ref = {'babar <babar@ratax.es>': 'pending-review',
               'victor <victor@ratax.es>': 'in-progress',
               'arthur <arthur@ratax.es>': 'in-progress',
               }
        with self.admin_access.client_cnx() as cnx:
            rset = cnx.execute('Any A, S WHERE P patch_revision REV, '
                               'REV author A, P in_state ST, ST name S')
            for user, status in rset: # pop to check "one commit per user"
                self.assertEqual(ref.pop(user), status, "%s: got %s" % (user, status))

class PatchLifeCycleTC(HgHelperTC):

    def test_root_publishing(self):

        hg = self.hgrepo
        a = self.hg_append_to

        ### 1) root initially draft becomes public
        #############################################################

        # create a simple root changeset as draft
        a('jungle', 'Babar')
        hg.commit(message='Initial jungle content')
        self.refresh()

        # We should have a new Patch linked to revision 0
        with self.admin_access.client_cnx() as cnx:
            revs = self.all_revs(cnx)
            self.assertEqual(1, len(revs))
            self.assertTrue(revs[0].reverse_patch_revision)
            patch = revs[0].reverse_patch_revision[0]
            self.assertEqual('Initial jungle content', patch.patch_name)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)

        # turn the changeset public
        hg.phase(['0'], public=True)
        self.refresh()
        # check that the patch has been "applied"
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('applied', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual(['applied'], wf_history)

    def test_draft_publishing(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to

        with self.admin_access.client_cnx() as cnx:
            oldpatch = self.all_revs(cnx)[0].reverse_patch_revision[0].eid

        ### 2) draft changeset becomes public
        #############################################################

        # create a draft child
        a('jungle', 'Celestine')
        hg.commit(message='couple of elephants')
        self.refresh()

        # We should have a new Patch linked to revision 1
        with self.admin_access.client_cnx() as cnx:
            for rev in self.all_revs(cnx):
                if rev.description == 'couple of elephants':
                    break
            else:
                self.fail('missing draft child')
            self.assertTrue(rev.reverse_patch_revision)
            patch = rev.reverse_patch_revision[0]
            self.assertNotEqual(oldpatch, patch.eid)
            self.assertEqual('couple of elephants', patch.patch_name)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)
            # old patch is unchanged
            oldpatch_state = cnx.entity_from_eid(oldpatch).cw_adapt_to('IWorkflowable').state
            self.assertEqual('applied', oldpatch_state)

        # make the child public
        hg.phase(['1'], public=True)
        self.refresh()

        # check that the patch has been "applied"
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('applied', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual(['applied'], wf_history)

    def test_empty_desc(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to

        a('jungle', 'Pam')
        hg.commit(message=' ') # sic
        self.refresh()

    def test_simple_amend(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to
        with self.admin_access.client_cnx() as cnx:
            oldpatch = self.all_revs(cnx)[0].reverse_patch_revision[0].eid

        ### 3) simple amend that ends up published
        #############################################################

        # add a new draft children again
        a('jungle', 'Pam')
        hg.commit(message='XXX')
        self.refresh()

        # We should have a new Patch linked to revision 1
        with self.admin_access.client_cnx() as cnx:
            rev = self.all_revs(cnx)[-1]
            assert rev.description == 'XXX'
            self.assertTrue(rev.reverse_patch_revision)
            patch = rev.reverse_patch_revision[0]
            self.assertNotEqual(oldpatch, patch.eid)
            self.assertEqual('XXX', patch.patch_name)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)

        # Fix changeset content and description
        path = osp.join(self.tmprepo, 'jungle')
        with open(path, 'r') as f:
            data = f.read().replace('Pam', 'Pom')
        with open(path, 'w') as f:
            f.write(data)
        self.hg('commit', '--amend', '-m', 'first child')
        self.refresh()
        # test that the new revision is added to the same patch
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            rev = self.all_revs(cnx)[-1]
            assert rev.description == 'first child'
            newpatch = rev.reverse_patch_revision[0]
            self.assertEqual(patch.eid, newpatch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)
            self.assertEqual('first child', patch.patch_name)

        # yet another successor. A public one
        self.hg('commit', '--amend', '-m', 'First child')
        hg.phase(['.'], public=True)
        self.refresh()
        # check that the patch has been "applied"
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('applied', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual(['applied'], wf_history)
            self.assertEqual(3, len(patch.patch_revision))


    def test_prune(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to
        with self.admin_access.client_cnx() as cnx:
            oldpatch = self.all_revs(cnx)[0].reverse_patch_revision[0].eid

        ### 4) simple amend that ends up pruned
        #############################################################

        # add a new draft child again
        a('jungle', 'Zephir')
        hg.commit('seocnd child')  # sic
        self.refresh()

        # look for a new patch
        with self.admin_access.client_cnx() as cnx:
            rev = self.all_revs(cnx)[-1]
            assert rev.description == 'seocnd child'
            self.assertTrue(rev.reverse_patch_revision)
            patch = rev.reverse_patch_revision[0]
            self.assertNotEqual(oldpatch, patch.eid)
            self.assertEqual('seocnd child', patch.patch_name)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)

        # amend the patch
        self.hg('commit', '--amend', '-m', 'second child')
        self.refresh()
        # test that patch has two revisions
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            self.assertEqual(2, len(patch.patch_revision))
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)

        prec = self.get_id('.')
        hg.update('.^')
        self.hg('debugobsolete', prec)  # Zephir is a monkey, donkey!
        self.refresh()
        # patch should turn rejected
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('rejected', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual(['rejected'], wf_history)
            self.assertEqual(2, len(patch.patch_revision))

    def test_zombie(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to
        with self.admin_access.client_cnx() as cnx:
            oldpatch = self.all_revs(cnx)[0].reverse_patch_revision[0].eid

        ### 5) changesets turning zombie at some point
        #############################################################

        # create a new draft child
        a('jungle', 'Flare')
        hg.commit('second child')
        self.refresh()

        # look for a new patch
        with self.admin_access.client_cnx() as cnx:
            rev = self.all_revs(cnx)[-1]
            assert rev.description == 'second child'
            self.assertTrue(rev.reverse_patch_revision)
            patch = rev.reverse_patch_revision[0]
            self.assertNotEqual(oldpatch, patch.eid)
            self.assertEqual('second child', patch.patch_name)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)

        # have a successor out of the repo
        path = osp.join(self.tmprepo, 'jungle')
        with open(path, 'r') as f:
            data = f.read().replace('Flare', 'Flore')
        with open(path, 'w') as f:
            f.write(data)
        bundlepath = osp.join(self.tmprepo, 'flore.hg')
        self.hg('commit', '--amend', '-m', 'second child')
        hg.bundle(bundlepath, rev='.', base='.^')
        self.hg('strip', '.')
        self.refresh()
        # patch should be "outdated"
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('outdated', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual(['outdated'], wf_history)
            self.assertEqual(1, len(patch.patch_revision))

        # make the successor visible again
        self.hg('unbundle', bundlepath)
        self.refresh()
        # test should be alive again
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(patch.eid)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual(['outdated', 'in-progress'],
                             wf_history)
            self.assertEqual(2, len(patch.patch_revision))

    def test_delete_revision(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to

        # create a new draft child
        a('jungle', 'Flare')
        hg.commit('second child')
        self.refresh()

        with self.admin_access.client_cnx() as cnx:
            rev = self.all_revs(cnx)[-1]
            assert rev.description == 'second child'
            self.assertTrue(rev.reverse_patch_revision)
            eid_patch = rev.reverse_patch_revision[0].eid
        with self.repo.internal_cnx() as cnx:
            self.assertTrue(cnx.execute('DELETE Revision R WHERE R eid %(eid)s',
                                        {'eid': rev.eid}))
            cnx.commit()
        with self.admin_access.client_cnx() as cnx:
            self.assertFalse(cnx.execute('Patch P WHERE P eid %(eid)s',
                                          {'eid': eid_patch}))

    def test_split(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to
        with self.admin_access.client_cnx() as cnx:
            oldpatch = self.all_revs(cnx)[0].reverse_patch_revision[0].eid

        ### 6) split
        #############################################################

        # create a new draft changeset with two changes
        a('jungle', 'Alexandre')
        a('jungle', 'Isabelle')
        hg.commit('Moar children')
        self.refresh()

        # search for a new patch
        with self.admin_access.client_cnx() as cnx:
            rev = self.all_revs(cnx)[-1]
            assert rev.description == 'Moar children'
            self.assertTrue(rev.reverse_patch_revision)
            patch = rev.reverse_patch_revision[0]
            self.assertNotEqual(oldpatch, patch.eid)
            self.assertEqual('Moar children', patch.patch_name)
            patch_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch_state)
            wf_history = self.get_wf_history(patch)
            self.assertEqual([], wf_history)

        # split them in two
        hg.update('.^')
        a('jungle', 'Alexandre')
        hg.commit('third child')
        a('jungle', 'Isabelle')
        hg.commit('fourth child')
        prec = self.get_id('-3')
        suc1 = self.get_id('-2')
        suc2 = self.get_id('-1')
        self.hg('debugobsolete', prec, suc1, suc2)
        self.refresh()
        # we should now have two patches
        with self.admin_access.client_cnx() as cnx:
            suc1 = self.all_revs(cnx)[-2]
            suc2 = self.all_revs(cnx)[-1]
            assert suc1.description == 'third child'
            assert suc2.description == 'fourth child'
            self.assertTrue(suc1.reverse_patch_revision)
            self.assertTrue(suc2.reverse_patch_revision)
            patch1 = suc1.reverse_patch_revision[0]
            patch2 = suc2.reverse_patch_revision[0]
            self.assertEqual(patch.eid, patch1.eid)
            self.assertNotEqual(patch.eid, patch2.eid)
            self.assertEqual(2, len(patch1.patch_revision))
            self.assertEqual(1, len(patch2.patch_revision))
            patch1_state = patch1.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch1_state)
            patch1_wf_history = self.get_wf_history(patch1)
            self.assertEqual([], patch1_wf_history)
            patch2_state = patch1.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch2_state)
            patch2_wf_history = self.get_wf_history(patch2)
            self.assertEqual([], patch2_wf_history)

    def test_fold(self):
        self.test_root_publishing()
        hg = self.hgrepo
        a = self.hg_append_to

        ### 7) fold
        #############################################################
        # create two draft changesets
        a('jungle', 'Cornelius')
        hg.commit('counselor')
        a('jungle', 'Pompadour')
        hg.commit('More counselor')
        self.refresh()
        # test we have two distinct patches
        with self.admin_access.client_cnx() as cnx:
            rev1 = self.all_revs(cnx)[-2]
            rev2 = self.all_revs(cnx)[-1]
            assert rev1.description == 'counselor'
            assert rev2.description == 'More counselor'
            self.assertTrue(rev1.reverse_patch_revision)
            self.assertTrue(rev2.reverse_patch_revision)
            patch1 = rev1.reverse_patch_revision[0].eid
            patch2 = rev2.reverse_patch_revision[0].eid
            self.assertNotEqual(patch1, patch2)

        # fold the two changesets
        hg.update('.~2')
        a('jungle', 'Cornelius')
        a('jungle', 'Pompadour')
        hg.commit('Counselor')
        pre1 = self.get_id('-3')
        pre2 = self.get_id('-2')
        succ = self.get_id('-1')
        self.hg('debugobsolete', pre1, succ)
        self.hg('debugobsolete', pre2, succ)
        self.refresh()
        # patch1 is folded (into patch2)
        with self.admin_access.client_cnx() as cnx:
            succ = self.all_revs(cnx)[-1]
            assert succ.description == 'Counselor'
            self.assertTrue(succ.reverse_patch_revision)
            patch = succ.reverse_patch_revision[0]
            morepatch = cnx.entity_from_eid(patch2)
            self.assertEqual(patch1, patch.eid)
            self.assertEqual(2, len(patch.patch_revision))
            self.assertEqual(1, len(morepatch.patch_revision))
            patch1_state = patch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('in-progress', patch1_state)
            wf1_history = self.get_wf_history(patch)
            self.assertEqual([], wf1_history)
            patch2_state = morepatch.cw_adapt_to('IWorkflowable').state
            self.assertEqual('folded', patch2_state)
            wf2_history = self.get_wf_history(morepatch)
            self.assertEqual(['folded'], wf2_history)

    def test_late_obsolete(self):
        hg = self.hgrepo
        a = self.hg_append_to

        # create a simple root changeset as draft
        a('jungle', 'Babar')
        hg.commit('Initial jungle content')
        self.refresh()

        # create an unrelated public cs
        hg.update('null')
        a('jungle', 'Babar')
        hg.commit('Amended jungle content')
        hg.phase('.', public=True)
        self.refresh()

        # add obsolete relation
        self.hg('debugobsolete', self.get_id('0'), self.get_id('1'))
        self.refresh()

        with self.admin_access.client_cnx() as cnx:
            rev0 = self.all_revs(cnx)[0]
            self.assertEqual(1, len(rev0.reverse_patch_revision))
            self.assertEqual(1, len(rev0.reverse_obsoletes))
            self.assertEqual(self.all_revs(cnx)[1].changeset, rev0.reverse_obsoletes[0].changeset)
            patch = rev0.reverse_patch_revision[0]
            self.assertEqual('applied', patch.cw_adapt_to('IWorkflowable').state)


class RepositoryNotificationTC(HgHelperTC):

    def test_repo_nosy_list(self):
        """Test that users in the repository nosylist get notified from new
        patches and their activity.
        """
        with self.admin_access.client_cnx() as cnx:
            self.create_user(cnx, 'Zephir', email=u'zephir@monke.ys',
                             interested_in=cnx.find('Repository').one())
            cnx.commit()
        hg = self.hgrepo
        self.hg_append_to('pub', 'whiskey')
        self.hgrepo.commit('refresh')
        self.refresh()
        self.set_description('new patch notification')
        self.assertEqual(len(MAILBOX), 1)
        yield self.assertEqual, MAILBOX[0].recipients, ['zephir@monke.ys']
        self.set_description('patch activity notification')
        MAILBOX[:] = []
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.find('Patch', patch_name='refresh').one()
            patch.cw_adapt_to('IWorkflowable').fire_transition('accept', u'LGTM')
            cnx.commit()
        yield self.assertEqual, MAILBOX[0].recipients, ['zephir@monke.ys']


class PatchNotificationTC(HGRCMixin, CubicWebTC):

    @classmethod
    def setUpClass(cls):
        cls.__tmpdir = tempfile.mkdtemp(prefix='vcreview-test-')
        tarfile.open(cls.repo_path + '.tar').extractall(cls.__tmpdir)

    @classmethod
    def tearDownClass(cls):
        cls.cleanup()

    @classmethod
    def cleanup(cls):
        try:
            rmtree(cls.__tmpdir)
        except:
            pass

    @classproperty
    def full_repo_path(cls):
        return osp.join(cls.__tmpdir, u'repo')

    # XXX presetup
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            # exist in the Mercurial repo
            self.create_user(cnx, 'Babar', ('users', 'reviewers', 'committers'),
                             email=u'babar@jungle.net')
            self.create_user(cnx, 'Victor', ('users', 'reviewers'),
                             email=u'victor@ratax.es')
            # unknown to the Mercurial repo
            self.create_user(cnx, 'Basile', ('users', 'reviewers'),
                             email=u'basile@ratax.es')
            cnx.commit()
            cnx.create_entity('Repository',
                              title=u'Jungle',
                              type=u'mercurial',
                              encoding=u'utf-8',
                              has_review=True,
                              local_cache=self.full_repo_path)
            cnx.commit()
        init_vcsrepo(self.repo)

    def assertEmailEqual(self, email, subject, recipient, content):
        self.assertEqual(email.subject, subject)
        self.assertEqual(email.recipients, [recipient])
        expected = content.splitlines()
        got = email.content.splitlines()
        # we should print a diff like -/+ stuff
        for idx, line in enumerate(expected):
            self.assertMatches('^' + line + '$', got[idx], idx)
        self.assertEqual(len(expected), len(got))

    def assertMatches(self, expected, got, lineno):
        """ expected is a regular expression """
        self.assertTrue(re.match(expected, got),
                'line %d: %r\n does not match:\n %r' % (lineno, got, expected))


    def test_nosy_list_author(self):
        """Test that author of a patch is automatically added to the nosylist"""
        with self.admin_access.client_cnx() as cnx:
            victor = cnx.execute('Any X WHERE X login "Victor"').get_entity(0, 0)
            all_nosy = set(e.eid for e in victor.reverse_nosy_list)
            rset = cnx.execute('Any P WHERE P patch_revision R, '
                               '            R author ILIKE "Victor%"')
            victor_patch = set(eid for eid, in rset)
            self.assertTrue(victor_patch.issubset(all_nosy))
            patch = rset.get_entity(0, 0)
            self.assertEqual(victor.eid, patch.creator.eid)
            self.assertEqual(victor.name(), patch.dc_authors())

    def test_nosy_list_task_author_commenter(self):
        """Test that users adding tasks or comments are added in nosylist"""
        with self.admin_access.repo_cnx() as cnx:
            cornelius_eid = self.create_user(cnx, 'Cornelius').eid
            zephir_eid = self.create_user(cnx, 'Zephir').eid
            cnx.commit()
        with self.new_access('Cornelius').client_cnx() as cnx:
            rset = cnx.find('Revision', description='Add more elephants children')
            rev = rset.get_entity(1, 0)
            patch = rev.reverse_patch_revision[0]
            patch_eid = patch.eid
            task = cnx.create_entity('Task', title=u'todo', reverse_has_activity=patch)
            task_eid = task.eid
            point = cnx.create_entity('InsertionPoint', lid=0, point_of=rev)
            cnx.commit()
        with self.new_access('Zephir').client_cnx() as cnx:
            comment_eid = cnx.create_entity(
                'Comment', comments=task_eid, content=u'coucou').eid
            cnx.commit()
        with self.new_access('Babar').client_cnx() as cnx:
            cnx.create_entity(
                'Comment', comments=comment_eid, content=u'salut')
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            patch = cnx.find('Patch', eid=patch_eid).one()
            patch_nosylist = set(x.login for x in patch.nosy_list)
        self.set_description('author of a task in patch nosylist')
        yield self.assertIn, 'Cornelius', patch_nosylist
        self.set_description('commenter of a task in patch nosylist')
        yield self.assertIn, 'Zephir', patch_nosylist
        self.set_description('commenter of a task comment in patch nosylist')
        yield self.assertIn, 'Babar', patch_nosylist

    def test_reviewer_email(self):
        with self.admin_access.client_cnx() as cnx:
            rql = 'Any R ORDERBY R DESC WHERE R is Revision'
            rev = cnx.execute(rql).get_entity(1, 0)
            assert rev.description == 'Add more elephants children'
            patch = rev.reverse_patch_revision[0]
            assert patch.patch_name == 'Add more elephants children'
            patch.cw_adapt_to('IWorkflowable').fire_transition('ask review')
            cnx.commit()

            self.assertEqual(1, len(patch.patch_reviewer))
            reviewer = patch.patch_reviewer[0]
            self.assertIn(reviewer.login, ('Babar', 'Basile'))
            nosyed = set(u.login for u in patch.nosy_list)
            self.assertEqual(2, len(nosyed))
            self.assertIn(reviewer.login, nosyed)

            MAILBOX[:] = []
            patch.cw_adapt_to('IWorkflowable').fire_transition('ask rework',
                                                               u'coin coin')
            cnx.commit()
            self.assertEqual(2, len(MAILBOX))

            MAILBOX[:] = []
            # patch are only send on ask review, so we reask for review
            patch.cw_adapt_to('IWorkflowable').fire_transition('ask review',
                                                               u'coin coin')
            cnx.commit()
            self.assertEqual(2, len(MAILBOX))
            MAILBOX.sort(key=lambda e: 'victor@ratax.es' in e.recipients)
            review_email = MAILBOX[0]
            self.assertEmailEqual(review_email,
                                  '[Jungle] patch pending-review: Add more elephants children',
                                  [e.address for e in reviewer.primary_email][0],
                                  '\n'
                                  'admin changed status from <in-progress> to <pending-review> for entity\n'
                                  "'Add more elephants children'\n"
                                  '\n'
                                  'coin coin\n'
                                  '\n'
                                  '\(No recorded task\)\n'
                                  '\n'
                                  'url: http://testing.fr/cubicweb/patch/\d+\n'
                                  '\n'
                                  'reviewer: Ba(bar|sile)\n'
                                  '\n'
                                  '# HG changeset patch\n'
                                  '# User Victor <victor@ratax.es>\n'
                                  '# Date 1361805588 0\n'
                                  '%s' # optional human-readable date
                                  '# Node ID bfa5da61c82507b76dae7927b4fce2aa4a0c9c6f\n'
                                  '# Parent  549cd3165597cdd5c9d8fa26e83e63483fcfb4b5\n'
                                  'Add more elephants children\n'
                                  '\n'
                                  'diff --git a/babar.py b/babar.py\n'
                                  '--- a/babar.py\n'
                                  '\+\+\+ b/babar.py\n'
                                  '@@ -5,10 \+5,15 @@\n'
                                  " elephants = \['Babar',\n"
                                  "              'Celeste',\n"
                                  "              'Cornelius',\n"
                                  "              'Pompadour',\n"
                                  "              'Poutifour',\n"
                                  "\+             'Arthur'\n"
                                  "\+             'Pom',\n"
                                  "\+             'Flore',\n"
                                  "\+             'Alexandre',\n"
                                  "\+             'Isabelle',\n"
                                  '              \]\n'
                                  ' \n'
                                  ' \n'
                                  " if __name__ == '__main__':\n"
                                  "     print 'Those are elephants:'\n"
                                  '\n' %
                                  '#      Mon Feb 25 15:19:48 2013 \+0000\n')
            # add task
            MAILBOX[:] = ()
            task = cnx.create_entity('Task', title=u'todo', reverse_has_activity=patch)
            point = cnx.create_entity('InsertionPoint', lid=0, point_of=rev)
            cnx.create_entity('Task', title=u'my point', reverse_has_activity=point)
            cnx.commit()
            self.assertEqual(4, len(MAILBOX))
            # reask review
            MAILBOX[:] = ()
            patch.cw_adapt_to('IWorkflowable').fire_transition('ask rework',
                                                               u'tasked ø')
            cnx.commit()
            self.assertEqual(2, len(MAILBOX))
            MAILBOX.sort(key=lambda e: 'victor@ratax.es' in e.recipients)
            review_email = MAILBOX[0]
            self.assertEmailEqual(review_email,
                                  '[Jungle] patch in-progress: Add more elephants children',
                                  [e.address for e in reviewer.primary_email][0],
                                  '\n'
                                  'admin changed status from <pending-review> to <in-progress> for entity\n'
                                  "'Add more elephants children'\n"
                                  '\n'
                                  u'tasked ø\n'
                                  '\n'
                                  'remaining tasks:\n'
                                  '\n'
                                  '- my point\n'
                                  '- todo\n'
                                  '\n'
                                  'url: http://testing.fr/cubicweb/patch/\d+\n'
                                  '\n'
                                  'reviewer: Ba(bar|sile)\n'
                                  '\n'
                                  '\n')

            # Test that comments are emailed too
            MAILBOX[:] = ()
            point.cw_clear_all_caches()
            comment = cnx.create_entity('Comment', comments=task,
                                            content=u'Babar comments')
            cnx.commit()
            MAILBOX.sort(key=lambda e: 'victor@ratax.es' in e.recipients)
            self.assertEqual(2, len(MAILBOX))
            review_email = MAILBOX[0]
            self.assertEmailEqual(review_email,
                                  'new comment for Task todo',
                                  [e.address for e in reviewer.primary_email][0],
                                  'Babar comments\n'
                                  '\n\n'
                                  'i18n_by_author_field: admin\n'
                                  'url: http://testing.fr/cubicweb/task/%i' % task.eid)

    def test_nonascii(self):
        with self.admin_access.client_cnx() as cnx:
            self.assertEqual(0, len(MAILBOX))
            rql = 'Any R ORDERBY R DESC WHERE R is Revision'
            rev = cnx.execute(rql).get_entity(0, 0)
            patch = rev.reverse_patch_revision[0]
            self.assertEqual(0, len(MAILBOX))
            patch_flow = patch.cw_adapt_to('IWorkflowable')
            patch_flow.fire_transition('ask review', u'beep beep')
            cnx.commit()
            # 3: 2x "patch pending-review" + 1x "patch assigned"
            self.assertEqual(3, len(MAILBOX))
            patch_flow.fire_transition('ask rework', u'coin coin')
            cnx.commit()
            self.assertEqual(5, len(MAILBOX))
            patch_flow.fire_transition('ask review', u'beep beep')
            cnx.commit()
            self.assertEqual(7, len(MAILBOX))
            patch_flow.fire_transition('ask rework', u'coin coin')
            cnx.commit()
            self.assertEqual(9, len(MAILBOX))

            MAILBOX[:] = []
            # emails are only sent on ask review, so we ask again for review
            patch.cw_adapt_to('IWorkflowable').fire_transition('ask review',
                                                               u'coin coin')
            cnx.commit()
            self.assertEqual(2, len(MAILBOX))

PatchNotificationTC.repo_path = osp.join(PatchNotificationTC.datadir,
                                         u'demo-repo-final')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
