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
from subprocess import check_call, Popen, PIPE
import hglib

from cubicweb.devtools.testlib import CubicWebTC
from cubes.vcsfile import bridge
from cubes.vcsfile.testutils import HGRCMixin

os.environ['HGRCPATH'] = os.devnull


class HgHelperTC(HGRCMixin, CubicWebTC):
    hgconfig = HGRCMixin.hgconfig.copy()
    hgconfig['extensions']['mq'] = ''
    verbose_hg = False

    def setup_database(self):
        self.tmprepo = tempfile.mkdtemp()
        hglib.init(self.tmprepo)
        self.hgrepo = hglib.open(self.tmprepo)
        with self.admin_access.client_cnx() as cnx:
            self.cwhgrepo = cnx.create_entity('Repository',
                                              type=u'mercurial',
                                              encoding=u'utf-8',
                                              import_revision_content=True,
                                              local_cache=unicode(self.tmprepo),
                                              has_review=True).eid
            cnx.commit()

    def tearDown(self):
        self.hgrepo.close()
        rmtree(self.tmprepo, ignore_errors=True)
        return super(HgHelperTC, self).tearDown()

    def hg(self, *args):
        return self.hgrepo.rawcommand(args)

    def hg_append_to(self, path, content='', add=True):
        """Add a new line to a file in the repo"""
        path = osp.join(self.tmprepo, path)
        with open(path, 'a') as f:
            f.write(content)
            f.write('\n')
        if add:
            self.hgrepo.add(path)

    def refresh(self):
        """Have cubicweb read the on disk repo"""
        with self.repo.internal_cnx() as cnx:
            bridge.import_content(cnx, raise_on_error=True)
            cnx.commit()

    def all_revs(self, cnx):
        """Return all revisions that exist in the test repo entity"""
        rql = 'Revision R ORDERBY R WHERE R from_repository RE, RE eid %(re)s'
        rset = cnx.execute(rql, {'re': self.cwhgrepo})
        return list(rset.entities())

    def get_id(self, rev):
        """return the full hex of the full id of a changeset"""
        cmd = ['id', '--debug', '--id', '--rev', rev]
        if self.verbose_hg:
            print ' '.join(cmd)
        rid = self.hgrepo.rawcommand(cmd).strip()
        assert len(rid) == 40, rid
        return rid

    @staticmethod
    def get_wf_history(patch):
        return [tr.new_state.name
                for tr in patch.cw_adapt_to('IWorkflowable').workflow_history]
