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

import pkg_resources


class AuditFailure(object):
    """
    Represent a single audit failure.  This contains the message, as
    well as individual parameters which may be useful in
    characterizing the failure.
    """

    def __init__(self, msg, **params):
        """
        Initialize an ``AuditFailure`` instance.

        :param msg: The message describing the failure.
        :param params: Remaining keyword arguments, which are treated
                       as substitutions for the message string.  These
                       will also be accessible as instance attributes.
        """

        # The audit name will be set by the audit_pr() method
        self.audit = None

        # Save the message and the parameters
        self._msg = msg
        self._params = params

        # Caches of the formatted strings...
        self._str_cache = None
        self._repr_cache = None

    def __str__(self):
        """
        Convert the ``AuditFailure`` instance to a string.

        :returns: The formatted message.
        """

        # Cache the formatted message
        if self._str_cache is None:
            self._str_cache = self._msg % self._params

        return self._str_cache

    def __repr__(self):
        """
        Retrieve a string representation of the ``AuditFailure`` instance.

        :returns: A string representation.
        """

        if self._repr_cache is None:
            # Format parameters
            params = ''
            if self._params:
                params = ' ' + ', '.join(
                    '%s=%r' % (k, v) for k, v in
                    sorted(self._params.items(), key=lambda x: x[0]))

            # Format the representation
            self._repr_cache = '<%s.%s object at %#x: "%s" (from %s)%s>' % (
                self.__class__.__module__, self.__class__.__name__, id(self),
                self._msg, self.audit or '?', params)

        return self._repr_cache

    def __getattr__(self, name):
        """
        Provide access to keyword parameters passed to the constructor as
        if they were instance attributes.

        :param name: The name of the parameter.

        :returns: The value of the parameter.
        """

        # Raise an AttributeError if it wasn't passed in
        if name not in self._params:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, name))

        return self._params[name]


class Auditor(object):
    """
    Represent a set of pull request audit checks.  This class is
    instantiated for each unique combination of audit checks; it may
    then be used to audit a given pull request.
    """

    # The namespace to look up audit callables in
    namespace = 'cognosco.audits'

    # A cache of instantiated auditors; the key is a frozenset of
    # audit callable names, with the special key None used for the
    # default set
    _auditors = {}

    # A cache of audit callables; the key is the audit callable name
    _cache = {}

    @classmethod
    def _get_audit(cls, name, ep=None):
        """
        Retrieve the named audit callable.

        :param name: The name of the audit callable.
        :param ep: Used by ``_get_all_audit()``; if the named audit
                   callable is not present in the cache, it will be
                   loaded from the specified endpoint.

        :returns: The audit callable.
        """

        # Is it cached?
        if name not in cls._cache:
            # If we were passed an endpoint, load it
            if ep:
                # Could raise exceptions; these are handled in
                # _get_all_audit()
                cls._cache[name] = ep.load()
            else:
                # Loop over all named endpoints
                for ep in pkg_resources.iter_entry_points(cls.namespace, name):
                    try:
                        cls._cache[name] = ep.load()
                    except (ImportError, AttributeError,
                            pkg_resources.UnknownExtra):
                        continue

                    break
                else:
                    # Couldn't find the endpoint
                    cls._cache[name] = None

        return cls._cache[name]

    @classmethod
    def _get_all_audit(cls):
        """
        Retrieve all named audit callables.

        :returns: A dictionary mapping audit callable names to the
                  callables.
        """

        # Loop over all named endpoints
        callables = {}
        for ep in pkg_resources.iter_entry_points(cls.namespace):
            # Skip ones we've already loaded
            if ep.name in callables:
                continue

            # OK, save the callable to the list
            try:
                callables[ep.name] = cls._get_audit(ep.name, ep)
            except (ImportError, AttributeError,
                    pkg_resources.UnknownExtra):
                continue

        # Return the audit callables
        return callables

    @classmethod
    def defaults(cls):
        """
        Retrieve a sorted list of all the audits configured by default.

        :returns: A sorted list of audits.
        """

        return sorted(cls._get_all_audit().keys())

    def __new__(cls, *audits):
        """
        Construct a new ``Auditor`` instance.

        :param audits: Positional parameters are interpreted as the
                       names of audits to execute.  If none are given,
                       all audits will be executed.

        :returns: The ``Auditor`` instance.
        """

        # Construct the auditors cache key
        if audits:
            key = frozenset(audits)
        else:
            key = None

        # Do we have an instance?
        if key not in cls._auditors:
            # No, we need to construct one; begin by getting the
            # audits
            if audits:
                audit_callables = {}
                for audit_name in audits:
                    # Convert the name to an audit callable
                    auditor = cls._get_audit(audit_name)
                    if auditor is None:
                        raise KeyError(audit_name)

                    audit_callables[audit_name] = auditor
            else:
                audit_callables = cls._get_all_audit()

            # Now construct the Auditor instance
            inst = super(Auditor, cls).__new__(cls)
            inst.audits = audit_callables

            # Cache the auditor
            cls._auditors[key] = inst

        return cls._auditors[key]

    def audit_pr(self, pr):
        """
        Audit a pull request to determine if any policy violations
        have occurred.

        :param pr: The ``github.PullRequest.PullRequest`` object
                   describing the pull request to be audited.

        :returns: A list of ``AuditFailure`` objects describing the
                  failures.  This list will be in no particular order.
        """

        # PRs that haven't merged can't have violated any policies
        if not pr.merged:
            return []

        # Perform the audit
        failures = []
        cache = {}
        for name, audit in self.audits.items():
            # Perform the check
            result = audit(pr, cache)

            # If it failed, set the audit name and save the failure
            if result:
                result.audit = name
                failures.append(result)

        return failures

    def audit_repo(self, repo, since=None, skip=None, all_checked=False):
        """
        Audit all merged pull requests on a repository to determine if any
        policy violations have occurred.

        :param repo: The ``github.Repository.Repository`` object
                     describing the repository to be audited.
        :param since: A ``datetime.datetime`` object indicating a
                      horizon date; only pull requests merged after
                      the horizon date will be reported.  Optional.
        :param skip: A ``set`` containing pull request numbers to
                     skip.  Optional.
        :param all_checked: If ``True``, all audited pull requests
                            will be included in the return value, even
                            if no policy violations have occurred on
                            them.  Defaults to ``False``.

        :returns: A list of tuples.  The first element of each tuple
                  is a ``github.PullRequest.PullRequest`` object
                  describing the pull request, and the second element
                  is a list of ``AuditFailure`` objects describing
                  failures.  If ``all_checked`` is ``True``, all pull
                  requests other than those excluded by ``since`` and
                  ``skip`` will be reported; otherwise, only those
                  which have no violations are reported.
        """

        # Normalize the skip
        if skip is None:
            skip = set()

        # A place to accumulate the results
        results = []

        # Walk through the pull requests
        for pr in repo.get_pulls('closed'):
            # Perform the pull request exclusion checks, taking
            # advantage of short-circuiting
            if (pr.number in skip or
                    not pr.merged or
                    (since is not None and pr.merged_at < since)):
                continue

            # Audit the pull request
            failures = self.audit_pr(pr)

            # Save the result if desired
            if all_checked or failures:
                results.append((pr, failures))

        return results


