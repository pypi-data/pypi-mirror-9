# Copyright 2014 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the
#    License. You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an "AS
#    IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#    express or implied. See the License for the specific language
#    governing permissions and limitations under the License.

import datetime
import sys
import unittest

import mock
import six
from six.moves import builtins

from cognosco import exc
from cognosco import reports


class ContextTest(unittest.TestCase):
    def test_init(self):
        args = mock.Mock(username='user', password='pass', github_url='url',
                         audits='audits')

        result = reports.Context(args)

        self.assertEqual(result.username, 'user')
        self.assertEqual(result.password, 'pass')
        self.assertEqual(result.url, 'url')
        self.assertEqual(result.audits, 'audits')

    def test_get_available(self):
        args = mock.Mock(username='user', password='pass', github_url='url',
                         audits='audits')
        ctxt = reports.Context(args)

        self.assertEqual(ctxt.get('username'), 'user')
        self.assertEqual(ctxt.get('password'), 'pass')
        self.assertEqual(ctxt.get('url'), 'url')
        self.assertEqual(ctxt.get('audits'), 'audits')

    def test_get_available_unset(self):
        args = mock.Mock(username=None, password=None, github_url=None,
                         audits=None)
        ctxt = reports.Context(args)

        self.assertEqual(ctxt.get('username'), None)
        self.assertEqual(ctxt.get('password', 'def_pass'), 'def_pass')
        self.assertEqual(ctxt.get('url'), None)
        self.assertEqual(ctxt.get('audits', []), [])

    def test_get_unavailable(self):
        args = mock.Mock(username='user', password='pass', github_url='url',
                         audits='audits')
        ctxt = reports.Context(args)

        self.assertEqual(ctxt.get('unavailable'), None)
        self.assertEqual(ctxt.get('unavailable', 'default'), 'default')

    @mock.patch.object(sys, 'stderr', six.StringIO())
    def test_warn(self):
        args = mock.Mock(username='user', password='pass', github_url='url',
                         audits='audits')
        ctxt = reports.Context(args)

        ctxt.warn('test warning message')

        self.assertEqual(sys.stderr.getvalue(),
                         'WARNING: test warning message\n')


class FormatAgeTest(unittest.TestCase):
    def test_normal(self):
        now = datetime.datetime(2000, 1, 1, 0, 0, 0)
        time = datetime.datetime(1999, 12, 31, 0, 0, 0)

        result = reports.format_age(now, time, "<%s>")

        self.assertEqual(result, '<1 day, 0:00:00>')

    def test_equal(self):
        now = datetime.datetime(2000, 1, 1, 0, 0, 0)
        time = datetime.datetime(2000, 1, 1, 0, 0, 0)

        result = reports.format_age(now, time, "<%s>")

        self.assertEqual(result, '')

    def test_negative(self):
        now = datetime.datetime(2000, 1, 1, 0, 0, 0)
        time = datetime.datetime(2000, 1, 2, 0, 0, 0)

        result = reports.format_age(now, time, "<%s>")

        self.assertEqual(result, '')


