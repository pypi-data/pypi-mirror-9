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

from cognosco import github_util


class GetHandleTest(unittest.TestCase):
    @mock.patch.dict(github_util._handles)
    @mock.patch('getpass.getuser', return_value='sysuser')
    @mock.patch('getpass.getpass', return_value='prompted')
    @mock.patch('github.Github')
    def test_no_args(self, mock_Github, mock_getpass, mock_getuser):
        handle = github_util.get_handle()

        self.assertEqual(handle, mock_Github.return_value)
        self.assertEqual(github_util._handles, {
            ('sysuser', 'https://api.github.com/'): handle,
        })
        mock_getuser.assert_called_once_with()
        mock_getpass.assert_called_once_with(
            'Password for sysuser at https://api.github.com/> ')
        mock_Github.assert_called_once_with(
            'sysuser', 'prompted', 'https://api.github.com/')

    @mock.patch.dict(github_util._handles)
    @mock.patch('getpass.getuser', return_value='sysuser')
    @mock.patch('getpass.getpass', return_value='prompted')
    @mock.patch('github.Github')
    def test_no_args_cached(self, mock_Github, mock_getpass, mock_getuser):
        github_util._handles[('sysuser', 'https://api.github.com/')] = 'cached'

        handle = github_util.get_handle()

        self.assertEqual(handle, 'cached')
        self.assertEqual(github_util._handles, {
            ('sysuser', 'https://api.github.com/'): 'cached',
        })
        mock_getuser.assert_called_once_with()
        mock_getpass.assert_called_once_with(
            'Password for sysuser at https://api.github.com/> ')
        self.assertFalse(mock_Github.called)

    @mock.patch.dict(github_util._handles)
    @mock.patch('getpass.getuser', return_value='sysuser')
    @mock.patch('getpass.getpass', return_value='prompted')
    @mock.patch('github.Github')
    def test_all_args(self, mock_Github, mock_getpass, mock_getuser):
        handle = github_util.get_handle(
            'username', 'password', 'http://some:283/random//url/')

        self.assertEqual(handle, mock_Github.return_value)
        self.assertEqual(github_util._handles, {
            ('username', 'http://some:283/random/url'): handle,
        })
        self.assertFalse(mock_getuser.called)
        self.assertFalse(mock_getpass.called)
        mock_Github.assert_called_once_with(
            'username', 'password', 'http://some:283/random/url')

    @mock.patch.dict(github_util._handles)
    @mock.patch('getpass.getuser', return_value='sysuser')
    @mock.patch('getpass.getpass', return_value='prompted')
    @mock.patch('github.Github')
    def test_user_pass_in_url(self, mock_Github, mock_getpass, mock_getuser):
        handle = github_util.get_handle(
            'username', 'password', 'http://user:pass@some:283/random//url/')

        self.assertEqual(handle, mock_Github.return_value)
        self.assertEqual(github_util._handles, {
            ('user', 'http://some:283/random/url'): handle,
        })
        self.assertFalse(mock_getuser.called)
        self.assertFalse(mock_getpass.called)
        mock_Github.assert_called_once_with(
            'user', 'pass', 'http://some:283/random/url')
