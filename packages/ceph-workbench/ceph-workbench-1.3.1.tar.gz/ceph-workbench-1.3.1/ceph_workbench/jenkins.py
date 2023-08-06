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
import json
import logging
import re
import requests


class Jenkins:

    def __init__(self, args):
        self.args = args

    def run(self):
        if self.args.publish_build_to_pull_request:
            return self.publish_build_to_pull_request()

    @staticmethod
    def get_parser():
        parser = argparse.ArgumentParser(
            description="Jenkins",
            conflict_handler='resolve',
        )
        parser.add_argument('--publish-build-to-pull-request',
                            help='add a comment to pull request XXX')
        parser.add_argument('--jenkins-url',
                            help='URL of the jenkins server')
        parser.add_argument('--github-repo',
                            help='GitHub repo (for instance ceph/ceph)')
        parser.add_argument('--github-token',
                            help='GitHub authentication token')
        return parser

    @staticmethod
    def factory(argv):
        return Jenkins(Jenkins.get_parser().parse_args(argv))

    def publish_build_to_pull_request(self):
        r = requests.get(self.args.jenkins_url + '/' +
                         self.args.publish_build_to_pull_request + '/api/json')
        r.raise_for_status()
        report = r.json()
        logging.debug("publish_build_to_pull_request: downstream " +
                      str(report))
        for action in report['actions']:
            if "causes" in action:
                cause = action['causes'][0]
                upstream = (cause['upstreamUrl'] + '/' +
                            str(cause['upstreamBuild']))
        r = requests.get(self.args.jenkins_url + '/' + upstream + '/api/json')
        r.raise_for_status()
        report = r.json()
        logging.debug("publish_build_to_pull_request: upstream " + str(report))
        for action in report['actions']:
            if "lastBuiltRevision" in action:
                branch = action["lastBuiltRevision"]["branch"][0]
        runs = {}
        for run in report['runs']:
            if run['number'] == report['number']:
                r = requests.get(run['url'] + 'api/json')
                r.raise_for_status()
                runs[run['url']] = r.json()['result']
        body = report['result'] + ": " + report['url'] + "\n"
        for url in sorted(runs):
            body += "* " + runs[url] + " " + url + "\n"
        logging.debug("publish_build_to_pull_request: " + body)
        if 'pull/' in branch['name']:
            (pr,) = re.findall('\d+$', branch['name'])
            payload = {'body': body}
            r = requests.post('https://api.github.com/repos/' +
                              self.args.github_repo + '/issues/' +
                              pr + '/comments?access_token=' +
                              self.args.github_token,
                              data=json.dumps(payload))
            r.raise_for_status()
            return r.json()['body']
        else:
            return body
