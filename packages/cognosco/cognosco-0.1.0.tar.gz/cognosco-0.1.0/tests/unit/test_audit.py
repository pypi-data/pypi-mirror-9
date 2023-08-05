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
import unittest

import mock
import pkg_resources

from cognosco import audit


class AuditFailureTest(unittest.TestCase):
    def test_init_base(self):
        af = audit.AuditFailure('a message')

        self.assertEqual(af.audit, None)
        self.assertEqual(af._msg, 'a message')
        self.assertEqual(af._params, {})
        self.assertEqual(af._str_cache, None)
        self.assertEqual(af._repr_cache, None)

    def test_init_params(self):
        af = audit.AuditFailure('a message', a=1, b=2, c=3)

        self.assertEqual(af.audit, None)
        self.assertEqual(af._msg, 'a message')
        self.assertEqual(af._params, {'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(af._str_cache, None)
        self.assertEqual(af._repr_cache, None)

    def test_str_cached(self):
        af = audit.AuditFailure('this is %(a)s test', a='the')
        af._str_cache = 'cached'

        self.assertEqual(str(af), 'cached')
        self.assertEqual(af._str_cache, 'cached')

    def test_str_uncached(self):
        af = audit.AuditFailure('this is %(a)s test', a='the')

        self.assertEqual(str(af), 'this is the test')
        self.assertEqual(af._str_cache, 'this is the test')

    def test_repr_cached(self):
        af = audit.AuditFailure('this is %(a)s test', a='the')
        af.audit = 'auditor'
        af._repr_cache = 'cached'

        self.assertEqual(repr(af), 'cached')
        self.assertEqual(af._repr_cache, 'cached')

    def test_repr_uncached_params(self):
        af = audit.AuditFailure('this is %(a)s test', a='the', b='whatever')
        af.audit = 'auditor'
        expected = ('<cognosco.audit.AuditFailure object at %#x: '
                    '"this is %%(a)s test" (from auditor) '
                    "a='the', b='whatever'>" % id(af))

        self.assertEqual(repr(af), expected)
        self.assertEqual(af._repr_cache, expected)

    def test_repr_uncached_noparams(self):
        af = audit.AuditFailure('this is a test')
        af.audit = 'auditor'
        expected = ('<cognosco.audit.AuditFailure object at %#x: '
                    '"this is a test" (from auditor)>' % id(af))

        self.assertEqual(repr(af), expected)
        self.assertEqual(af._repr_cache, expected)

    def test_getattr_missing_param(self):
        af = audit.AuditFailure('this is a test')

        self.assertRaises(AttributeError, lambda: af.a)

    def test_getattr_with_param(self):
        af = audit.AuditFailure('this is %(a)s test', a='the')

        self.assertEqual(af.a, 'the')


class AuditorTest(unittest.TestCase):
    @mock.patch.dict(audit.Auditor._cache, clear=True, name='result')
    @mock.patch.object(pkg_resources, 'iter_entry_points', return_value=[])
    def test_get_audit_cached(self, mock_iter_entry_points):
        result = audit.Auditor._get_audit('name')

        self.assertEqual(result, 'result')
        self.assertEqual(audit.Auditor._cache, {'name': 'result'})
        self.assertFalse(mock_iter_entry_points.called)

    @mock.patch.dict(audit.Auditor._cache, clear=True)
    @mock.patch.object(pkg_resources, 'iter_entry_points', return_value=[])
    def test_get_audit_from_ep(self, mock_iter_entry_points):
        ep = mock.Mock(**{'load.return_value': 'result'})

        result = audit.Auditor._get_audit('name', ep)

        self.assertEqual(result, 'result')
        self.assertEqual(audit.Auditor._cache, {'name': 'result'})
        ep.load.assert_called_once_with()
        self.assertFalse(mock_iter_entry_points.called)

    @mock.patch.dict(audit.Auditor._cache, clear=True)
    @mock.patch.object(pkg_resources, 'iter_entry_points', return_value=[])
    def test_get_audit_none(self, mock_iter_entry_points):
        result = audit.Auditor._get_audit('name')

        self.assertEqual(result, None)
        self.assertEqual(audit.Auditor._cache, {'name': None})
        mock_iter_entry_points.assert_called_once_with(
            'cognosco.audits', 'name')

    @mock.patch.dict(audit.Auditor._cache, clear=True)
    @mock.patch.object(pkg_resources, 'iter_entry_points', return_value=[
        mock.Mock(**{'load.side_effect': ImportError()}),
        mock.Mock(**{'load.side_effect': AttributeError()}),
        mock.Mock(**{'load.side_effect': pkg_resources.UnknownExtra()}),
        mock.Mock(**{'load.return_value': 'result'}),
        mock.Mock(**{'load.return_value': 'not here'}),
    ])
    def test_get_audit_entrypoints(self, mock_iter_entry_points):
        result = audit.Auditor._get_audit('name')

        self.assertEqual(result, 'result')
        self.assertEqual(audit.Auditor._cache, {'name': 'result'})
        mock_iter_entry_points.assert_called_once_with(
            'cognosco.audits', 'name')
        for ep in mock_iter_entry_points.return_value[:-1]:
            ep.load.assert_called_once_with()
        self.assertFalse(mock_iter_entry_points.return_value[-1].load.called)

    @mock.patch.object(pkg_resources, 'iter_entry_points', return_value=[])
    @mock.patch.object(audit.Auditor, '_get_audit')
    def test_get_all_audit_empty(self, mock_get_audit, mock_iter_entry_points):
        result = audit.Auditor._get_all_audit()

        self.assertEqual(result, {})
        mock_iter_entry_points.assert_called_once_with('cognosco.audits')
        self.assertFalse(mock_get_audit.called)

    @mock.patch.object(pkg_resources, 'iter_entry_points', return_value=[
        mock.Mock(e_name='ep1', result='ep1'),
        mock.Mock(e_name='ep1', result='bad_ep1'),
        mock.Mock(e_name='ep2', result=ImportError()),
        mock.Mock(e_name='ep2', result=AttributeError()),
        mock.Mock(e_name='ep2', result=pkg_resources.UnknownExtra()),
        mock.Mock(e_name='ep2', result='ep2'),
    ])
    @mock.patch.object(audit.Auditor, '_get_audit')
    def test_get_all_audit_eps(self, mock_get_audit, mock_iter_entry_points):
        def fake_get_audit(name, ep):
            if isinstance(ep.result, Exception):
                raise ep.result
            return ep.result
        mock_get_audit.side_effect = fake_get_audit
        for ep in mock_iter_entry_points.return_value:
            ep.name = ep.e_name

        result = audit.Auditor._get_all_audit()

        self.assertEqual(result, {'ep1': 'ep1', 'ep2': 'ep2'})
        mock_iter_entry_points.assert_called_once_with('cognosco.audits')
        mock_get_audit.assert_has_calls([
            mock.call('ep1', mock_iter_entry_points.return_value[0]),
            mock.call('ep2', mock_iter_entry_points.return_value[2]),
            mock.call('ep2', mock_iter_entry_points.return_value[3]),
            mock.call('ep2', mock_iter_entry_points.return_value[4]),
            mock.call('ep2', mock_iter_entry_points.return_value[5]),
        ])
        self.assertEqual(mock_get_audit.call_count, 5)

    @mock.patch.object(audit.Auditor, '_get_all_audit',
                       return_value={'ep1': 1, 'ep2': 2})
    def test_defaults(self, mock_get_all_audit):
        result = audit.Auditor.defaults()

        self.assertEqual(result, ['ep1', 'ep2'])

    @mock.patch.dict(audit.Auditor._auditors, {None: 'cached'})
    @mock.patch.object(audit.Auditor, '_get_audit',
                       side_effect=lambda x: 'ep.%s' % x)
    @mock.patch.object(audit.Auditor, '_get_all_audit',
                       return_value={'ep1': 1, 'ep2': 2})
    def test_new_cached_no_audit(self, mock_get_all_audit, mock_get_audit):
        result = audit.Auditor()

        self.assertEqual(result, 'cached')
        self.assertEqual(audit.Auditor._auditors, {None: 'cached'})
        self.assertFalse(mock_get_audit.called)
        self.assertFalse(mock_get_all_audit.called)

    @mock.patch.dict(audit.Auditor._auditors,
                     {frozenset(['a1', 'a2']): 'cached'})
    @mock.patch.object(audit.Auditor, '_get_audit',
                       side_effect=lambda x: 'ep.%s' % x)
    @mock.patch.object(audit.Auditor, '_get_all_audit',
                       return_value={'ep1': 1, 'ep2': 2})
    def test_new_cached_with_audit(self, mock_get_all_audit, mock_get_audit):
        result = audit.Auditor('a1', 'a2')

        self.assertEqual(result, 'cached')
        self.assertEqual(audit.Auditor._auditors,
                         {frozenset(['a1', 'a2']): 'cached'})
        self.assertFalse(mock_get_audit.called)
        self.assertFalse(mock_get_all_audit.called)

    @mock.patch.dict(audit.Auditor._auditors)
    @mock.patch.object(audit.Auditor, '_get_audit',
                       side_effect=lambda x: 'ep.%s' % x)
    @mock.patch.object(audit.Auditor, '_get_all_audit',
                       return_value={'ep1': 1, 'ep2': 2})
    def test_new_uncached_no_audit(self, mock_get_all_audit, mock_get_audit):
        result = audit.Auditor()

        self.assertTrue(isinstance(result, audit.Auditor))
        self.assertEqual(result.audits, {'ep1': 1, 'ep2': 2})
        self.assertEqual(audit.Auditor._auditors, {None: result})
        self.assertFalse(mock_get_audit.called)
        mock_get_all_audit.assert_called_once_with()

    @mock.patch.dict(audit.Auditor._auditors)
    @mock.patch.object(audit.Auditor, '_get_audit',
                       side_effect=lambda x: 'ep.%s' % x)
    @mock.patch.object(audit.Auditor, '_get_all_audit',
                       return_value={'ep1': 1, 'ep2': 2})
    def test_new_uncached_with_audit(self, mock_get_all_audit, mock_get_audit):
        result = audit.Auditor('a1', 'a2')

        self.assertTrue(isinstance(result, audit.Auditor))
        self.assertEqual(result.audits, {'a1': 'ep.a1', 'a2': 'ep.a2'})
        self.assertEqual(audit.Auditor._auditors,
                         {frozenset(['a1', 'a2']): result})
        mock_get_audit.assert_has_calls([
            mock.call('a1'),
            mock.call('a2'),
        ], any_order=True)
        self.assertEqual(mock_get_audit.call_count, 2)
        self.assertFalse(mock_get_all_audit.called)

    @mock.patch.dict(audit.Auditor._auditors)
    @mock.patch.object(audit.Auditor, '_get_audit', return_value=None)
    @mock.patch.object(audit.Auditor, '_get_all_audit',
                       return_value={'ep1': 1, 'ep2': 2})
    def test_new_uncached_missing_audit(self, mock_get_all_audit,
                                        mock_get_audit):
        self.assertRaises(KeyError, audit.Auditor, 'a1')
        self.assertEqual(audit.Auditor._auditors, {})
        mock_get_audit.assert_called_once_with('a1')
        self.assertFalse(mock_get_all_audit.called)

    def make_auditor(self, audits):
        inst = super(audit.Auditor, audit.Auditor).__new__(audit.Auditor)
        inst.audits = audits

        return inst

    def test_audit_pr_merged(self):
        pr = mock.Mock(merged=False)
        audits = {
            'a1': mock.Mock(return_value=mock.Mock()),
            'a2': mock.Mock(return_value=mock.Mock()),
        }
        auditor = self.make_auditor(audits)

        result = auditor.audit_pr(pr)

        self.assertEqual(result, [])
        for audit in audits.values():
            self.assertFalse(audit.called)

    def test_audit_pr_passed(self):
        pr = mock.Mock(merged=True)
        audits = {
            'a1': mock.Mock(return_value=None),
            'a2': mock.Mock(return_value=None),
        }
        auditor = self.make_auditor(audits)

        result = auditor.audit_pr(pr)

        self.assertEqual(result, [])
        for audit in audits.values():
            audit.assert_called_once_with(pr, {})

    def test_audit_pr_failure(self):
        failures = {
            'f1': mock.Mock(),
            'f2': mock.Mock(),
        }

        def a1_side_effect(pr, cache):
            cache['side_effect'] = 'cached'
            return None

        def a2_side_effect(pr, cache):
            self.assertEqual(cache['side_effect'], 'cached')
            return failures['f1']

        pr = mock.Mock(merged=True)
        audits = {
            'a1': mock.Mock(side_effect=a1_side_effect),
            'a2': mock.Mock(side_effect=a2_side_effect),
            'a3': mock.Mock(return_value=failures['f2']),
            'a4': mock.Mock(return_value=None),
        }
        auditor = self.make_auditor(mock.Mock(**{
            'items.return_value': [(k, v) for k, v in
                                   sorted(audits.items(), key=lambda x: x[0])],
        }))

        result = auditor.audit_pr(pr)

        self.assertEqual(result, [v for k, v in sorted(failures.items(),
                                                       key=lambda x: x[0])])
        for audit in audits.values():
            audit.assert_called_once_with(pr, {'side_effect': 'cached'})

    @mock.patch.object(audit.Auditor, 'audit_pr',
                       side_effect=lambda x: x.failures)
    def test_audit_repo_base(self, mock_audit_pr):
        prs = [
            mock.Mock(
                number=1,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
                failures=['f1', 'f2'],
            ),
            mock.Mock(
                number=2,
                merged=False,
                merged_at=None,
                failures=[],
            ),
            mock.Mock(
                number=3,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
                failures=[],
            ),
            mock.Mock(
                number=4,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 2),
                failures=['f3', 'f4'],
            ),
        ]
        repo = mock.Mock(**{'get_pulls.return_value': prs})
        auditor = self.make_auditor({})

        result = auditor.audit_repo(repo)

        self.assertEqual(result, [
            (prs[0], ['f1', 'f2']),
            (prs[3], ['f3', 'f4']),
        ])
        mock_audit_pr.assert_has_calls([
            mock.call(prs[0]),
            mock.call(prs[2]),
            mock.call(prs[3]),
        ])
        self.assertEqual(mock_audit_pr.call_count, 3)

    @mock.patch.object(audit.Auditor, 'audit_pr',
                       side_effect=lambda x: x.failures)
    def test_audit_repo_base_all(self, mock_audit_pr):
        prs = [
            mock.Mock(
                number=1,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
                failures=['f1', 'f2'],
            ),
            mock.Mock(
                number=2,
                merged=False,
                merged_at=None,
                failures=[],
            ),
            mock.Mock(
                number=3,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
                failures=[],
            ),
            mock.Mock(
                number=4,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 2),
                failures=['f3', 'f4'],
            ),
        ]
        repo = mock.Mock(**{'get_pulls.return_value': prs})
        auditor = self.make_auditor({})

        result = auditor.audit_repo(repo, all_checked=True)

        self.assertEqual(result, [
            (prs[0], ['f1', 'f2']),
            (prs[2], []),
            (prs[3], ['f3', 'f4']),
        ])
        mock_audit_pr.assert_has_calls([
            mock.call(prs[0]),
            mock.call(prs[2]),
            mock.call(prs[3]),
        ])
        self.assertEqual(mock_audit_pr.call_count, 3)

    @mock.patch.object(audit.Auditor, 'audit_pr',
                       side_effect=lambda x: x.failures)
    def test_audit_repo_skip(self, mock_audit_pr):
        prs = [
            mock.Mock(
                number=1,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
                failures=['f1', 'f2'],
            ),
            mock.Mock(
                number=2,
                merged=False,
                merged_at=None,
                failures=[],
            ),
            mock.Mock(
                number=3,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
                failures=[],
            ),
            mock.Mock(
                number=4,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 2),
                failures=['f3', 'f4'],
            ),
        ]
        repo = mock.Mock(**{'get_pulls.return_value': prs})
        auditor = self.make_auditor({})

        result = auditor.audit_repo(repo, skip=set([1, 3]))

        self.assertEqual(result, [
            (prs[3], ['f3', 'f4']),
        ])
        mock_audit_pr.assert_has_calls([
            mock.call(prs[3]),
        ])
        self.assertEqual(mock_audit_pr.call_count, 1)

    @mock.patch.object(audit.Auditor, 'audit_pr',
                       side_effect=lambda x: x.failures)
    def test_audit_repo_skip_all(self, mock_audit_pr):
        prs = [
            mock.Mock(
                number=1,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
                failures=['f1', 'f2'],
            ),
            mock.Mock(
                number=2,
                merged=False,
                merged_at=None,
                failures=[],
            ),
            mock.Mock(
                number=3,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
                failures=[],
            ),
            mock.Mock(
                number=4,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 2),
                failures=['f3', 'f4'],
            ),
        ]
        repo = mock.Mock(**{'get_pulls.return_value': prs})
        auditor = self.make_auditor({})

        result = auditor.audit_repo(repo, skip=set([1, 2]), all_checked=True)

        self.assertEqual(result, [
            (prs[2], []),
            (prs[3], ['f3', 'f4']),
        ])
        mock_audit_pr.assert_has_calls([
            mock.call(prs[2]),
            mock.call(prs[3]),
        ])
        self.assertEqual(mock_audit_pr.call_count, 2)

    @mock.patch.object(audit.Auditor, 'audit_pr',
                       side_effect=lambda x: x.failures)
    def test_audit_repo_since(self, mock_audit_pr):
        since = datetime.datetime(2014, 1, 1, 0, 0, 1)
        prs = [
            mock.Mock(
                number=1,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
                failures=['f1', 'f2'],
            ),
            mock.Mock(
                number=2,
                merged=False,
                merged_at=None,
                failures=[],
            ),
            mock.Mock(
                number=3,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
                failures=[],
            ),
            mock.Mock(
                number=4,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 2),
                failures=['f3', 'f4'],
            ),
        ]
        repo = mock.Mock(**{'get_pulls.return_value': prs})
        auditor = self.make_auditor({})

        result = auditor.audit_repo(repo, since=since)

        self.assertEqual(result, [
            (prs[3], ['f3', 'f4']),
        ])
        mock_audit_pr.assert_has_calls([
            mock.call(prs[2]),
            mock.call(prs[3]),
        ])
        self.assertEqual(mock_audit_pr.call_count, 2)

    @mock.patch.object(audit.Auditor, 'audit_pr',
                       side_effect=lambda x: x.failures)
    def test_audit_repo_since_all(self, mock_audit_pr):
        since = datetime.datetime(2014, 1, 1, 0, 0, 1)
        prs = [
            mock.Mock(
                number=1,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
                failures=['f1', 'f2'],
            ),
            mock.Mock(
                number=2,
                merged=False,
                merged_at=None,
                failures=[],
            ),
            mock.Mock(
                number=3,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
                failures=[],
            ),
            mock.Mock(
                number=4,
                merged=True,
                merged_at=datetime.datetime(2014, 1, 1, 0, 0, 2),
                failures=['f3', 'f4'],
            ),
        ]
        repo = mock.Mock(**{'get_pulls.return_value': prs})
        auditor = self.make_auditor({})

        result = auditor.audit_repo(repo, since=since, all_checked=True)

        self.assertEqual(result, [
            (prs[2], []),
            (prs[3], ['f3', 'f4']),
        ])
        mock_audit_pr.assert_has_calls([
            mock.call(prs[2]),
            mock.call(prs[3]),
        ])
        self.assertEqual(mock_audit_pr.call_count, 2)