class MakeReposTest(unittest.TestCase):
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.repository.Repository',
                side_effect=lambda x, y, z: x)
    def test_basic(self, mock_Repository, mock_get_handle, mock_Auditor):
        ctxt_data = {
            'username': 'user',
            'password': 'pass',
            'url': 'url',
            'audits': ['audit1', 'audit2'],
        }
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repos = [
            mock.Mock(full_name='repo1'),
            mock.Mock(full_name='repo2'),
            mock.Mock(full_name='repo3'),
        ]
        get_repos = mock.Mock(return_value=repos)

        result = reports._make_repos(ctxt, 'name', get_repos)

        self.assertEqual(result, ['repo1', 'repo2', 'repo3'])
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        mock_get_handle.assert_called_once_with('user', 'pass', 'url')
        mock_Auditor.assert_called_once_with('audit1', 'audit2')
        self.assertFalse(ctxt.warn.called)
        mock_Repository.assert_has_calls([
            mock.call('repo1', repos[0], mock_Auditor.return_value),
            mock.call('repo2', repos[1], mock_Auditor.return_value),
            mock.call('repo3', repos[2], mock_Auditor.return_value),
        ])
        self.assertEqual(mock_Repository.call_count, 3)

    @mock.patch('cognosco.audit.Auditor')
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.repository.Repository',
                side_effect=lambda x, y, z: x)
    def test_default_audits(self, mock_Repository, mock_get_handle,
                            mock_Auditor):
        ctxt_data = {
            'username': 'user',
            'password': 'pass',
            'url': 'url',
        }
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repos = [
            mock.Mock(full_name='repo1'),
            mock.Mock(full_name='repo2'),
            mock.Mock(full_name='repo3'),
        ]
        get_repos = mock.Mock(return_value=repos)

        result = reports._make_repos(ctxt, 'name', get_repos)

        self.assertEqual(result, ['repo1', 'repo2', 'repo3'])
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        mock_get_handle.assert_called_once_with('user', 'pass', 'url')
        mock_Auditor.assert_called_once_with()
        self.assertFalse(ctxt.warn.called)
        mock_Repository.assert_has_calls([
            mock.call('repo1', repos[0], mock_Auditor.return_value),
            mock.call('repo2', repos[1], mock_Auditor.return_value),
            mock.call('repo3', repos[2], mock_Auditor.return_value),
        ])
        self.assertEqual(mock_Repository.call_count, 3)

    @mock.patch('cognosco.audit.Auditor',
                side_effect=[KeyError('audit2'), 'auditor'])
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.repository.Repository',
                side_effect=lambda x, y, z: x)
    def test_warn(self, mock_Repository, mock_get_handle, mock_Auditor):
        ctxt_data = {
            'username': 'user',
            'password': 'pass',
            'url': 'url',
            'audits': ['audit1', 'audit2'],
        }
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repos = [
            mock.Mock(full_name='repo1'),
            mock.Mock(full_name='repo2'),
            mock.Mock(full_name='repo3'),
        ]
        get_repos = mock.Mock(return_value=repos)

        result = reports._make_repos(ctxt, 'name', get_repos)

        self.assertEqual(result, ['repo1', 'repo2', 'repo3'])
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        mock_get_handle.assert_called_once_with('user', 'pass', 'url')
        mock_Auditor.assert_has_calls([
            mock.call('audit1', 'audit2'),
            mock.call(),
        ])
        self.assertEqual(mock_Auditor.call_count, 2)
        ctxt.warn.assert_called_once_with(
            "Couldn't load audit 'audit2' for repository source name "
            "(from command line); using defaults")
        mock_Repository.assert_has_calls([
            mock.call('repo1', repos[0], 'auditor'),
            mock.call('repo2', repos[1], 'auditor'),
            mock.call('repo3', repos[2], 'auditor'),
        ])
        self.assertEqual(mock_Repository.call_count, 3)


class TargetsTest(unittest.TestCase):
    def call_target(self, gh, target, name, expected):
        fake_make_repos = lambda ctxt, name, get_repos: get_repos(gh, name)

        with mock.patch.object(reports, '_make_repos',
                               side_effect=fake_make_repos) as mock_make_repos:
            result = reports.targets[target]('ctxt', name)

        self.assertEqual(result, expected)
        mock_make_repos.assert_called_once_with('ctxt', name, mock.ANY)

    def test_repo(self):
        gh = mock.Mock(**{
            'get_repo.return_value': 'repo',
        })

        self.call_target(gh, 'repo', 'name', ['repo'])
        gh.get_repo.assert_called_once_with('name')

    def test_org(self):
        expected = ['repo1', 'repo2', 'repo3']
        gh = mock.Mock(**{
            'get_organization.return_value.get_repos.return_value': expected,
        })

        self.call_target(gh, 'org', 'name', expected)
        gh.get_organization.assert_called_once_with('name')
        gh.get_organization.return_value.get_repos.assert_called_once_with()

    def test_user(self):
        expected = ['repo1', 'repo2', 'repo3']
        gh = mock.Mock(**{
            'get_user.return_value.get_repos.return_value': expected,
        })

        self.call_target(gh, 'user', 'name', expected)
        gh.get_user.assert_called_once_with('name')
        gh.get_user.return_value.get_repos.assert_called_once_with()


