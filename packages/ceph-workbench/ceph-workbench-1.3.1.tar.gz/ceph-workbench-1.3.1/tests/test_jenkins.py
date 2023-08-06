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
import responses
import testtools

from ceph_workbench import jenkins

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.DEBUG)


class TestJenkins(testtools.TestCase):

    @responses.activate
    def test_publish_build_to_pull_request(self):
        pr = '123'
        build = 'ceph/3'
        jenkins_url = 'http://jenkins'
        upstream_build = '12'
        upstream_url = 'job/ceph'
        build_report = """
{
  "actions": [
    {
      "causes": [
        {
          "shortDescription": "Started by upstream project build number 12",
          "upstreamBuild": {upstream_build},
          "upstreamProject": "ceph",
          "upstreamUrl": "{upstream_url}"
        }
      ]
    },
    {}
  ],
  "artifacts": [],
  "building": false,
  "description": null,
  "duration": 3996,
  "estimatedDuration": 2042,
  "executor": null,
  "fullDisplayName": "ceph-report #1",
  "id": "2015-04-06_08-26-47",
  "keepLog": false,
  "number": 1,
  "result": "SUCCESS",
  "timestamp": 1428308807127,
  "url": "http://jenkins/job/ceph-report/1/",
  "builtOn": "rex003",
  "changeSet": {
    "items": [],
    "kind": null
  },
  "culprits": []
}
""".replace('{upstream_url}',
            upstream_url).replace('{upstream_build}',
                                  upstream_build)
        responses.add(responses.GET, jenkins_url + '/' + build + '/api/json',
                      body=build_report, status=200,
                      content_type='application/json')
        os_url = 'http://jenkins/job/ceph/TARGET_OPERATING_SYSTEM'
        upstream_build_report = """
{
  "actions": [
    {
      "causes": [
        {
          "shortDescription": "Started by user Ceph Admin",
          "userId": "admin",
          "userName": "Ceph Admin"
        }
      ]
    },
    {},
    {
      "buildsByBranchName": {
        "refs/remotes/origin/pull/123": {
          "buildNumber": 12,
          "buildResult": null,
          "marked": {
            "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
            "branch": [
              {
                "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
                "name": "refs/remotes/origin/pull/123"
              }
            ]
          },
          "revision": {
            "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
            "branch": [
              {
                "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
                "name": "refs/remotes/origin/pull/123"
              }
            ]
          }
        }
      },
      "lastBuiltRevision": {
        "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
        "branch": [
          {
            "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
            "name": "refs/remotes/origin/pull/123"
          }
        ]
      },
      "remoteUrls": [
        "http://workbench.dachary.org/ceph/ceph.git"
      ],
      "scmName": ""
    },
    {},
    {}
  ],
  "artifacts": [],
  "building": false,
  "description": null,
  "duration": 31117,
  "estimatedDuration": 1971442,
  "executor": null,
  "fullDisplayName": "ceph #12",
  "id": "2015-04-06_08-26-06",
  "keepLog": false,
  "number": 12,
  "result": "FAILURE",
  "timestamp": 1428308766532,
  "url": "http://jenkins/{upstream_url}/{upstream_build}/",
  "builtOn": "rex003",
  "changeSet": {
    "items": [],
    "kind": "git"
  },
  "culprits": [],
  "runs": [
    {
      "number": {upstream_build},
      "url": "{os_url}=centos-7/{upstream_build}/"
    },
    {
      "number": {upstream_build},
      "url": "{os_url}=ubuntu-14.04/{upstream_build}/"
    },
    {
      "number": 1,
      "url": "http://jenkins/job/ceph/system=centos-7/1/"
    }
  ]
}
""".replace('{upstream_url}',
            upstream_url).replace('{upstream_build}',
                                  upstream_build).replace('{os_url}', os_url)
        responses.add(responses.GET, jenkins_url + '/' +
                      upstream_url + '/' + upstream_build + '/api/json',
                      body=upstream_build_report, status=200,
                      content_type='application/json')
        build_url = ("http://jenkins/" + upstream_url +
                     "/TARGET_OPERATING_SYSTEM=centos-7/" + upstream_build)
        os_build_report = """
{
  "actions": [
    {
      "lastBuiltRevision": {
        "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
        "branch": [
          {
            "SHA1": "23549bfbbdc88c874d9660889450612d2d372b26",
            "name": "refs/remotes/origin/pull/123"
          }
        ]
      }
    }
  ],
  "number": {upstream_build},
  "result": "{result}",
  "url": "{build_url}"
}
"""
        centos_build_report = (os_build_report.
                               replace('{build_url}', build_url).
                               replace('{result}', 'SUCCESS').
                               replace('{upstream_build}', upstream_build))
        responses.add(responses.GET, build_url + '/api/json',
                      body=centos_build_report, status=200,
                      content_type='application/json')
        build_url = ("http://jenkins/" + upstream_url +
                     "/TARGET_OPERATING_SYSTEM=ubuntu-14.04/" +
                     upstream_build)
        ubuntu_build_report = (os_build_report.
                               replace('{build_url}', build_url).
                               replace('{result}', 'FAILURE').
                               replace('{upstream_build}', upstream_build))
        responses.add(responses.GET, build_url + '/api/json',
                      body=ubuntu_build_report, status=200,
                      content_type='application/json')
        github_repo = 'my/repo'
        github_token = 'TOKEN'
        expected = """\
FAILURE: http://jenkins/job/ceph/12/
* SUCCESS http://jenkins/job/ceph/TARGET_OPERATING_SYSTEM=centos-7/12/
* FAILURE http://jenkins/job/ceph/TARGET_OPERATING_SYSTEM=ubuntu-14.04/12/
"""
        github_url = ('https://api.github.com/repos/' + github_repo +
                      '/issues/' + pr + '/comments?access_token=' +
                      github_token)

        def request_callback(request):
            return (200, {}, request.body)
        responses.add_callback(responses.POST, github_url,
                               callback=request_callback,
                               content_type='application/json',
                               match_querystring=True)
        j = jenkins.Jenkins.factory([
            '--publish-build-to-pull-request', build,
            '--jenkins-url', jenkins_url,
            '--github-repo', github_repo,
            '--github-token', github_token,
        ])
        self.assertEquals(expected, j.run())
