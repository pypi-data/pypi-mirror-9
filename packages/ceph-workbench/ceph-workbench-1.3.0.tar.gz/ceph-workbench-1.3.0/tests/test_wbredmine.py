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
import logging
import testtools

from ceph_workbench import wbredmine

REDMINE = {
    'url': 'http://localhost:10080',
    'username': 'admin',
    'password': 'admin',
}

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG)


class TestWBRedmine(testtools.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.argv = [
            '--redmine-url', REDMINE['url'],
            '--redmine-user', REDMINE['username'],
            '--redmine-password', REDMINE['password'],
        ]
        r = wbredmine.WBRedmine.factory(cls.argv).open()

        cls.redmine = r.r

        cls.tearDownClass()

        cls.project = cls.redmine.project.create(
            name='Ceph',
            identifier='ceph',
            issue_custom_field_ids=[r.backport_id],
        )

    @classmethod
    def tearDownClass(cls):
        for project in cls.redmine.project.all():
            if project['name'] == 'Ceph':
                cls.redmine.project.delete(project['id'])

    def test_load_open_issues(self):
        argv = self.argv + ['--releases=firefly']
        r = wbredmine.WBRedmine.factory(argv).open()
        issue = r.r.issue.create(project_id=self.project['id'],
                                 subject='SUBJECT',
                                 description='DESCRIPTION',
                                 custom_fields=[{
                                     "id": r.backport_id,
                                     "value": 'firefly'
                                 }])
        r.r.issue.update(issue.id, notes='NOTE')
        r.load_open_issues()
        self.assertIn(issue['id'], r.issues)
        issue = r.issues[issue['id']]
        self.assertEquals(set(['firefly']), issue['backports'])
        notes = list(map(lambda j: j['notes'], issue['journals']))
        self.assertEquals(['NOTE'], notes)