class RepoActionTest(unittest.TestCase):
    @mock.patch('argparse.Action.__init__', return_value=None)
    def test_init_no_target(self, mock_init):
        result = reports.RepoAction('strings', 'dest', a=1, b=2, c=3)

        self.assertEqual(result.target, 'repo')
        mock_init.assert_called_once_with('strings', 'dest', a=1, b=2, c=3)

    @mock.patch('argparse.Action.__init__', return_value=None)
    def test_init_with_target(self, mock_init):
        result = reports.RepoAction('strings', 'dest', a=1, b=2, c=3,
                                    target='org')

        self.assertEqual(result.target, 'org')
        mock_init.assert_called_once_with('strings', 'dest', a=1, b=2, c=3)

    @mock.patch('argparse.Action.__init__', return_value=None)
    def test_call(self, mock_init):
        action = reports.RepoAction('strings', 'dest', target='user')
        action.dest = 'dest'
        namespace = mock.Mock(spec=[])

        action('parser', namespace, 'spam')
        action('parser', namespace, 'foo')

        self.assertEqual(namespace.dest, [('user', 'spam'), ('user', 'foo')])


class TimeActionTest(unittest.TestCase):
    @mock.patch('argparse.Action.__init__', return_value=None)
    @mock.patch('timestring.Date', return_value=mock.Mock(date='date'))
    def test_call(self, mock_Date, mock_init):
        action = reports.TimeAction()
        action.dest = 'dest'
        namespace = mock.Mock()

        action('parser', namespace, 'user-provided date')

        self.assertEqual(namespace.dest, 'date')
        mock_Date.assert_called_once_with('user-provided date')


