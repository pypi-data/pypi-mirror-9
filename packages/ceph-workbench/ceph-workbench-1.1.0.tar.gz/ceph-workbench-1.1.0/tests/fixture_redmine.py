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
from ceph_workbench import wbredmine

REDMINE = {
    'url': 'http://localhost:10080',
    'username': 'admin',
    'password': 'admin',
}


class FixtureRedmine:

    def setUp(self):
        self.argv = [
            '--redmine-url', REDMINE['url'],
            '--redmine-user', REDMINE['username'],
            '--redmine-password', REDMINE['password'],
        ]
        r = wbredmine.WBRedmine.factory(self.argv).open()

        self.redmine = r.r
        self.backport_id = r.backport_id

        self.tearDown()

        self.project = self.redmine.project.create(
            name='Ceph',
            identifier='ceph',
            issue_custom_field_ids=[self.backport_id],
        )

    def tearDown(self):
        for project in self.redmine.project.all():
            if project['name'] == 'Ceph':
                self.redmine.project.delete(project['id'])

    def issue_create(self, subject, description, backport, notes):
        issue = self.redmine.issue.create(project_id=self.project['id'],
                                          subject=subject,
                                          description=description,
                                          custom_fields=[{
                                              "id": self.backport_id,
                                              "value": backport,
                                          }])
        self.redmine.issue.update(issue.id, notes=notes)
        return issue
