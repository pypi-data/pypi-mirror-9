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

from __future__ import with_statement

import os.path as osp
import functools
import tempfile
import tarfile
from shutil import rmtree

from logilab.common.decorators import classproperty

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web import facet

from cubes.vcsfile.testutils import init_vcsrepo, HGRCMixin
from cubes.vcreview.views.facets import PatchHasTodoTask


class PatchReviewWorkflowTC(HGRCMixin, CubicWebTC):

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

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            # create users
            create_user = functools.partial(self.create_user, cnx)
            self.reviewer1 = create_user('Victor', ('users', 'reviewers'),
                                         email=u'victor@ratax.es').eid
            self.reviewer2 = create_user('Podular', ('users', 'reviewers'),
                                         email=u'podular@elephan.tz').eid
            self.committer = create_user('committer', ('users',)).eid
            cnx.commit()

            # import revisions from repository
            with cnx.security_enabled(write=False):
                with cnx.deny_all_hooks_but('metadata'):
                    cnx.create_entity('Repository', type=u'mercurial',
                                      encoding=u'utf8',
                                      local_cache=self.full_repo_path,
                                      repository_committer=self.committer,
                                      has_review=True)
                    cnx.commit()
            init_vcsrepo(self.repo)

            # ask review
            rset = cnx.execute('Patch P ORDERBY P DESC '
                               'WHERE P in_state S, '
                               '      S name "in-progress"')
            for patch in rset.entities():
                patch.cw_adapt_to('IWorkflowable').fire_transition('ask review')
            cnx.commit()

            # record eids of patches pending review
            rset = cnx.execute('Patch P ORDERBY P DESC '
                               'WHERE P in_state S, '
                               '      S name "pending-review"')
            self.patch1eid = rset[2][0]
            self.patch2eid = rset[3][0]
            cnx.commit()

            # create task
            self.task1eid = cnx.create_entity(
                'Task', reverse_has_activity=self.patch1eid, title=u'todo 1').eid
            cnx.commit()

    def test_wf(self):
        with self.admin_access.client_cnx() as cnx:
            patch = cnx.entity_from_eid(self.patch1eid)
            self.assertEqual(patch.patch_reviewer[0].eid, self.reviewer2)
        with self.new_access('Victor').client_cnx() as cnx:
            rset = cnx.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid})
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(cnx, rset, 'workflow')),
                                 ['accept', 'ask rework', 'fold', 'view history', 'view workflow'])
            # reviewer1 submit its second patch for review: while reviewer2
            # already has a patch for review, it should be picked anyway as a
            # patch creator can't be its reviewer
            patch = cnx.execute('Any X WHERE X eid %(x)s', {'x': self.patch2eid}).get_entity(0, 0)
            self.assertEqual(patch.patch_reviewer[0].eid, self.reviewer2)
            # create a task and mark the task1 as done
            task2eid = cnx.create_entity(
                'Task', reverse_has_activity=patch, title=u'todo 2').eid
            task = cnx.execute('Any X WHERE X eid %(x)s', {'x': self.task1eid}).get_entity(0, 0)
            task.cw_adapt_to('IWorkflowable').fire_transition('done')
            cnx.commit()
        with self.new_access('Podular').client_cnx() as cnx:
            rset = cnx.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid})
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(cnx, rset, 'workflow')),
                                 ['accept', 'ask rework', 'fold', 'view history', 'view workflow'])
            patch = rset.get_entity(0, 0)
            patch.cw_adapt_to('IWorkflowable').fire_transition('accept')
            cnx.commit()
            patch.cw_clear_all_caches()
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(cnx, rset, 'workflow')),
                                 [u'ask review', u'ask rework', u'fold', u'view history', u'view workflow'])
            # create a task and mark task2 as done
            task3eid = cnx.create_entity(
                'Task', reverse_has_activity=patch, title=u'todo 3').eid
            task = cnx.execute('Any X WHERE X eid %(x)s', {'x': task2eid}).get_entity(0, 0)
            task.cw_adapt_to('IWorkflowable').fire_transition('done')
            cnx.commit()
        with self.new_access('committer').client_cnx() as cnx:
            rset = cnx.execute('Any X WHERE X eid %(x)s', {'x': self.patch1eid})
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(cnx, rset, 'workflow')),
                                 ['apply', 'ask review', 'ask rework', 'fold', 'reject', 'view history', 'view workflow'])
            patch = rset.get_entity(0, 0)
            patch.cw_adapt_to('IWorkflowable').fire_transition('apply')
            cnx.commit()
            patch.cw_clear_all_caches()
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(cnx, rset, 'workflow')),
                                 ['view history'])
            # mark task3 as done
            task = cnx.execute('Any X WHERE X eid %(x)s', {'x': task3eid}).get_entity(0, 0)
            task.cw_adapt_to('IWorkflowable').fire_transition('done')
            cnx.commit()


    def test_review_adapter_reviewers_rset(self):
        """check reviewer configuration

        1) Test that explicit `repository_reviewer` are taken in account
        2) Test that `reviewer` group can be disabled on a repo.
        """
        with self.admin_access.client_cnx() as cnx:
            otherrepo = cnx.create_entity('Repository', type=u'mercurial',
                                          encoding=u'utf8',
                                          local_cache=u'/dev/null',
                                          has_review=True)
            cnx.execute('SET X repository_reviewer U WHERE U login "committer"')
            patch = cnx.entity_from_eid(self.patch1eid)
            ireview = patch.cw_adapt_to('IPatchReviewControl')
            self.assertEqual(set(x for x,_ in ireview.reviewers_rset().rows),
                             set([self.reviewer2,
                                  self.committer]))
            cnx.execute('SET X use_global_groups FALSE WHERE NOT X eid %(e)s', {'e': otherrepo.eid})
            patch.cw_clear_all_caches()
            ireview = patch.cw_adapt_to('IPatchReviewControl')
            self.assertEqual(set(x for x,_ in ireview.reviewers_rset().rows),
                             set([self.committer]))


PatchReviewWorkflowTC.repo_path = osp.join(PatchReviewWorkflowTC.datadir,
                                      u'demo-repo-final')


class VCReviewFacetTC(CubicWebTC):

    def test_patch_has_open_task_facet(self):
        with self.admin_access.web_request() as req:
            req.create_entity('Patch', patch_name=u'turlu')
            rset = req.cnx.execute('Patch X')
            rqlst = rset.syntax_tree().copy()
            select = rqlst.children[0]
            filtered_variable, baserql = facet.init_facets(rset, select)

            f = PatchHasTodoTask(req, rset=rset, select=select,
                                 filtered_variable=filtered_variable)
            req.form[f.__regid__] = "1"
            f.add_rql_restrictions()
            self.assertEqual(f.select.as_string(),
                             "DISTINCT Any  WHERE X is Patch, (EXISTS(X has_activity A, "
                             "A in_state B, B name 'todo')) OR (EXISTS(X patch_revision C, "
                             "D point_of C, D has_activity E, E in_state F, F name 'todo'))")


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
