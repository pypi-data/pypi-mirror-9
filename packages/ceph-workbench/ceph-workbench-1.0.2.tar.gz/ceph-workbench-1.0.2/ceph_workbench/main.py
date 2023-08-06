# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 2015 <contact@redhat.com>
#
# Author: Loic Dachary <loic@dachary.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see `<http://www.gnu.org/licenses/>`.
#
import argparse
from ceph_workbench import wbbackport
from github2gitlab import main


class CephWorkbench:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="development workflow for Ceph")

        subparsers = self.parser.add_subparsers(
            title='subcommands',
            description='valid subcommands',
            help='sub-command -h',
        )

        subparsers.add_parser(
            'github2gitlab',
            help='Mirror a GitHub project to GitLab',
            parents=[main.GitHub2GitLab.get_parser()],
            add_help=False,
        ).set_defaults(
            func=main.GitHub2GitLab,
        )

        subparsers.add_parser(
            'backport',
            help='Backport reports',
            parents=[wbbackport.WBBackport.get_parser()],
            add_help=False,
        ).set_defaults(
            func=wbbackport.WBBackport,
        )
