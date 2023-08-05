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
"""cubicweb-vcreview automatic tests"""

import os.path as osp
from shutil import rmtree
import tempfile
import tarfile

from logilab.common.decorators import classproperty


from cubicweb.devtools import testlib

from cubes.vcsfile.testutils import init_vcsrepo, HGRCMixin

class AutomaticWebTest(HGRCMixin, testlib.AutomaticWebTest):
    no_auto_populate = ('Repository',
                        'Revision',
                        'Patch',
                        'Comment',
                        'InsertionPoint',)
    ignored_relations = set(('parent_revision',
                             'from_repository',
                             'patch_revision',
                             'nosy_list',
                             'comments',
                             'depends_on',
                             'point_of'))

    def to_test_etypes(self):
        return set(('Repository',
                    'Revision',
                    'Patch',
                    'InsertionPoint',
                    ))


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
    def custom_populate(self, how_many, cnx):
        self.create_user(cnx, 'Babar', ('users', 'reviewers', 'committers'),
                         email=u'babar@jungle.net')
        self.create_user(cnx, 'Victor', ('users', 'reviewers'),
                         email=u'victor@ratax.es')
        cnx.commit()
        cnx.create_entity('Repository',
                          type=u'mercurial',
                          encoding=u'utf8',
                          local_cache=self.full_repo_path,
                          has_review=True)
        cnx.commit()
        init_vcsrepo(self.repo)

AutomaticWebTest.repo_path = osp.join(AutomaticWebTest.datadir,
                                      u'demo-repo-final')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
