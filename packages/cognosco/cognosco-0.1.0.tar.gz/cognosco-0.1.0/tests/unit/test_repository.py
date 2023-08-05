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

import unittest

import mock
from six.moves import builtins

from cognosco import exc
from cognosco import repository


class TestException(Exception):
    pass


class RepositoryTest(unittest.TestCase):
    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value='bogus data')
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_str_file(self, mock_init, mock_Auditor, mock_get_handle,
                                mock_safe_load, mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })

        self.assertRaises(TypeError, repository.Repository._load_yaml,
                          ctxt, 'target/path')
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        self.assertFalse(mock_get_handle.called)
        self.assertFalse(ctxt.get.called)
        self.assertFalse(mock_Auditor.called)
        self.assertFalse(ctxt.warn.called)
        self.assertFalse(mock_init.called)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value=123)
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_int_file(self, mock_init, mock_Auditor, mock_get_handle,
                                mock_safe_load, mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })

        self.assertRaises(TypeError, repository.Repository._load_yaml,
                          ctxt, 'target/path')
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        self.assertFalse(mock_get_handle.called)
        self.assertFalse(ctxt.get.called)
        self.assertFalse(mock_Auditor.called)
        self.assertFalse(ctxt.warn.called)
        self.assertFalse(mock_init.called)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={
        'name': 'repo',
    })
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_dict_file(self, mock_init, mock_Auditor,
                                 mock_get_handle, mock_safe_load, mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        repo = gh_handle.get_repo.return_value
        auditor = mock_Auditor.return_value

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo' in result)
        self.assertTrue(isinstance(result['repo'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_called_once_with(
            None, None, 'https://api.github.com')
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        gh_handle.get_repo.assert_called_once_with('repo')
        mock_Auditor.assert_called_once_with()
        self.assertFalse(ctxt.warn.called)
        mock_init.assert_called_once_with(
            'repo', repo, auditor, set(), 'target/path', repo_data)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value=[
        {
            'name': 'repo1',
        },
        {
            'name': 'repo2',
        },
        {
            'name': 'repo3',
        },
    ])
    @mock.patch('cognosco.github_util.get_handle', return_value=mock.Mock())
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_list_file(self, mock_init, mock_Auditor,
                                 mock_get_handle, mock_safe_load, mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        repos = [mock.Mock() for i in range(3)]
        gh_handle.get_repo.side_effect = repos
        auditor = mock_Auditor.return_value

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo1' in result)
        self.assertTrue(isinstance(result['repo1'], repository.Repository))
        self.assertTrue('repo2' in result)
        self.assertTrue(isinstance(result['repo2'], repository.Repository))
        self.assertTrue('repo3' in result)
        self.assertTrue(isinstance(result['repo3'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_has_calls([
            mock.call(None, None, 'https://api.github.com'),
            mock.call(None, None, 'https://api.github.com'),
            mock.call(None, None, 'https://api.github.com'),
        ])
        self.assertEqual(mock_get_handle.call_count, 3)
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 12)
        gh_handle.get_repo.assert_has_calls([
            mock.call('repo1'),
            mock.call('repo2'),
            mock.call('repo3'),
        ])
        self.assertEqual(gh_handle.get_repo.call_count, 3)
        mock_Auditor.assert_has_calls([
            mock.call(),
            mock.call(),
            mock.call(),
        ])
        self.assertEqual(mock_Auditor.call_count, 3)
        self.assertFalse(ctxt.warn.called)
        mock_init.assert_has_calls([
            mock.call('repo%d' % (idx + 1), repos[idx], auditor, set(),
                      'target/path', repo_data[idx])
            for idx in range(3)
        ])
        self.assertEqual(mock_init.call_count, 3)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value=[['bad data']])
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_bad_repodata(self, mock_init, mock_Auditor,
                                    mock_get_handle, mock_safe_load,
                                    mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })

        self.assertRaises(TypeError, repository.Repository._load_yaml,
                          ctxt, 'target/path')
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        self.assertFalse(mock_get_handle.called)
        self.assertFalse(ctxt.get.called)
        self.assertFalse(mock_Auditor.called)
        self.assertFalse(ctxt.warn.called)
        self.assertFalse(mock_init.called)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={})
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_missing_name(self, mock_init, mock_Auditor,
                                    mock_get_handle, mock_safe_load,
                                    mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })

        self.assertRaises(TypeError, repository.Repository._load_yaml,
                          ctxt, 'target/path')
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        self.assertFalse(mock_get_handle.called)
        self.assertFalse(ctxt.get.called)
        self.assertFalse(mock_Auditor.called)
        self.assertFalse(ctxt.warn.called)
        self.assertFalse(mock_init.called)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={
        'name': 'repo',
        'api_url': 'https://some/other/github',
    })
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_override_url(self, mock_init, mock_Auditor,
                                    mock_get_handle, mock_safe_load,
                                    mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        repo = gh_handle.get_repo.return_value
        auditor = mock_Auditor.return_value

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo' in result)
        self.assertTrue(isinstance(result['repo'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_called_once_with(
            None, None, 'https://some/other/github')
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        gh_handle.get_repo.assert_called_once_with('repo')
        mock_Auditor.assert_called_once_with()
        self.assertFalse(ctxt.warn.called)
        mock_init.assert_called_once_with(
            'repo', repo, auditor, set(), 'target/path', repo_data)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={
        'name': 'repo',
        'full_name': 'org/repo',
    })
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_full_name(self, mock_init, mock_Auditor,
                                 mock_get_handle, mock_safe_load, mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        repo = gh_handle.get_repo.return_value
        auditor = mock_Auditor.return_value

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo' in result)
        self.assertTrue(isinstance(result['repo'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_called_once_with(
            None, None, 'https://api.github.com')
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        gh_handle.get_repo.assert_called_once_with('org/repo')
        mock_Auditor.assert_called_once_with()
        self.assertFalse(ctxt.warn.called)
        mock_init.assert_called_once_with(
            'repo', repo, auditor, set(), 'target/path', repo_data)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={
        'name': 'repo',
    })
    @mock.patch('cognosco.github_util.get_handle', return_value=mock.Mock(**{
        'get_repo.side_effect': TestException('some error'),
    }))
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_missing_repo(self, mock_init, mock_Auditor,
                                    mock_get_handle, mock_safe_load,
                                    mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        auditor = mock_Auditor.return_value

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo' in result)
        self.assertTrue(isinstance(result['repo'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_called_once_with(
            None, None, 'https://api.github.com')
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        gh_handle.get_repo.assert_called_once_with('repo')
        mock_Auditor.assert_called_once_with()
        ctxt.warn.assert_called_once_with(
            "Couldn't find repository repo (from target/path): some error")
        mock_init.assert_called_once_with(
            'repo', None, auditor, set(), 'target/path', repo_data)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={
        'name': 'repo',
        'audits': ['a', 'b', 'c'],
    })
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_audits(self, mock_init, mock_Auditor,
                              mock_get_handle, mock_safe_load, mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        repo = gh_handle.get_repo.return_value
        auditor = mock_Auditor.return_value

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo' in result)
        self.assertTrue(isinstance(result['repo'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_called_once_with(
            None, None, 'https://api.github.com')
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        gh_handle.get_repo.assert_called_once_with('repo')
        mock_Auditor.assert_called_once_with('a', 'b', 'c')
        self.assertFalse(ctxt.warn.called)
        mock_init.assert_called_once_with(
            'repo', repo, auditor, set(), 'target/path', repo_data)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={
        'name': 'repo',
        'audits': ['a', 'b', 'c'],
    })
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_missing_audit(self, mock_init, mock_Auditor,
                                     mock_get_handle, mock_safe_load,
                                     mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {
            'audits': ['x', 'y', 'z'],
        }
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        repo = gh_handle.get_repo.return_value
        auditor = mock.Mock()
        mock_Auditor.side_effect = [KeyError('b'), auditor]

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo' in result)
        self.assertTrue(isinstance(result['repo'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_called_once_with(
            None, None, 'https://api.github.com')
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        gh_handle.get_repo.assert_called_once_with('repo')
        mock_Auditor.assert_has_calls([
            mock.call('a', 'b', 'c'),
            mock.call('x', 'y', 'z'),
        ])
        self.assertEqual(mock_Auditor.call_count, 2)
        ctxt.warn.assert_called_once_with(
            "Couldn't load audit 'b' for repository repo (from target/path); "
            "using defaults")
        mock_init.assert_called_once_with(
            'repo', repo, auditor, set(), 'target/path', repo_data)

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_load', return_value={
        'name': 'repo',
        'skip': [1, 3, 5, 7],
    })
    @mock.patch('cognosco.github_util.get_handle')
    @mock.patch('cognosco.audit.Auditor')
    @mock.patch.object(repository.Repository, '__init__', return_value=None)
    def test_load_yaml_skip(self, mock_init, mock_Auditor,
                            mock_get_handle, mock_safe_load, mock_open):
        filemock = mock.MagicMock()
        filemock.__enter__.return_value = filemock
        mock_open.return_value = filemock
        ctxt_data = {}
        ctxt = mock.Mock(**{
            'get.side_effect': lambda x, y=None: ctxt_data.get(x, y),
        })
        repo_data = mock_safe_load.return_value
        gh_handle = mock_get_handle.return_value
        repo = gh_handle.get_repo.return_value
        auditor = mock_Auditor.return_value

        result = repository.Repository._load_yaml(ctxt, 'target/path')

        self.assertTrue(isinstance(result, dict))
        self.assertTrue('repo' in result)
        self.assertTrue(isinstance(result['repo'], repository.Repository))
        mock_open.assert_called_once_with('target/path')
        mock_safe_load.assert_called_once_with(filemock)
        mock_get_handle.assert_called_once_with(
            None, None, 'https://api.github.com')
        ctxt.get.assert_has_calls([
            mock.call('username'),
            mock.call('password'),
            mock.call('url', 'https://api.github.com'),
            mock.call('audits'),
        ])
        self.assertEqual(ctxt.get.call_count, 4)
        gh_handle.get_repo.assert_called_once_with('repo')
        mock_Auditor.assert_called_once_with()
        self.assertFalse(ctxt.warn.called)
        mock_init.assert_called_once_with(
            'repo', repo, auditor, set([1, 3, 5, 7]), 'target/path', repo_data)

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('os.walk', return_value=[])
    @mock.patch.object(repository.Repository, '_load_yaml')
    def test_load_from_file(self, mock_load_yaml, mock_walk, mock_isfile):
        repos = {
            'target/path': {
                'repo1': 'repository1',
                'repo2': 'repository2',
            },
        }
        mock_load_yaml.side_effect = lambda ctxt, target: repos[target]

        result = repository.Repository.load_from('ctxt', 'target/path')

        self.assertEqual(sorted(result), ['repository1', 'repository2'])
        mock_isfile.assert_called_once_with('target/path')
        mock_load_yaml.assert_called_once_with('ctxt', 'target/path')
        self.assertFalse(mock_walk.called)

    @mock.patch('os.path.isfile', return_value=False)
    @mock.patch('os.walk', return_value=[
        ('target/path', ['a', 'b'], ['file1', 'file2.yaml']),
        ('target/path/a', [], ['file3.YAML', 'file4.yaml.gz']),
        ('target/path/b', [], []),
    ])
    @mock.patch.object(repository.Repository, '_load_yaml')
    def test_load_from_dir(self, mock_load_yaml, mock_walk, mock_isfile):
        repos = {
            'target/path': {
                'bad': 'repo',
            },
            'target/path/file1': {
                'bad': 'repo',
            },
            'target/path/file2.yaml': {
                'repo1': 'repository1',
                'repo2': 'repository2',
            },
            'target/path/a': {
                'bad': 'repo',
            },
            'target/path/a/file3.YAML': {
                'repo3': 'repository3',
                'repo4': 'repository4',
            },
            'target/path/a/file4.yaml.gz': {
                'bad': 'repo',
            },
            'target/path/b': {
                'bad': 'repo',
            },
        }
        mock_load_yaml.side_effect = lambda ctxt, target: repos[target]

        result = repository.Repository.load_from('ctxt', 'target/path')

        self.assertEqual(sorted(result), ['repository1', 'repository2',
                                          'repository3', 'repository4'])
        mock_isfile.assert_called_once_with('target/path')
        mock_load_yaml.assert_has_calls([
            mock.call('ctxt', 'target/path/file2.yaml'),
            mock.call('ctxt', 'target/path/a/file3.YAML'),
        ])
        self.assertEqual(mock_load_yaml.call_count, 2)
        mock_walk.assert_called_once_with('target/path')

    @mock.patch('os.path.isfile', return_value=False)
    @mock.patch('os.walk', return_value=[
        ('target/path', ['a'], ['file1.yaml']),
        ('target/path/a', [], ['file2.yaml']),
    ])
    @mock.patch.object(repository.Repository, '_load_yaml')
    def test_load_from_dups(self, mock_load_yaml, mock_walk, mock_isfile):
        repos = {
            'target/path/file1.yaml': {
                'repo1': 'repository1',
                'repo2': 'repository2',
            },
            'target/path/a/file2.yaml': {
                'repo2': 'repository3',
                'repo3': 'repository4',
            },
        }
        mock_load_yaml.side_effect = lambda ctxt, target: repos[target]

        try:
            repository.Repository.load_from('ctxt', 'target/path')
        except exc.DuplicateRepositoryException as ex:
            self.assertEqual(str(ex), 'Duplicate repositories defined '
                             'in target/path')
            self.assertEqual(ex.dups, {
                'repo2': ['repository2', 'repository3'],
            })
        else:
            self.fail('Failed to detect duplicates')

    @mock.patch.object(builtins, 'open')
    @mock.patch('yaml.safe_dump')
    def test_save(self, mock_safe_dump, mock_open):
        filemocks = {
            'file1.yaml': mock.MagicMock(),
            'file2.yaml': mock.MagicMock(),
        }
        for filemock in filemocks.values():
            filemock.__enter__.return_value = filemock
        mock_open.side_effect = lambda x, y: filemocks[x]
        repos = [
            mock.Mock(path=None, raw='repo0'),
            mock.Mock(path='file1.yaml', raw='repo3'),
            mock.Mock(path='file1.yaml', raw='repo2'),
            mock.Mock(path='file2.yaml', raw='repo4'),
            mock.Mock(path='file2.yaml', raw='repo5'),
        ]
        for repo in repos:
            repo.name = repo.raw

        repository.Repository.save(repos)

        mock_open.assert_has_calls([
            mock.call('file1.yaml', 'w'),
            mock.call('file2.yaml', 'w'),
        ], any_order=True)
        self.assertEqual(mock_open.call_count, 2)
        mock_safe_dump.assert_has_calls([
            mock.call(['repo2', 'repo3'], filemocks['file1.yaml']),
            mock.call(['repo4', 'repo5'], filemocks['file2.yaml']),
        ], any_order=True)
        self.assertEqual(mock_safe_dump.call_count, 2)

    def test_init_base(self):
        repo = mock.Mock(full_name='org/repo')

        result = repository.Repository('name', repo, 'auditor')

        self.assertEqual(result.name, 'name')
        self.assertEqual(result.repo, repo)
        self.assertEqual(result.auditor, 'auditor')
        self.assertEqual(result.skip, set())
        self.assertEqual(result.path, None)
        self.assertEqual(result._raw, {'name': 'org/repo'})

    def test_init_alt(self):
        result = repository.Repository('name', 'repo', 'auditor',
                                       [1, 3, 5], 'target/path', 'raw')

        self.assertEqual(result.name, 'name')
        self.assertEqual(result.repo, 'repo')
        self.assertEqual(result.auditor, 'auditor')
        self.assertEqual(result.skip, [1, 3, 5])
        self.assertEqual(result.path, 'target/path')
        self.assertEqual(result._raw, 'raw')

    def test_init_no_repo(self):
        result = repository.Repository('name', None, 'auditor')

        self.assertEqual(result.name, 'name')
        self.assertEqual(result.repo, None)
        self.assertEqual(result.auditor, 'auditor')
        self.assertEqual(result.skip, set())
        self.assertEqual(result.path, None)
        self.assertEqual(result._raw, {})

    def test_audit_base(self):
        failures = [
            (mock.Mock(number=0), ['fail0', 'fail1']),
            (mock.Mock(number=1), ['fail1', 'fail2']),
            (mock.Mock(number=2), []),
            (mock.Mock(number=3), ['fail3', 'fail4']),
        ]
        auditor = mock.Mock(**{'audit_repo.return_value': failures})
        repo = repository.Repository('name', 'repo', auditor, raw='raw')

        result = repo.audit()

        self.assertEqual(result, [f for f in failures if f[1]])
        auditor.audit_repo.assert_called_once_with(
            'repo', None, repo.skip, True)
        self.assertEqual(repo.skip, set([0, 1, 2, 3]))

    def test_audit_no_repo(self):
        failures = [
            (mock.Mock(number=0), ['fail0', 'fail1']),
            (mock.Mock(number=1), ['fail1', 'fail2']),
            (mock.Mock(number=2), []),
            (mock.Mock(number=3), ['fail3', 'fail4']),
        ]
        auditor = mock.Mock(**{'audit_repo.return_value': failures})
        repo = repository.Repository('name', None, auditor, raw='raw')

        result = repo.audit()

        self.assertEqual(result, [])
        self.assertFalse(auditor.audit_repo.called)
        self.assertEqual(repo.skip, set())

    def test_audit_since(self):
        failures = [
            (mock.Mock(number=0), ['fail0', 'fail1']),
            (mock.Mock(number=1), ['fail1', 'fail2']),
            (mock.Mock(number=2), []),
            (mock.Mock(number=3), ['fail3', 'fail4']),
        ]
        auditor = mock.Mock(**{'audit_repo.return_value': failures})
        repo = repository.Repository('name', 'repo', auditor, raw='raw')

        result = repo.audit(since='since')

        self.assertEqual(result, [f for f in failures if f[1]])
        auditor.audit_repo.assert_called_once_with(
            'repo', 'since', repo.skip, True)
        self.assertEqual(repo.skip, set([0, 1, 2, 3]))

    def test_audit_update_skip(self):
        failures = [
            (mock.Mock(number=0), ['fail0', 'fail1']),
            (mock.Mock(number=1), ['fail1', 'fail2']),
            (mock.Mock(number=2), []),
            (mock.Mock(number=3), ['fail3', 'fail4']),
        ]
        auditor = mock.Mock(**{'audit_repo.return_value': failures})
        repo = repository.Repository('name', 'repo', auditor, raw='raw')

        result = repo.audit(update_skip=False)

        self.assertEqual(result, failures)
        auditor.audit_repo.assert_called_once_with(
            'repo', None, repo.skip, False)
        self.assertEqual(repo.skip, set())

    def test_audit_all_checked(self):
        failures = [
            (mock.Mock(number=0), ['fail0', 'fail1']),
            (mock.Mock(number=1), ['fail1', 'fail2']),
            (mock.Mock(number=2), []),
            (mock.Mock(number=3), ['fail3', 'fail4']),
        ]
        auditor = mock.Mock(**{'audit_repo.return_value': failures})
        repo = repository.Repository('name', 'repo', auditor, raw='raw')

        result = repo.audit(all_checked=True)

        self.assertEqual(result, failures)
        auditor.audit_repo.assert_called_once_with(
            'repo', None, repo.skip, True)
        self.assertEqual(repo.skip, set([0, 1, 2, 3]))

    def test_audit_no_update_skip_but_all_checked(self):
        failures = [
            (mock.Mock(number=0), ['fail0', 'fail1']),
            (mock.Mock(number=1), ['fail1', 'fail2']),
            (mock.Mock(number=2), []),
            (mock.Mock(number=3), ['fail3', 'fail4']),
        ]
        auditor = mock.Mock(**{'audit_repo.return_value': failures})
        repo = repository.Repository('name', 'repo', auditor, raw='raw')

        result = repo.audit(update_skip=False, all_checked=True)

        self.assertEqual(result, failures)
        auditor.audit_repo.assert_called_once_with(
            'repo', None, repo.skip, True)
        self.assertEqual(repo.skip, set())

    def test_raw(self):
        repo = repository.Repository('name', 'repo', 'auditor',
                                     skip=set([1, 3, 5]), raw={})

        self.assertEqual(repo.raw, {'skip': [1, 3, 5]})
        self.assertEqual(repo._raw, {'skip': [1, 3, 5]})