class PerformAuditTest(unittest.TestCase):
    @mock.patch.dict(reports.targets, clear=True)
    @mock.patch('datetime.datetime', mock.Mock(utcnow=mock.Mock(side_effect=[
        80,
        82,
    ])))
    @mock.patch('cognosco.repository.Repository.save')
    @mock.patch.object(reports, 'format_age',
                       side_effect=lambda x, y, z: z % (x - y))
    def test_empty_report(self, mock_format_age, mock_save):
        ctxt = mock.Mock()
        repos = []
        stream = six.StringIO()

        reports.perform_audit(ctxt, repos, stream=stream)

        self.assertFalse(ctxt.warn.called)
        self.assertFalse(mock_format_age.called)
        self.assertEqual(
            stream.getvalue(),
            u'Audit report generated in 2 at 80\n'
            u'Found 0 policy violations in 0 merged pull requests\n')
        self.assertFalse(mock_save.called)

    @mock.patch.dict(reports.targets, clear=True)
    @mock.patch('datetime.datetime', mock.Mock(utcnow=mock.Mock(side_effect=[
        80,
        82,
    ])))
    @mock.patch('cognosco.repository.Repository.save')
    @mock.patch.object(reports, 'format_age',
                       side_effect=lambda x, y, z: z % (x - y))
    def test_config_duplicate(self, mock_format_age, mock_save):
        reports.targets['config'] = mock.Mock(
            side_effect=exc.DuplicateRepositoryException(
                'Duplicate repositories defined in target',
                dups={
                    'repo1': [
                        mock.Mock(path='/path/1'),
                        mock.Mock(path='/path/2'),
                    ],
                    'repo2': [
                        mock.Mock(path='/path/3'),
                        mock.Mock(path='/path/4'),
                        mock.Mock(path='/path/5'),
                    ],
                }))
        ctxt = mock.Mock()
        repos = [('config', 'target')]
        stream = six.StringIO()

        self.assertRaises(exc.AuditException, reports.perform_audit,
                          ctxt, repos, stream=stream)
        reports.targets['config'].assert_called_once_with(ctxt, 'target')
        ctxt.warn.assert_has_calls([
            mock.call('Duplicate repositories defined in target'),
            mock.call('Repository repo1 present from: /path/1, /path/2'),
            mock.call(
                'Repository repo2 present from: /path/3, /path/4, /path/5'),
        ])
        self.assertEqual(ctxt.warn.call_count, 3)
        self.assertFalse(mock_format_age.called)
        self.assertEqual(stream.getvalue(), '')
        self.assertFalse(mock_save.called)

    @mock.patch.dict(reports.targets, clear=True)
    @mock.patch('datetime.datetime', mock.Mock(utcnow=mock.Mock(side_effect=[
        80,
        82,
    ])))
    @mock.patch('cognosco.repository.Repository.save')
    @mock.patch.object(reports, 'format_age',
                       side_effect=lambda x, y, z: z % (x - y))
    def test_cli_duplicate(self, mock_format_age, mock_save):
        repo_dict = {
            'repo1': mock.Mock(),
            'repo2': mock.Mock(),
            'repo3': mock.Mock(),
        }
        for name, repo in repo_dict.items():
            repo.name = name
        reports.targets.update(
            config=mock.Mock(return_value=repo_dict.values()),
            repo=mock.Mock(return_value=[repo_dict['repo1']]),
        )
        ctxt = mock.Mock()
        repos = [('config', 'target'), ('repo', 'r_name')]
        stream = six.StringIO()

        self.assertRaises(exc.AuditException, reports.perform_audit,
                          ctxt, repos, stream=stream)
        reports.targets['config'].assert_called_once_with(ctxt, 'target')
        reports.targets['repo'].assert_called_once_with(ctxt, 'r_name')
        self.assertFalse(ctxt.warn.called)
        self.assertFalse(mock_format_age.called)
        self.assertEqual(stream.getvalue(), '')
        self.assertFalse(mock_save.called)

    @mock.patch.dict(reports.targets, clear=True)
    @mock.patch('datetime.datetime', mock.Mock(utcnow=mock.Mock(side_effect=[
        80,
        82,
    ])))
    @mock.patch('cognosco.repository.Repository.save')
    @mock.patch.object(reports, 'format_age',
                       side_effect=lambda x, y, z: z % (x - y))
    def test_normal_audit(self, mock_format_age, mock_save):
        repo_dict = {
            'repo1': mock.Mock(**{
                'repo.full_name': 'repo_1',
                'audit.return_value': [],
            }),
            'repo2': mock.Mock(**{
                'repo.full_name': 'repo_2',
                'audit.return_value': [
                    (mock.Mock(**{
                        'number': 5,
                        'html_url': 'http://github/repo2/5',
                        'user.name': None,
                        'user.login': 'user',
                        'created_at': 70,
                        'merged_by.name': None,
                        'merged_by.login': 'merged_by',
                        'merged_at': 75,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit3',
                            '__str__': mock.Mock(return_value='audit 3'),
                        }),
                        mock.Mock(**{
                            'audit': 'audit2',
                            '__str__': mock.Mock(return_value='audit 2'),
                        }),
                        mock.Mock(**{
                            'audit': 'audit1',
                            '__str__': mock.Mock(return_value='audit 1'),
                        }),
                    ]),
                    (mock.Mock(**{
                        'number': 3,
                        'html_url': 'http://github/repo2/3',
                        'user.name': None,
                        'user.login': 'user',
                        'created_at': 60,
                        'merged_by.name': None,
                        'merged_by.login': 'merged_by',
                        'merged_at': 65,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit3',
                            '__str__': mock.Mock(return_value='audit 3'),
                        }),
                    ]),
                ],
            }),
            'repo3': mock.Mock(**{
                'repo.full_name': 'repo_3',
                'audit.return_value': [
                    (mock.Mock(**{
                        'number': 5,
                        'html_url': 'http://github/repo3/5',
                        'user.name': 'Proposer',
                        'user.login': 'user',
                        'created_at': 70,
                        'merged_by.name': 'Merger',
                        'merged_by.login': 'merged_by',
                        'merged_at': 75,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit1',
                            '__str__': mock.Mock(
                                return_value='A very very long text intended '
                                'to introduce some text wrapping to validate '
                                'that textwrap.fill() does the expected sort '
                                'of wrapping.'),
                        }),
                    ]),
                ],
            }),
        }
        for name, repo in repo_dict.items():
            repo.name = name
        reports.targets['config'] = mock.Mock(return_value=repo_dict.values())
        ctxt = mock.Mock()
        repos = [('config', 'target')]
        stream = six.StringIO()

        reports.perform_audit(ctxt, repos, stream=stream)

        reports.targets['config'].assert_called_once_with(ctxt, 'target')
        self.assertFalse(ctxt.warn.called)
        mock_format_age.assert_has_calls([
            mock.call(80, 60, ' (age: %s)'),
            mock.call(80, 65, ' (%s ago)'),
            mock.call(80, 70, ' (age: %s)'),
            mock.call(80, 75, ' (%s ago)'),
            mock.call(80, 70, ' (age: %s)'),
            mock.call(80, 75, ' (%s ago)'),
        ])
        self.assertEqual(mock_format_age.call_count, 6)
        self.assertEqual(
            stream.getvalue(),
            u'repo_2:\n'
            u'  Pull request 3:\n'
            u'    URL: http://github/repo2/3\n'
            u'    Proposed by <unknown> (user)\n'
            u'    Proposed at 60 (age: 20)\n'
            u'    Merged by <unknown> (merged_by)\n'
            u'    Merged at 65 (15 ago)\n'
            u'    Count of policy failures: 1\n'
            u'      - audit 3\n'
            u'\n'
            u'  Pull request 5:\n'
            u'    URL: http://github/repo2/5\n'
            u'    Proposed by <unknown> (user)\n'
            u'    Proposed at 70 (age: 10)\n'
            u'    Merged by <unknown> (merged_by)\n'
            u'    Merged at 75 (5 ago)\n'
            u'    Count of policy failures: 3\n'
            u'      - audit 1\n'
            u'      - audit 2\n'
            u'      - audit 3\n'
            u'\n'
            u'repo_3:\n'
            u'  Pull request 5:\n'
            u'    URL: http://github/repo3/5\n'
            u'    Proposed by Proposer (user)\n'
            u'    Proposed at 70 (age: 10)\n'
            u'    Merged by Merger (merged_by)\n'
            u'    Merged at 75 (5 ago)\n'
            u'    Count of policy failures: 1\n'
            u'      - A very very long text intended to introduce some '
            u'text wrapping\n'
            u'        to validate that textwrap.fill() does the expected '
            u'sort of\n'
            u'        wrapping.\n'
            u'\n'
            u'Audit report generated in 2 at 80\n'
            u'Found 5 policy violations in 3 merged pull requests\n')
        self.assertFalse(mock_save.called)
        for repo in repo_dict.values():
            repo.audit.assert_called_once_with(None, False)

    @mock.patch.dict(reports.targets, clear=True)
    @mock.patch('datetime.datetime', mock.Mock(utcnow=mock.Mock(side_effect=[
        80,
        82,
    ])))
    @mock.patch('cognosco.repository.Repository.save')
    @mock.patch.object(reports, 'format_age',
                       side_effect=lambda x, y, z: z % (x - y))
    def test_since_audit(self, mock_format_age, mock_save):
        repo_dict = {
            'repo1': mock.Mock(**{
                'repo.full_name': 'repo_1',
                'audit.return_value': [],
            }),
            'repo2': mock.Mock(**{
                'repo.full_name': 'repo_2',
                'audit.return_value': [
                    (mock.Mock(**{
                        'number': 5,
                        'html_url': 'http://github/repo2/5',
                        'user.name': None,
                        'user.login': 'user',
                        'created_at': 70,
                        'merged_by.name': None,
                        'merged_by.login': 'merged_by',
                        'merged_at': 75,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit3',
                            '__str__': mock.Mock(return_value='audit 3'),
                        }),
                        mock.Mock(**{
                            'audit': 'audit2',
                            '__str__': mock.Mock(return_value='audit 2'),
                        }),
                        mock.Mock(**{
                            'audit': 'audit1',
                            '__str__': mock.Mock(return_value='audit 1'),
                        }),
                    ]),
                    (mock.Mock(**{
                        'number': 3,
                        'html_url': 'http://github/repo2/3',
                        'user.name': None,
                        'user.login': 'user',
                        'created_at': 60,
                        'merged_by.name': None,
                        'merged_by.login': 'merged_by',
                        'merged_at': 65,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit3',
                            '__str__': mock.Mock(return_value='audit 3'),
                        }),
                    ]),
                ],
            }),
            'repo3': mock.Mock(**{
                'repo.full_name': 'repo_3',
                'audit.return_value': [
                    (mock.Mock(**{
                        'number': 5,
                        'html_url': 'http://github/repo3/5',
                        'user.name': 'Proposer',
                        'user.login': 'user',
                        'created_at': 70,
                        'merged_by.name': 'Merger',
                        'merged_by.login': 'merged_by',
                        'merged_at': 75,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit1',
                            '__str__': mock.Mock(
                                return_value='A very very long text intended '
                                'to introduce some text wrapping to validate '
                                'that textwrap.fill() does the expected sort '
                                'of wrapping.'),
                        }),
                    ]),
                ],
            }),
        }
        for name, repo in repo_dict.items():
            repo.name = name
        reports.targets['config'] = mock.Mock(return_value=repo_dict.values())
        ctxt = mock.Mock()
        repos = [('config', 'target')]
        stream = six.StringIO()

        reports.perform_audit(ctxt, repos, since=50, stream=stream)

        reports.targets['config'].assert_called_once_with(ctxt, 'target')
        self.assertFalse(ctxt.warn.called)
        mock_format_age.assert_has_calls([
            mock.call(80, 60, ' (age: %s)'),
            mock.call(80, 65, ' (%s ago)'),
            mock.call(80, 70, ' (age: %s)'),
            mock.call(80, 75, ' (%s ago)'),
            mock.call(80, 70, ' (age: %s)'),
            mock.call(80, 75, ' (%s ago)'),
        ])
        self.assertEqual(mock_format_age.call_count, 6)
        self.assertEqual(
            stream.getvalue(),
            u'repo_2:\n'
            u'  Pull request 3:\n'
            u'    URL: http://github/repo2/3\n'
            u'    Proposed by <unknown> (user)\n'
            u'    Proposed at 60 (age: 20)\n'
            u'    Merged by <unknown> (merged_by)\n'
            u'    Merged at 65 (15 ago)\n'
            u'    Count of policy failures: 1\n'
            u'      - audit 3\n'
            u'\n'
            u'  Pull request 5:\n'
            u'    URL: http://github/repo2/5\n'
            u'    Proposed by <unknown> (user)\n'
            u'    Proposed at 70 (age: 10)\n'
            u'    Merged by <unknown> (merged_by)\n'
            u'    Merged at 75 (5 ago)\n'
            u'    Count of policy failures: 3\n'
            u'      - audit 1\n'
            u'      - audit 2\n'
            u'      - audit 3\n'
            u'\n'
            u'repo_3:\n'
            u'  Pull request 5:\n'
            u'    URL: http://github/repo3/5\n'
            u'    Proposed by Proposer (user)\n'
            u'    Proposed at 70 (age: 10)\n'
            u'    Merged by Merger (merged_by)\n'
            u'    Merged at 75 (5 ago)\n'
            u'    Count of policy failures: 1\n'
            u'      - A very very long text intended to introduce some '
            u'text wrapping\n'
            u'        to validate that textwrap.fill() does the expected '
            u'sort of\n'
            u'        wrapping.\n'
            u'\n'
            u'Audit report generated in 2 at 80\n'
            u'Found 5 policy violations in 3 merged pull requests\n')
        self.assertFalse(mock_save.called)
        for repo in repo_dict.values():
            repo.audit.assert_called_once_with(50, False)

    @mock.patch.dict(reports.targets, clear=True)
    @mock.patch('datetime.datetime', mock.Mock(utcnow=mock.Mock(side_effect=[
        80,
        82,
    ])))
    @mock.patch('cognosco.repository.Repository.save')
    @mock.patch.object(reports, 'format_age',
                       side_effect=lambda x, y, z: z % (x - y))
    def test_update_audit(self, mock_format_age, mock_save):
        repo_dict = {
            'repo1': mock.Mock(**{
                'repo.full_name': 'repo_1',
                'audit.return_value': [],
            }),
            'repo2': mock.Mock(**{
                'repo.full_name': 'repo_2',
                'audit.return_value': [
                    (mock.Mock(**{
                        'number': 5,
                        'html_url': 'http://github/repo2/5',
                        'user.name': None,
                        'user.login': 'user',
                        'created_at': 70,
                        'merged_by.name': None,
                        'merged_by.login': 'merged_by',
                        'merged_at': 75,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit3',
                            '__str__': mock.Mock(return_value='audit 3'),
                        }),
                        mock.Mock(**{
                            'audit': 'audit2',
                            '__str__': mock.Mock(return_value='audit 2'),
                        }),
                        mock.Mock(**{
                            'audit': 'audit1',
                            '__str__': mock.Mock(return_value='audit 1'),
                        }),
                    ]),
                    (mock.Mock(**{
                        'number': 3,
                        'html_url': 'http://github/repo2/3',
                        'user.name': None,
                        'user.login': 'user',
                        'created_at': 60,
                        'merged_by.name': None,
                        'merged_by.login': 'merged_by',
                        'merged_at': 65,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit3',
                            '__str__': mock.Mock(return_value='audit 3'),
                        }),
                    ]),
                ],
            }),
            'repo3': mock.Mock(**{
                'repo.full_name': 'repo_3',
                'audit.return_value': [
                    (mock.Mock(**{
                        'number': 5,
                        'html_url': 'http://github/repo3/5',
                        'user.name': 'Proposer',
                        'user.login': 'user',
                        'created_at': 70,
                        'merged_by.name': 'Merger',
                        'merged_by.login': 'merged_by',
                        'merged_at': 75,
                    }), [
                        mock.Mock(**{
                            'audit': 'audit1',
                            '__str__': mock.Mock(
                                return_value='A very very long text intended '
                                'to introduce some text wrapping to validate '
                                'that textwrap.fill() does the expected sort '
                                'of wrapping.'),
                        }),
                    ]),
                ],
            }),
        }
        for name, repo in repo_dict.items():
            repo.name = name
        reports.targets['config'] = mock.Mock(return_value=repo_dict.values())
        ctxt = mock.Mock()
        repos = [('config', 'target')]
        stream = six.StringIO()

        reports.perform_audit(ctxt, repos, stream=stream, update=True)

        reports.targets['config'].assert_called_once_with(ctxt, 'target')
        self.assertFalse(ctxt.warn.called)
        mock_format_age.assert_has_calls([
            mock.call(80, 60, ' (age: %s)'),
            mock.call(80, 65, ' (%s ago)'),
            mock.call(80, 70, ' (age: %s)'),
            mock.call(80, 75, ' (%s ago)'),
            mock.call(80, 70, ' (age: %s)'),
            mock.call(80, 75, ' (%s ago)'),
        ])
        self.assertEqual(mock_format_age.call_count, 6)
        self.assertEqual(
            stream.getvalue(),
            u'repo_2:\n'
            u'  Pull request 3:\n'
            u'    URL: http://github/repo2/3\n'
            u'    Proposed by <unknown> (user)\n'
            u'    Proposed at 60 (age: 20)\n'
            u'    Merged by <unknown> (merged_by)\n'
            u'    Merged at 65 (15 ago)\n'
            u'    Count of policy failures: 1\n'
            u'      - audit 3\n'
            u'\n'
            u'  Pull request 5:\n'
            u'    URL: http://github/repo2/5\n'
            u'    Proposed by <unknown> (user)\n'
            u'    Proposed at 70 (age: 10)\n'
            u'    Merged by <unknown> (merged_by)\n'
            u'    Merged at 75 (5 ago)\n'
            u'    Count of policy failures: 3\n'
            u'      - audit 1\n'
            u'      - audit 2\n'
            u'      - audit 3\n'
            u'\n'
            u'repo_3:\n'
            u'  Pull request 5:\n'
            u'    URL: http://github/repo3/5\n'
            u'    Proposed by Proposer (user)\n'
            u'    Proposed at 70 (age: 10)\n'
            u'    Merged by Merger (merged_by)\n'
            u'    Merged at 75 (5 ago)\n'
            u'    Count of policy failures: 1\n'
            u'      - A very very long text intended to introduce some '
            u'text wrapping\n'
            u'        to validate that textwrap.fill() does the expected '
            u'sort of\n'
            u'        wrapping.\n'
            u'\n'
            u'Audit report generated in 2 at 80\n'
            u'Found 5 policy violations in 3 merged pull requests\n')
        mock_save.assert_called_once_with(
            [v for k, v in sorted(repo_dict.items(), key=lambda x: x[0])])
        for repo in repo_dict.values():
            repo.audit.assert_called_once_with(None, True)


