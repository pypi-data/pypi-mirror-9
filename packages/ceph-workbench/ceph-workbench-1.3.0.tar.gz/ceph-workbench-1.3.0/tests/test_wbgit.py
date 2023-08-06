# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2015 <contact@redhat.com>
#
# Author: Loic Dachary <loic@dachary.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import fixtures
import mock
import testtools

from ceph_workbench import util
from ceph_workbench import wbgit


class TestWBRepo(testtools.TestCase):

    def setUp(self):
        super(TestWBRepo, self).setUp()
        fixture = fixtures.TempDir()
        self.useFixture(fixture)
        self.d = fixture.path
        util.sh("""
        cd {dir}
        git init
        """.format(dir=self.d))

    def test_update_release2ranges(self):
        util.sh("""
        cd {dir}
        echo > README ; git add README ; git commit -m 'initial' README
        git branch firefly
        echo a >> README ; git commit -m 'a' README
        git tag --annotate -m tag v0.80
        echo a >> README ; git commit -m 'a' README
        git tag --annotate -m tag v0.80.1
        echo a >> README ; git commit -m 'a' README
        git tag --annotate -m tag v0.80.2
        """.format(dir=self.d))
        r = wbgit.WBRepo.factory(['--git-directory', self.d]).open()
        r.release2tag = {'firefly': 'v0.80'}
        r.update_release2ranges()
        self.assertEquals({'firefly': [('v0.80..v0.80.1', 'v0.80.1'),
                                       ('v0.80.1..v0.80.2', 'v0.80.2'),
                                       ('v0.80.2..firefly', 'firefly')]},
                          r.release2ranges)

    def test_remember_picked(self):
        r = wbgit.WBRepo.factory(['--git-directory', self.d]).open()

        class Commit:

            def __init__(self, picked_from, picked_by):
                self.hexsha = picked_by
                self.message = 'cherry picked from commit ' + picked_from
        r.remember_picked(Commit('A', 'B'))
        self.assertEquals(set(['B']), r.commit2picked_by['A'])
        self.assertEquals(set(['A']), r.picked_by2commits['B'])
        r.remember_picked(Commit('A', 'C'))
        self.assertEquals(set(['B', 'C']), r.commit2picked_by['A'])
        r.remember_picked(Commit('D', 'B'))
        self.assertEquals(set(['A', 'D']), r.picked_by2commits['B'])

    @mock.patch.object(wbgit.WBRepo, 'remember_picked')
    def test_remember_commits(self, m_remember_picked):
        util.sh("""
        cd {dir}
        echo > README ; git add README ; git commit -m 'initial' README
        """.format(dir=self.d))

        r = wbgit.WBRepo.factory(['--git-directory', self.d]).open()
        r.remember_commits('release', 'master', 'tag')
        (c,) = r.hexsha2commit.values()
        self.assertEquals('tag', r.commit2tag[c.hexsha])
        self.assertEquals('release', r.commit2release[c.hexsha])
        m_remember_picked.assert_called_with(c)

    @mock.patch.object(wbgit.WBRepo, 'remember_commits')
    def test_update_commits(self, m_remember_commits):
        util.sh("""
        cd {dir}
        echo > README ; git add README ; git commit -m 'initial' README
        git branch next
        git branch firefly
        echo a >> README ; git commit -m 'a' README
        git tag --annotate -m tag v0.80
        echo a >> README ; git commit -m 'a' README
        git tag --annotate -m tag v0.80.1
        """.format(dir=self.d))
        r = wbgit.WBRepo.factory(['--git-directory', self.d,
                                  '--releases=firefly']).open()
        r.update_release2ranges()
        r.update_commits()
        e = [mock.call('firefly', 'v0.80..v0.80.1', 'v0.80.1'),
             mock.call('firefly', 'v0.80.1..firefly', 'firefly'),
             mock.call('master', 'cuttlefish..master', 'master'),
             mock.call('next', 'master..next', 'next')]
        self.assertEquals(m_remember_commits.call_args_list, e)

    def test_update_head2merge(self):
        util.sh("""
        cd {dir}
        set -x
        echo > README ; git add README ; git commit -m 'initial' README
        git branch cuttlefish
        echo a >> README ; git commit -m 'a' README
        git branch firefly
        echo a >> README ; git commit -m 'a' README
        git checkout -b next
        echo a >> README ; git commit -m 'head' README
        git checkout master
        git merge --no-ff -m 'merge' next
        """.format(dir=self.d))

        r = wbgit.WBRepo.factory(['--git-directory', self.d,
                                  '--releases=firefly']).open()
        r.update_head2merge()
        self.assertEquals(1, len(r.head2merge))
        head = r.r.commit(list(r.head2merge.keys())[0])
        self.assertEquals('head\n', head.message)
        merge = r.r.commit(list(r.head2merge.values())[0])
        self.assertEquals('merge\n', merge.message)

    def test_update_release2backports(self):
        util.sh("""
        cd {dir}
        set -x
        echo > README ; git add README ; git commit -m 'initial' README
        git branch emperor
        echo a >> README ; git commit -m 'a' README
        git branch firefly
        git branch firefly-backports
        """.format(dir=self.d))

        r = wbgit.WBRepo.factory(['--git-directory', self.d,
                                  '--releases=emperor,firefly']).open()
        r.update_release2backports()
        self.assertIn('firefly', r.release2backports)
        self.assertNotIn('emperor', r.release2backports)

    def test_update_release2last_tag(self):
        util.sh("""
        cd {dir}
        echo > README ; git add README ; git commit -m 'initial' README
        git checkout -b firefly
        echo a >> README ; git commit -m 'a' README
        git tag --annotate -m tag v0.80
        echo a >> README ; git commit -m 'a' README
        git tag --annotate -m tag v0.80.1
        """.format(dir=self.d))
        r = wbgit.WBRepo.factory(['--git-directory', self.d,
                                  '--releases=firefly']).open()
        r.update_release2last_tag()
        self.assertEquals('v0.80.1', r.release2last_tag['firefly'])