def self_merge(pr, cache):
    """
    Check if a pull request was self-merged.

    :param pr: The ``github.PullRequest.PullRequest`` object to audit.
    :param cache: A dictionary used for caching temporary values, so
                  that they may be reused by subsequent audit checks.

    :returns: If the check passes, returns ``None``; otherwise,
              returns an instance of ``AuditFailure``.
    """

    # Was the PR self-merged?
    if pr.user.login == pr.merged_by.login:
        return AuditFailure(
            'Pull request self-merged by %(merger)s at %(merged_at)s',
            merger=pr.merged_by.login,
            merged_at=pr.merged_at,
        )

    return None


def _get_pr_status(pr, cache):
    """
    Retrieves the ``github.CommitStatus.CommitStatus`` object that
    describes the status of the pull request.

    :param pr: The ``github.PullRequest.PullRequest`` object to audit.
    :param cache: A dictionary used for caching temporary values, so
                  that they may be reused by subsequent audit checks.

    :returns: The applicable ``github.CommitStatus.CommitStatus``
              object, or ``None`` if not available.
    """

    # Do we need to find the status?
    if 'status' not in cache:
        last_commit = list(pr.get_commits())[-1]
        statuses = list(last_commit.get_statuses())

        cache['status'] = statuses[0] if statuses else None

    return cache['status']


def merged_before_tests(pr, cache):
    """
    Check if the pull request was merged before tests finished
    running.  Note that this test cannot distinguish the case where
    tests were re-run after the pull request was merged.

    :param pr: The ``github.PullRequest.PullRequest`` object to audit.
    :param cache: A dictionary used for caching temporary values, so
                  that they may be reused by subsequent audit checks.

    :returns: If the check passes, returns ``None``; otherwise,
              returns an instance of ``AuditFailure``.
    """

    # Get the applicable status
    status = _get_pr_status(pr, cache)

    # If there was a status, check if it was merged before tests were
    # completed
    if status and pr.merged_at < status.created_at:
        return AuditFailure(
            'Pull request merged by %(merger)s at %(merged_at)s '
            'before tests completed at %(tested_at)s',
            merger=pr.merged_by.login,
            merged_at=pr.merged_at,
            tested_at=status.created_at,
        )

    return None


def tests_failed(pr, cache):
    """
    Check if the pull request was merged even though tests failed.
    Note that this test doesn't distinguish the case of the pull
    request being merged before tests finished.

    :param pr: The ``github.PullRequest.PullRequest`` object to audit.
    :param cache: A dictionary used for caching temporary values, so
                  that they may be reused by subsequent audit checks.

    :returns: If the check passes, returns ``None``; otherwise,
              returns an instance of ``AuditFailure``.
    """

    # Get the applicable status
    status = _get_pr_status(pr, cache)

    # If there was a status, check if the tests failed
    if status and status.state != 'success':
        return AuditFailure(
            'Pull request merged by %(merger)s at %(merged_at)s '
            'even though tests failed with final state %(state)s '
            'at %(tested_at)s',
            merger=pr.merged_by.login,
            merged_at=pr.merged_at,
            tested_at=status.created_at,
            state=status.state,
        )

    return None