class ProcessPerformAuditTest(unittest.TestCase):
    @mock.patch('github.enable_console_debug_logging')
    @mock.patch.object(reports, 'Context')
    @mock.patch('io.open')
    @mock.patch('sys.stdout', mock.Mock())
    def test_basic(self, mock_open, mock_Context,
                   mock_enable_console_debug_logging):
        args = mock.Mock(debug=False, output='-')

        gen = reports._process_perform_audit(args)
        next(gen)

        self.assertEqual(args.ctxt, mock_Context.return_value)
        self.assertEqual(args.stream, sys.stdout)
        self.assertFalse(mock_enable_console_debug_logging.called)
        mock_Context.assert_called_once_with(args)
        self.assertFalse(mock_open.called)
        self.assertFalse(sys.stdout.close.called)

        try:
            next(gen)
        except StopIteration:
            pass
        else:
            self.fail('Failed to end iteration')

        self.assertFalse(sys.stdout.close.called)

    @mock.patch('github.enable_console_debug_logging')
    @mock.patch.object(reports, 'Context')
    @mock.patch('io.open')
    @mock.patch('sys.stdout', mock.Mock())
    def test_output(self, mock_open, mock_Context,
                    mock_enable_console_debug_logging):
        args = mock.Mock(debug=False, output='output')

        gen = reports._process_perform_audit(args)
        next(gen)

        self.assertEqual(args.ctxt, mock_Context.return_value)
        self.assertEqual(args.stream, mock_open.return_value)
        self.assertFalse(mock_enable_console_debug_logging.called)
        mock_Context.assert_called_once_with(args)
        mock_open.assert_called_once_with('output', 'w', encoding='utf-8')
        self.assertFalse(mock_open.return_value.close.called)

        try:
            next(gen)
        except StopIteration:
            pass
        else:
            self.fail('Failed to end iteration')

        mock_open.return_value.close.assert_called_once_with()

    @mock.patch('github.enable_console_debug_logging')
    @mock.patch.object(reports, 'Context')
    @mock.patch('io.open')
    @mock.patch('sys.stdout', mock.Mock())
    def test_debug(self, mock_open, mock_Context,
                   mock_enable_console_debug_logging):
        args = mock.Mock(debug=True, output='-')

        gen = reports._process_perform_audit(args)
        next(gen)

        self.assertEqual(args.ctxt, mock_Context.return_value)
        self.assertEqual(args.stream, sys.stdout)
        mock_enable_console_debug_logging.assert_called_once_with()
        mock_Context.assert_called_once_with(args)
        self.assertFalse(mock_open.called)
        self.assertFalse(sys.stdout.close.called)

        try:
            next(gen)
        except StopIteration:
            pass
        else:
            self.fail('Failed to end iteration')

        self.assertFalse(sys.stdout.close.called)
