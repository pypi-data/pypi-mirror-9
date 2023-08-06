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

from ceph_workbench import main

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG)


class TestCephWorkbench(testtools.TestCase):

    def test_init(self):
        w = main.CephWorkbench()
        w.parser.parse_args([
            'backport',
            '--git-directory=A',
            '--redmine-url=A',
            '--redmine-user=A',
            '--redmine-password=A',
            '--gitlab-url=A',
            '--gitlab-token=A',
        ])
        w.parser.parse_args([
            'github2gitlab',
            '--gitlab-url=A',
            '--gitlab-token=A',
            '--github-repo=A/B',
        ])

# Local Variables:
# compile-command: "../.tox/py27/bin/py.test test_main.py"
# End:
