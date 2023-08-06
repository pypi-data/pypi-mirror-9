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
import fixtures
import json
import mock
import os
import tempfile
import testtools

from github2gitlab import main

class TestGitHub2GitLab(testtools.TestCase):

    def setUp(self):
        super(TestGitHub2GitLab, self).setUp()
        self.gitlab_url = 'http://gitlab'
        self.gitlab_token = 'token'
        self.github_repo = 'user/repo'
        self.g = main.GitHub2GitLab([
            '--gitlab-url', self.gitlab_url,
            '--gitlab-token', self.gitlab_token,
            '--github-repo', self.github_repo,
        ])
        fixture = fixtures.TempDir()
        self.useFixture(fixture)
        self.d = fixture.path

    def tearDown(self):
        super(TestGitHub2GitLab, self).tearDown()

    def test_init(self):
        self.assertRaises(SystemExit, main.GitHub2GitLab, [])
        self.assertIn(os.environ['HOME'], self.g.args.ssh_public_key)
        self.assertEqual(self.github_repo, self.g.github['repo'])
        self.assertIn(self.gitlab_url, self.g.gitlab['url'])

    @mock.patch('requests.get')
    def test_get(self, m_requests_get):
        g = self.g
        class Request:
            def __init__(self, params):
                if params.get('page') == '1':
                    self.payload = [1]
                    self.headers = {}
                else:
                    self.payload = [0]
                    self.headers = {
                        "Link": ("<" + g.gitlab['url'] +
                                 '?page=1> rel="next"'),
                    }

            def json(self):
                return self.payload

        m_requests_get.side_effect = lambda url, params: Request(params)
        result = self.g.get(self.g.gitlab['url'], {'key': 'value'},
                            cache=False)
        m_requests_get.assert_called()
        self.assertEqual([0, 1], result)
        other_result = self.g.get(self.g.gitlab['url'], {'key': 'value'},
                                  cache=False)
        self.assertEqual(result, other_result)

    @mock.patch('requests.get')
    def test_get_pull_requests(self, m_requests_get):
        number1 = 1
        number2 = 2

        class Request:
            def __init__(self):
                self.headers = {}

            def json(self):
                return [{"number":number1},
                        {"number":number2}]

        m_requests_get.side_effect = lambda url, params: Request()
        result = self.g.get_pull_requests()
        self.assertEqual({
            str(number1): { u'number': number1 },
            str(number2): { u'number': number2 },
        }, result)

    @mock.patch('requests.get')
    def test_get_merge_requests(self, m_requests_get):
        id1 = 100
        id2 = 200

        class Request:
            def __init__(self):
                self.headers = {}

            def json(self):
                return [{"id": id1},
                        {"id": id2}]

        m_requests_get.side_effect = lambda url, params: Request()
        result = self.g.get_merge_requests()
        self.assertEqual({
            str(id1): { u'id': id1 },
            str(id2): { u'id': id2 },
        }, result)

    @mock.patch('requests.put')
    @mock.patch('requests.get')
    def test_unprotect_branches(self,
                                m_requests_get,
                                m_requests_put):
        class Get:
            def raise_for_status(self):
                pass
            def json(self):
                return [
                    {
                        'name': 'master',
                        'protected': True,
                    },
                    {
                        'name': 'branch1',
                        'protected': False,
                    },
                ]
        m_requests_get.side_effect = lambda url, params: Get()
        class Put:
            def raise_for_status(self):
                pass
        m_requests_put.side_effect = lambda url, params: Put()
        self.assertEquals(1, self.g.unprotect_branches())
        m_requests_get.assert_called()
        m_requests_put.assert_called()

    def test_update_merge_pull(self):
        id1 = '100'
        id2 = '200'
        number1 = '1'
        number2 = '2'
        self.g.pull_requests = {
            number1: { u'number': int(number1) },
            number2: { u'number': int(number2) },
        }
        self.g.merge_requests = {
            id1: {
                u'id': int(id1),
                u'source_branch': 'pull/' + number1 + '/head',
            },
            id2: {
                u'id': int(id2),
                u'source_branch': 'UNEXPECTED',
            },
        }
        self.g.update_merge_pull()
        self.assertEquals(self.g.merge2pull,
                          {'100': {u'number': 1}})
        self.assertEquals(self.g.pull2merge,
                          {'1': {u'id': 100, u'source_branch': 'pull/1/head'}})


    @mock.patch('requests.post')
    def test_create_merge_request(self, m_requests_post):
        data = { 'title': u'TITLE é' }
        class Request:
            def __init__(self):
                self.status_code = 201

            def json(self):
                return data

        m_requests_post.side_effect = lambda url, params: Request()
        self.g.create_merge_request(data)
        m_requests_post.assert_called()
        
    @mock.patch('requests.post')
    def test_create_merge_request_fail(self, m_requests_post):
        data = { 'title': u'TITLE é' }
        class Request:
            def __init__(self, data):
                self.data = data

            def read(self):
                return {}

        m_requests_post.side_effect = lambda url, data: Request(data)
        self.assertRaises(Exception, self.g.create_merge_request, data)
        m_requests_post.assert_called()

    @mock.patch('requests.put')
    def test_update_merge_request(self, m_requests_put):
        data = {
            'title': u'TITLE é',
            'state_event': 'close',
        }
        class Request:
            def json(self):
                data['state'] = 'closed'
                return data

        m_requests_put.side_effect = lambda url, params: Request()
        merge_request = { 'id': 3 }
        self.g.update_merge_request(merge_request, data)
        m_requests_put.assert_called()
        
    @mock.patch('requests.put')
    def test_update_merge_request_fail_state(self, m_requests_put):
        data = { 'state_event': 'close' }
        class Request:
            def json(self):
                return {
                    'state': 'UNEXPECTED',
                    'iid': 1,
                    'merged': False,
                }

        m_requests_put.side_effect = lambda url, params: Request()
        merge_request = { 'id': 3 }
        self.assertRaisesRegexp(Exception, 'UNEXPECTED',
                                self.g.update_merge_request,
                                merge_request,
                                data)
        m_requests_put.assert_called()

    @mock.patch('github2gitlab.main.GitHub2GitLab.put_merge_request')
    @mock.patch('github2gitlab.main.GitHub2GitLab.verify_merge_update')
    def test_update_merge_request_merge(self,
                                        m_verify_merge_update,
                                        m_put_merge_request):
        description = 'DESCRIPTION'
        def put(merge_request, updates):
            if updates['state_event'] == 'merge':
                updates['state'] = 'opened'
                updates['description'] = description
            else:
                updates['state'] = 'closed'
            return updates

        m_put_merge_request.side_effect = put
        merge_request = { 'id': 3 }
        result = self.g.update_merge_request(merge_request,
                                             { 'state_event': 'merge' })
        self.assertIn(self.g.TAG_MERGED, result['description'])
        m_verify_merge_update.assert_called()
        
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_add_project_create(self,
                                m_requests_post,
                                m_requests_get):
        class Get:
            def __init__(self):
                self.status_code = 404
        m_requests_get.side_effect = lambda url, params: Get()
        class Post:
            def __init__(self):
                self.status_code = 201
                self.text = 'true'

            def json(self):
                return {}
        m_requests_post.side_effect = lambda url, params: Post()
        self.assertEquals({}, self.g.add_project())
        m_requests_get.assert_called()
        m_requests_post.assert_called()

    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_add_project_create_400(self,
                                    m_requests_post,
                                    m_requests_get):
        class Get:
            def __init__(self):
                self.status_code = 404
        m_requests_get.side_effect = lambda url, params: Get()
        error_message = 'ERROR MESSAGE'
        class Post:
            def __init__(self):
                self.status_code = 400
                self.text = error_message
        m_requests_post.side_effect = lambda url, params: Post()
        self.assertRaisesRegexp(ValueError, error_message, self.g.add_project)
        m_requests_get.assert_called()
        m_requests_post.assert_called()

    @mock.patch('requests.get')
    def test_add_project_noop(self, m_requests_get):
        class Get:
            def __init__(self):
                self.status_code = 200
        m_requests_get.side_effect = lambda url, params: Get()
        self.assertEquals(None, self.g.add_project())
        m_requests_get.assert_called()
        
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_add_key_create(self,
                            m_requests_post,
                            m_requests_get):
        public_key = 'PUBLIC KEY'
        ssh_public_key = self.d + "/key.pub"
        with open(ssh_public_key, 'w') as f:
            f.write(public_key)
        self.g.args.ssh_public_key = ssh_public_key
        class Get:
            def json(self):
                return []
        m_requests_get.side_effect = lambda url, params: Get()
        class Post:
            def __init__(self):
                self.status_code = 201
        m_requests_post.side_effect = lambda url, params: Post()
        self.assertEquals(public_key, self.g.add_key())
        m_requests_get.assert_called()
        m_requests_post.assert_called()
        
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_add_key_create_400(self,
                                m_requests_post,
                                m_requests_get):
        public_key = 'PUBLIC KEY'
        ssh_public_key = self.d + "/key.pub"
        with open(ssh_public_key, 'w') as f:
            f.write(public_key)
        self.g.args.ssh_public_key = ssh_public_key
        class Get:
            def json(self):
                return []
        m_requests_get.side_effect = lambda url, params: Get()
        error_message = 'ERROR MESSAGE'
        class Post:
            def __init__(self):
                self.status_code = 400
                self.text = error_message
        m_requests_post.side_effect = lambda url, params: Post()
        self.assertRaisesRegexp(ValueError, error_message, self.g.add_key)
        m_requests_get.assert_called()
        m_requests_post.assert_called()
        
    @mock.patch('requests.get')
    def test_add_key_noop(self, m_requests_get):
        public_key = 'PUBLIC KEY'
        ssh_public_key = self.d + "/key.pub"
        with open(ssh_public_key, 'w') as f:
            f.write(public_key)
        self.g.args.ssh_public_key = ssh_public_key
        class Get:
            def json(self):
                return [{'key': public_key}]
        m_requests_get.side_effect = lambda url, params: Get()
        self.assertEquals(None, self.g.add_key())
        m_requests_get.assert_called()
        
        
    @mock.patch('github2gitlab.main.GitHub2GitLab.update_merge_request')
    @mock.patch('github2gitlab.main.GitHub2GitLab.create_merge_request')
    @mock.patch('github2gitlab.main.GitHub2GitLab.rev_parse')
    def test_sync(self,
                  m_rev_parse,
                  m_create_merge_request,
                  m_update_merge_request):
        m_rev_parse.side_effect = lambda pull, revision: True
        self.g.pull_requests = {
            '1': {
                'number': 1,
                'state': 'open',
                'title': u'TITLE é',
                'body': 'DESCRIPTION è',
                'base': {
                    'ref': 'master',
                },
                'merged_at': None,
            },
            '2': {
                'number': 2,
                'state': 'closed',
                'title': 'OTHER_TITLE',
                'body': 'DESCRIPTION è',
                'merged_at': 'today',
            },
        }
        self.g.merge_requests = {
            '100': {
                'id': 100,
                'state': 'opened',
                'title': u'TITLE é',
                'description': 'DESCRIPTION è',
                'source_branch': 'pull/2/head',
                'target_branch': 'master',
            }
        }
        self.g.update_merge_pull()
        self.assertEquals(1, len(self.g.merge2pull))
        self.assertEquals(2, self.g.merge2pull['100']['number'])
        self.assertEquals(100, self.g.pull2merge['2']['id'])

        self.g.sync()
        m_update_merge_request.assert_called_with(self.g.merge_requests['100'],
                                                  {
                                                      'title': 'OTHER_TITLE',
                                                      'state_event': 'merge',
                                                  })
        pull = self.g.pull_requests['1']
        m_create_merge_request.assert_called_with({
            'title': pull['title'],
            'description': pull['body'],
            'target_branch': pull['base']['ref'],
            'source_branch': 'pull/' + str(pull['number']) + '/head',
        })
    
class TestGitHub2GitLabNoSetup(testtools.TestCase):

    def test_json_loads(self):
        r = main.GitHub2GitLab.json_loads('{}')
        self.assertEquals({}, r)
        self.assertRaises(ValueError, main.GitHub2GitLab.json_loads, ']')
