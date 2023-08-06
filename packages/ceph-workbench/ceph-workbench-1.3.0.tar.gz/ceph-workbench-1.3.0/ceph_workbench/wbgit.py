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
from ceph_workbench import util
import git
import logging
import re
import six


class WBRepo:

    release2tag = {'dumpling': 'v0.67',
                   'emperor': 'v0.72',
                   'firefly': 'v0.80',
                   'giant': 'v0.87'}

    def __init__(self, args):
        self.args = args
        self.release2tag = WBRepo.release2tag
        self.commit2picked_by = {}
        self.picked_by2commits = {}
        self.hexsha2commit = {}
        self.commit2release = {}
        self.commit2tag = {}
        self.head2merge = {}

    def open(self):
        logging.debug("git.Repo(" + self.args.git_directory + ")")
        self.r = git.Repo(self.args.git_directory)
        return self

    def index(self):
        self.update_release2ranges()
        self.update_commits()
        self.update_head2merge()
        self.update_release2backports()
        self.update_release2last_tag()
        return self

    @staticmethod
    def get_parser():
        parser = argparse.ArgumentParser(
            description="git repository",
            parents=[util.get_parser()],
            add_help=False,
        )
        parser.add_argument('--git-directory',
                            help='git directory',
                            required=True)
        return parser

    @staticmethod
    def factory(argv):
        return WBRepo(WBRepo.get_parser().parse_args(argv))

    def update_release2ranges(self):
        self.release2ranges = {}
        # generate the ranges that will give us the list of commits
        # for each minor release
        for (release, tag) in six.iteritems(self.release2tag):
            self.release2ranges[release] = []
            current = tag
            minor = 1
            while True:
                try:
                    minor_tag = tag + "." + str(minor)
                    self.r.rev_parse(minor_tag)
                    self.release2ranges[release].append(
                        (current + ".." + minor_tag, minor_tag)
                    )
                    current = minor_tag
                    minor += 1
                except git.exc.BadName:
                    self.release2ranges[release].append(
                        (current + ".." + release, release)
                    )
                    break

    def remember_picked(self, c):
        match = re.search(r'cherry picked from commit (\w+)',
                          c.message,
                          re.IGNORECASE)
        if match:
            hexsha = match.group(1)
            self.commit2picked_by.setdefault(hexsha, set()).add(c.hexsha)
            self.picked_by2commits.setdefault(c.hexsha, set()).add(hexsha)

    def remember_commits(self, release, range, tag):
        for c in self.r.iter_commits(range, no_merges=True):
            self.remember_picked(c)
            self.commit2release[c.hexsha] = release
            self.commit2tag[c.hexsha] = tag
            self.hexsha2commit[c.hexsha] = c

    def update_commits(self):
        for release in self.args.releases:
            for (range, tag) in self.release2ranges[release]:
                self.remember_commits(release, range, tag)
        dev = [('cuttlefish..master', 'master')]
        if 'next' in self.r.branches:
            dev.append(('master..next', 'next'))
        for (range, tag) in dev:
            self.remember_commits(tag, range, tag)

    def for_each_merge(self, fun):
        for merge in self.r.iter_commits('cuttlefish..master',
                                         merges=True):
            fun(merge)
        if 'next' in self.r.branches:
            n = ['next']
        else:
            n = []
        for release in self.args.releases + n:
            for merge in self.r.iter_commits('master..' + release,
                                             merges=True):
                fun(merge)

    def update_head2merge(self):
        """There is no convenient way to find the child of a commit: make a
        table that associates the commit that was merged into Ceph to
        the merge commit that did it (i.e. the child of the commit).
        """
        def head2merge(merge):
            self.head2merge[merge.parents[1].hexsha] = merge.hexsha
        self.for_each_merge(head2merge)

    def update_release2backports(self):
        self.release2backports = {}
        for release in self.args.releases:
            try:
                backport = release + '-backports'
                self.r.rev_parse(backport)
                logging.debug("found " + backport)
                self.release2backports[release] = backport
            except git.exc.BadName:
                pass

    def update_release2last_tag(self):
        self.release2last_tag = {}
        for release in self.args.releases:
            self.release2last_tag[release] = util.sh(
                'cd ' + self.args.git_directory + ' ; '
                'git describe --abbrev=0 heads/' + release
            ).strip()