class SelfMergeTest(unittest.TestCase):
    @mock.patch.object(audit, 'AuditFailure')
    def test_pass(self, mock_AuditFailure):
        pr = mock.Mock(**{
            'user.login': 'one',
            'merged_by.login': 'two',
            'merged_at': 'merged_at',
        })
        cache = {}

        result = audit.self_merge(pr, cache)

        self.assertEqual(result, None)
        self.assertEqual(cache, {})
        self.assertFalse(mock_AuditFailure.called)

    @mock.patch.object(audit, 'AuditFailure')
    def test_fail(self, mock_AuditFailure):
        pr = mock.Mock(**{
            'user.login': 'one',
            'merged_by.login': 'one',
            'merged_at': 'merged_at',
        })
        cache = {}

        result = audit.self_merge(pr, cache)

        self.assertEqual(result, mock_AuditFailure.return_value)
        self.assertEqual(cache, {})
        mock_AuditFailure.assert_called_once_with(
            mock.ANY, merger='one', merged_at='merged_at')


class GetPrStatusTest(unittest.TestCase):
    def test_cached(self):
        pr = mock.Mock(**{
            'get_commits.return_value': [
                'commit1',
                'commit2',
                mock.Mock(**{
                    'get_statuses.return_value': ['status1', 'status2'],
                }),
            ],
        })
        cache = {'status': 'cached'}

        result = audit._get_pr_status(pr, cache)

        self.assertEqual(result, 'cached')
        self.assertEqual(cache, {'status': 'cached'})

    def test_uncached(self):
        pr = mock.Mock(**{
            'get_commits.return_value': [
                'commit1',
                'commit2',
                mock.Mock(**{
                    'get_statuses.return_value': ['status1', 'status2'],
                }),
            ],
        })
        cache = {}

        result = audit._get_pr_status(pr, cache)

        self.assertEqual(result, 'status1')
        self.assertEqual(cache, {'status': 'status1'})

    def test_uncached_no_status(self):
        pr = mock.Mock(**{
            'get_commits.return_value': [
                'commit1',
                'commit2',
                mock.Mock(**{
                    'get_statuses.return_value': [],
                }),
            ],
        })
        cache = {}

        result = audit._get_pr_status(pr, cache)

        self.assertEqual(result, None)
        self.assertEqual(cache, {'status': None})


