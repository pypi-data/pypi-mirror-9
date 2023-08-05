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

import collections
import os

import six
import yaml

from cognosco import audit
from cognosco import exc
from cognosco import github_util


class Repository(object):
    """
    Represents a Github repository.  This binds together the
    ``github.Repository.Repository`` object, which is the handle for
    the Github API representation; the desired
    ``cognosco.audit.Auditor`` instance, which describes which audits
    to make on the repository; and an optional set of pull requests to
    ignore for the purposes of at audit.  This class also provides a
    class method for importing ``Repository`` objects from one or more
    YAML files.
    """

    @classmethod
    def _load_yaml(cls, ctxt, path):
        """
        Load a set of ``Repository`` objects from a single YAML file.

        :param ctxt: An object containing defaults for the API
                     location, authentication credentials, and list of
                     audits to perform, obtainable with a ``get()``
                     method similar to that on ``dict``.  The object
                     must also have a ``warn()`` method, which will be
                     used to report warnings.
        :param path: The path to the YAML file to load.

        :returns: A dictionary mapping repository names to
                  ``Repository`` objects.
        """

        # Begin by loading the YAML file
        with open(path) as f:
            data = yaml.safe_load(f)

        # Validate the data format
        if isinstance(data, collections.Mapping):
            data = [data]
        elif (isinstance(data, six.string_types) or
              not isinstance(data, collections.Sequence)):
            raise TypeError('YAML file %s does not contain a list' % path)

        # Walk through the list of repositories
        repos = {}
        for idx, repo_data in enumerate(data):
            # Again, validate the data format
            if not isinstance(repo_data, collections.Mapping):
                raise TypeError(
                    'Repository at index %d in YAML file %s is not a dict' %
                    (idx, path))

            # Obtain the repository name
            try:
                name = repo_data['name']
            except KeyError:
                raise TypeError(
                    'Repository at index %d in YAML file %s is missing a '
                    'name' % (idx, path))

            # Get the github handle
            handle = github_util.get_handle(
                ctxt.get('username'), ctxt.get('password'),
                repo_data.get('api_url',
                              ctxt.get('url', 'https://api.github.com')))

            # Look up the repository
            try:
                repo = handle.get_repo(repo_data.get('full_name', name))
            except Exception as ex:
                # Log a warning
                ctxt.warn("Couldn't find repository %s (from %s): %s" %
                          (name, path, ex))

                # Need to go ahead and allocate a Repository, even if
                # we can't use it, so that we don't lose it when
                # overwriting the YAML files later
                repo = None

            # Now we need the Auditor
            audit_sources = [
                (path, repo_data.get('audits')),
                ('command line', ctxt.get('audits')),
                ('default', []),
            ]
            for src, audits in audit_sources:  # pragma: no branch
                if audits is None:
                    continue

                try:
                    auditor = audit.Auditor(*audits)
                except KeyError as ex:
                    # Log a warning
                    ctxt.warn("Couldn't load audit %s for repository %s "
                              "(from %s); using defaults" % (ex, name, src))
                else:
                    break

            # Construct the Repository
            repos[name] = cls(name, repo, auditor,
                              set(repo_data.get('skip', [])),
                              path, repo_data)

        return repos

    @classmethod
    def load_from(cls, ctxt, target):
        """
        Load a set of ``Repository`` objects from one or more YAML files.

        :param ctxt: An object containing defaults for the API
                     location, authentication credentials, and list of
                     audits to perform, obtainable with a ``get()``
                     method similar to that on ``dict``.  The object
                     must also have a ``warn()`` method, which will be
                     used to report warnings.
        :param target: The name of a YAML file, or the name of a
                       directory containing one or more files with a
                       ".yaml" extension.

        :returns: A list of ``Repository`` objects.
        """

        # If it's a single file, load it directly
        if os.path.isfile(target):
            return cls._load_yaml(ctxt, target).values()

        # A dictionary of repositories to return; the key is the
        # repository name
        repos = {}
        dups = {}

        # Walk the directory tree
        for dirpath, dirnames, filenames in os.walk(target):
            # Walk through each file in that directory
            for filename in filenames:
                # Skip any with the wrong extension
                root, ext = os.path.splitext(filename)
                if ext.lower() != '.yaml':
                    continue

                # Load the YAML file
                tmp_repos = cls._load_yaml(
                    ctxt, os.path.join(dirpath, filename))

                # Look for any duplicated repositories
                tmp_dups = set(repos.keys()) & set(tmp_repos.keys())
                for dup in tmp_dups:
                    dups.setdefault(dup, [repos[dup]])
                    dups[dup].append(tmp_repos.pop(dup))

                # Save the newly loaded repositories
                repos.update(tmp_repos)

        # If there were any duplications, report them
        if dups:
            raise exc.DuplicateRepositoryException(
                'Duplicate repositories defined in %s' % (target,),
                dups=dups)

        return repos.values()

    @classmethod
    def save(cls, repos):
        """
        Given a list of ``Repository`` objects, re-writes the YAML files
        from which those objects were loaded.  This is used to update
        the set of pull request numbers to skip on the next run.

        :param repos: A list of ``Repository`` objects.
        """

        # Need to map the repositories back to their YAML files
        files = {}
        for repo in repos:
            # Skip repositories that came from the command line
            if not repo.path:
                continue

            # Save the repository to the list of repositories for that
            # YAML file
            files.setdefault(repo.path, [])
            files[repo.path].append(repo)

        # Now walk through each file...
        for path, repo_list in files.items():
            # Build the raw data for the file to contain
            data = [repo.raw for repo in
                    sorted(repo_list, key=lambda x: x.name)]

            # Save that data
            with open(path, 'w') as f:
                yaml.safe_dump(data, f)

    def __init__(self, name, repo, auditor, skip=None, path=None, raw=None):
        """
        Initialize a ``Repository`` object.

        :param name: The repository name.
        :param repo: A ``github.Repository.Repository`` object
                     describing the repository.
        :param auditor: A ``cognosco.audit.Auditor`` object describing
                        the audit checks to perform on the repository.
        :param skip: A set of pull request numbers to ignore during
                     audits.  Optional.
        :param path: A path to a YAML file containing data about the
                     repository.  Optional.
        :param raw: The raw data describing the repository, as loaded
                    from the YAML file.  Optional.
        """

        # Save the repository information
        self.name = name
        self.repo = repo
        self.auditor = auditor
        self.skip = skip or set()
        self.path = path

        # Synthesize raw data if possible
        if raw is not None:
            self._raw = raw
        elif repo:
            self._raw = {'name': self.repo.full_name}
        else:
            self._raw = {}

    def audit(self, since=None, update_skip=True, all_checked=False):
        """
        Audit all merged pull requests on the repository to determine if
        any policy violations have occurred.

        :param since: A ``datetime.datetime`` object indicating a
                      horizon date; only pull requests merged after
                      the horizon date will be reported.  Optional.
        :param update_skip: Controls whether the set of handled pull
                            requests will be updated.  Defaults to
                            ``True``.
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
                  the skip list will be reported; otherwise, only
                  those which have no violations are reported.
        """

        # If there's no repository, return no failures
        if not self.repo:
            return []

        # First step is to run the audit
        failures = self.auditor.audit_repo(
            self.repo, since, self.skip, update_skip or all_checked)

        # Update the skips if we were asked to
        if update_skip:
            self.skip |= set(f[0].number for f in failures)

        # Return the list of failures
        if not all_checked and update_skip:
            # Need to filter out the non-failures
            return [f for f in failures if f[1]]
        return failures

    @property
    def raw(self):
        """
        Return the updated raw data for the repository.  This will include
        the updated list of skipped pull requests.
        """

        # Update the skip set in the raw data
        self._raw['skip'] = sorted(self.skip)

        return self._raw