class MergedBeforeTestsTest(unittest.TestCase):
    @mock.patch.object(audit, '_get_pr_status', return_value=mock.Mock(
        created_at=datetime.datetime(2014, 1, 1, 0, 0, 1)))
    @mock.patch.object(audit, 'AuditFailure')
    def test_pass(self, mock_AuditFailure, mock_get_pr_status):
        pr = mock.Mock(**{
            'merged_at': datetime.datetime(2014, 1, 1, 0, 0, 2),
            'merged_by.login': 'merger',
        })
        cache = {}

        result = audit.merged_before_tests(pr, cache)

        self.assertEqual(result, None)
        self.assertEqual(cache, {})
        mock_get_pr_status.assert_called_once_with(pr, cache)
        self.assertFalse(mock_AuditFailure.called)

    @mock.patch.object(audit, '_get_pr_status', return_value=None)
    @mock.patch.object(audit, 'AuditFailure')
    def test_no_status(self, mock_AuditFailure, mock_get_pr_status):
        pr = mock.Mock(**{
            'merged_at': datetime.datetime(2014, 1, 1, 0, 0, 2),
            'merged_by.login': 'merger',
        })
        cache = {}

        result = audit.merged_before_tests(pr, cache)

        self.assertEqual(result, None)
        self.assertEqual(cache, {})
        mock_get_pr_status.assert_called_once_with(pr, cache)
        self.assertFalse(mock_AuditFailure.called)

    @mock.patch.object(audit, '_get_pr_status', return_value=mock.Mock(
        created_at=datetime.datetime(2014, 1, 1, 0, 0, 1)))
    @mock.patch.object(audit, 'AuditFailure')
    def test_fail(self, mock_AuditFailure, mock_get_pr_status):
        pr = mock.Mock(**{
            'merged_at': datetime.datetime(2014, 1, 1, 0, 0, 0),
            'merged_by.login': 'merger',
        })
        cache = {}

        result = audit.merged_before_tests(pr, cache)

        self.assertEqual(result, mock_AuditFailure.return_value)
        self.assertEqual(cache, {})
        mock_get_pr_status.assert_called_once_with(pr, cache)
        mock_AuditFailure.assert_called_once_with(
            mock.ANY, merger='merger',
            merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
            tested_at=datetime.datetime(2014, 1, 1, 0, 0, 1))


class TestsFailedTest(unittest.TestCase):
    @mock.patch.object(audit, '_get_pr_status', return_value=mock.Mock(
        created_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
        state='success'))
    @mock.patch.object(audit, 'AuditFailure')
    def test_pass(self, mock_AuditFailure, mock_get_pr_status):
        pr = mock.Mock(**{
            'merged_at': datetime.datetime(2014, 1, 1, 0, 0, 2),
            'merged_by.login': 'merger',
        })
        cache = {}

        result = audit.tests_failed(pr, cache)

        self.assertEqual(result, None)
        self.assertEqual(cache, {})
        mock_get_pr_status.assert_called_once_with(pr, cache)
        self.assertFalse(mock_AuditFailure.called)

    @mock.patch.object(audit, '_get_pr_status', return_value=None)
    @mock.patch.object(audit, 'AuditFailure')
    def test_no_status(self, mock_AuditFailure, mock_get_pr_status):
        pr = mock.Mock(**{
            'merged_at': datetime.datetime(2014, 1, 1, 0, 0, 2),
            'merged_by.login': 'merger',
        })
        cache = {}

        result = audit.tests_failed(pr, cache)

        self.assertEqual(result, None)
        self.assertEqual(cache, {})
        mock_get_pr_status.assert_called_once_with(pr, cache)
        self.assertFalse(mock_AuditFailure.called)

    @mock.patch.object(audit, '_get_pr_status', return_value=mock.Mock(
        created_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
        state='error'))
    @mock.patch.object(audit, 'AuditFailure')
    def test_fail(self, mock_AuditFailure, mock_get_pr_status):
        pr = mock.Mock(**{
            'merged_at': datetime.datetime(2014, 1, 1, 0, 0, 0),
            'merged_by.login': 'merger',
        })
        cache = {}

        result = audit.tests_failed(pr, cache)

        self.assertEqual(result, mock_AuditFailure.return_value)
        self.assertEqual(cache, {})
        mock_get_pr_status.assert_called_once_with(pr, cache)
        mock_AuditFailure.assert_called_once_with(
            mock.ANY, merger='merger',
            merged_at=datetime.datetime(2014, 1, 1, 0, 0, 0),
            tested_at=datetime.datetime(2014, 1, 1, 0, 0, 1),
            state='error')
