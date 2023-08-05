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

from __future__ import print_function

import argparse
import datetime
import getpass
import io
import sys
import textwrap

import cli_tools
import github
import six
import timestring

from cognosco import audit
from cognosco import exc
from cognosco import github_util
from cognosco import repository


class Context(object):
    """
    A class to contain defaults for API location and authentication
    credentials.  The class also provides a ``warn()`` method to emit
    warnings to standard error.
    """

    def __init__(self, args):
        """
        Initialize a ``Context`` object.

        :param args: The ``argparse.Namespace`` object containing the
                     results of command line argument processing.
        """

        # Save the argument data
        self.username = args.username
        self.password = args.password
        self.url = args.github_url
        self.audits = args.audits

    def get(self, name, default=None):
        """
        Get the value of a configured attribute.  If the value is not
        available (e.g., set to ``None``), a default value will be
        returned.

        :param name: The name of the desired attribute.
        :param default: The default value to return.  Defaults to
                        ``None``.

        :returns: The value of the configured attribute, or the value
                  of ``default`` if the attribute was not set or was
                  empty.
        """

        # Use getattr() for the attributes we know
        if name in ('username', 'password', 'url', 'audits'):
            return getattr(self, name) or default

        return default

    def warn(self, msg):
        """
        Emit a warning message.

        :param msg: The message to emit.
        """

        print("WARNING: %s" % msg, file=sys.stderr)


td_zero = datetime.timedelta(0)


def format_age(now, time, fmt):
    """
    Format an age safely.  If the age is less than 0, an empty string
    will be returned.

    :param now: The current time, as a ``datetime.datetime`` object.
    :param time: The time to be converted into an age, as a
                 ``datetime.datetime`` object.
    :param fmt: A format string designating how the age should be
                formatted.  A "%s" will be replaced with the age.

    :returns: The age, formatted as a string.
    """

    # Compute the age
    age = now - time

    # If it's less than zero, it has no age, so return an empty string
    if age <= td_zero:
        return ''

    # Format and return the age
    return fmt % age


def _make_repos(ctxt, name, get_repos):
    """
    A helper to construct ``cognosco.repository.Repository`` objects.

    :param ctxt: An object containing defaults for the API location,
                 authentication credentials, and list of audits to
                 perform, obtainable with a ``get()`` method similar
                 to that on ``dict``.  The object must also have a
                 ``warn()`` method, which will be used to report
                 warnings.
    :param name: The name of the resource to look up.
    :param get_repos: A callable that, given a ``github.Github``
                      handle and a name, returns an iterable of
                      ``github.Repository.Repository`` objects.

    :returns: A list of ``cognosco.repository.Repository`` objects.
    """

    # First, obtain the appropriate Github handle
    gh = github_util.get_handle(
        ctxt.get('username'), ctxt.get('password'), ctxt.get('url'))

    # Next, select the appropriate auditor
    audit_sources = [
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
            ctxt.warn("Couldn't load audit %s for repository source %s "
                      "(from %s); using defaults" % (ex, name, src))
        else:
            break

    # Now we need to construct the Repository objects
    return [repository.Repository(repo.full_name, repo, auditor)
            for repo in get_repos(gh, name)]


# This maps the target name used in an argument declaration to the
# routine used to find the open pull requests for that target
targets = {
    'repo': lambda ctxt, name: _make_repos(
        ctxt, name, lambda gh, name: [gh.get_repo(name)]),
    'org': lambda ctxt, name: _make_repos(
        ctxt, name, lambda gh, name: gh.get_organization(name).get_repos()),
    'user': lambda ctxt, name: _make_repos(
        ctxt, name, lambda gh, name: gh.get_user(name).get_repos()),
    'config': repository.Repository.load_from,
}


class RepoAction(argparse.Action):
    """
    An ``argparse.Action`` subclass used for command line arguments
    that are used in indicating which repositories to audit.
    """

    def __init__(self, option_strings, dest, **kwargs):
        """
        Initialize a ``RepoAction`` object.

        :param option_strings: A list of option strings.
        :param dest: The target attribute to store the option values
                     in.
        :param target: The target the option specifies.  Must be one
                       of the keys from the ``targets`` dictionary.
                       Defaults to "repo" if not provided.
        """

        # Need the target information
        target = kwargs.pop('target', 'repo')

        # Initialize the Action
        super(RepoAction, self).__init__(option_strings, dest, **kwargs)

        # Save the target information
        self.target = target

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Called when encountering an argument bound to the ``RepoAction``
        object.

        :param parser: An ``argparse.ArgumentParser`` object.
        :param namespace: The ``argparse.Namespace`` into which to
                          store argument values.
        :param values: The values that were passed for the argument.
        :param option_string: The string used to invoke the option.
        """

        # Append the appropriate value to the namespace
        items = getattr(namespace, self.dest, [])
        items.append((self.target, values))
        setattr(namespace, self.dest, items)


class TimeAction(argparse.Action):
    """
    An ``argparse.Action`` subclass used for interpreting the command
    line option(s) which need to parse a time.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Called when encountering an argument bound to the ``TimeAction``
        object.

        :param parser: An ``argparse.ArgumentParser`` object.
        :param namespace: The ``argparse.Namespace`` into which to
                          store argument values.
        :param values: The values that were passed for the argument.
        :param option_string: The string used to invoke the option.
        """

        # Parse the time into a datetime and save it
        setattr(namespace, self.dest, timestring.Date(values).date)


@cli_tools.argument_group(
    'auth',
    title='Authentication-related Options',
    description='Options used to authenticate to Github.',
)
@cli_tools.argument(
    '--username', '-u',
    help=('Username for accessing the Github API.  Defaults to "%s"' %
          getpass.getuser()),
    group='auth',
)
@cli_tools.argument(
    '--password', '-p',
    help='Password or personal access token for accessing the Github API.  '
    'If not provided, it will be prompted for.',
    group='auth',
)
@cli_tools.argument(
    '--github-url', '-g',
    default='https://api.github.com',
    help='API URL for accessing the Github API.  Defaults to "%(default)s".',
    group='auth',
)
@cli_tools.argument_group(
    'repo',
    title='Repositories to Audit',
    description='Options used to identify specific repositories to generate '
    'audit reports on.  These options may be used multiple times.',
)
@cli_tools.argument(
    '--config', '-c',
    dest='repos',
    action=RepoAction,
    default=[],
    help='Identify a single configuration file or a directory of '
    'configuration files describing one or more repositories to audit.  If '
    'a directory is specified, all files with a ".yaml" extension will be '
    'read.',
    group='repo',
    target='config',
)
@cli_tools.argument(
    '--repo', '-r',
    dest='repos',
    action=RepoAction,
    default=[],
    help='Identify a specific repository to generate an audit report for.  '
    'The full repository name must be provided, e.g., "<login>/<repo>".',
    group='repo',
)
@cli_tools.argument(
    '--user', '-U',
    dest='repos',
    action=RepoAction,
    help='Identify a user to generate an audit report for.  The user login '
    'name must be provided.  The report will include all visible repositories '
    'belonging to that user.  (This does *not* audit pull requests merged by '
    'this user.)',
    group='repo',
    target='user',
)
@cli_tools.argument(
    '--org', '-o',
    dest='repos',
    action=RepoAction,
    help='Identify an organization to generate an audit report for.  The '
    'organization name must be provided.  The report will include all '
    'visible repositories belonging to that organization.',
    group='repo',
    target='org',
)
@cli_tools.argument(
    '--audit', '-a',
    dest='audits',
    action='append',
    default=[],
    help='Select the specific audit rules to run.  May be given more than '
    'once to specify more audit rules.  Defaults to "%s".' %
    '", "'.join(sorted(audit.Auditor.defaults())),
)
@cli_tools.argument(
    '--since', '-s',
    action=TimeAction,
    help='Specify a horizon date for the audit.  Pull requests that were '
    'merged before this date will be omitted from the audit.  The horizon '
    'date may be specified as an actual date stamp (e.g., "2014-12-1"), or '
    'as a relative expression (e.g., "1 week ago").  Note that the value '
    'will need to be quoted if it contains any spaces.',
)
@cli_tools.argument(
    '--update',
    action='store_true',
    default=False,
    help='If given, repository information read from configuration files '
    'will be updated to reflect audited pull requests, enabling them to be '
    'skipped on subsequent runs.',
)
@cli_tools.argument(
    '--output', '-O',
    default='-',
    help='Specify the file name the report should be emitted to.  If not '
    'provided, or if specified as "-", the report will be emitted to '
    'standard output.',
)
@cli_tools.argument(
    '--verbose', '-v',
    action='store_const',
    default=1,
    const=2,
    help='Request verbose output.  This will cause status messages to be '
    'emitted while producing the report.',
)
@cli_tools.argument(
    '--quiet', '-q',
    dest='verbose',
    action='store_const',
    const=0,
    help='Request quiet output.  This will suppress all status messages, '
    'emitting only the final report.',
)
@cli_tools.argument(
    '--debug', '-d',
    action='store_true',
    help='Enable debugging mode.  If errors occur, a more detailed output '
    'will be emitted.  This does not affect verbosity.'
)
def perform_audit(ctxt, repos, since=None, stream=sys.stdout, update=False):
    """
    Generate an audit report of all merged pull requests on the
    specified repositories (see the "--config", "--repo", "--user",
    and "--org" options for how to specify repositories).

    :param ctxt: An object containing defaults for the API location,
                 authentication credentials, and list of audits to
                 perform, obtainable with a ``get()`` method similar
                 to that on ``dict``.  The object must also have a
                 ``warn()`` method, which will be used to report
                 warnings.
    :param repos: A list of tuples specifying repositories to obtain
                  the report on.  For each element of the list, the
                  first element of the tuple is one of "config",
                  "repo", "user", or "organization", and the second
                  element is the name of the config file (or
                  directory), the repository, the user, or the
                  organization, respectively.
    :param since: A ``datetime.datetime`` object indicating a horizon
                  date; only pull requests merged after the horizon
                  date will be reported.  Optional.
    :param stream: The output stream to receive the audit report.
                   Defaults to ``sys.stdout``.
    :param update: If ``True``, repository information read from
                   configuration files may be updated to reflect
                   audited pull requests, enabling them to be skipped
                   on subsequent runs.
    """

    start = datetime.datetime.utcnow()

    # Build the list of repositories
    repo_dict = {}
    for target, name in repos:
        try:
            tmp_repos = targets[target](ctxt, name)
        except exc.DuplicateRepositoryException as ex:
            # Emit information about duplications from configuration
            ctxt.warn(str(ex))
            for r_name, sublist in sorted(ex.dups.items(), key=lambda x: x[0]):
                ctxt.warn('Repository %s present from: %s' %
                          (r_name, ', '.join(r.path for r in sublist)))
            raise exc.AuditException('Cannot process duplicate repositories')

        # Now assemble the repos into the master list we'll use for
        # the audit
        for repo in tmp_repos:
            if repo.name in repo_dict:
                raise exc.AuditException(
                    'Repository %s specified by --%s=%s is a duplicate' %
                    (repo.name, target, name))

            repo_dict[repo.name] = repo

    # Build the list of repositories
    repo_list = [v for k, v in sorted(repo_dict.items(), key=lambda x: x[0])]

    # Perform the audit
    fail_count = 0
    pr_count = 0
    for repo in repo_list:
        failures = repo.audit(since, update)
        if not failures:
            continue

        # Report the audit failures
        print('%s:' % repo.repo.full_name, file=stream)
        for pull, fails in sorted(failures, key=lambda x: x[0].number):
            # Keep track of the number of pull requests and failures
            pr_count += 1
            fail_count += len(fails)

            print(u'  Pull request {pull.number}:\n'
                  u'    URL: {pull.html_url}\n'
                  u'    Proposed by {proposer} ({pull.user.login})\n'
                  u'    Proposed at {pull.created_at}{age}\n'
                  u'    Merged by {merger} ({pull.merged_by.login})\n'
                  u'    Merged at {pull.merged_at}{merged}\n'
                  u'    Count of policy failures: {count}'.format(
                      pull=pull,
                      proposer=(pull.user.name or '<unknown>'),
                      merger=(pull.merged_by.name or '<unknown>'),
                      age=format_age(start, pull.created_at, ' (age: %s)'),
                      merged=format_age(start, pull.merged_at, ' (%s ago)'),
                      count=len(fails),
                  ),
                  file=stream)

            # Output the actual failures
            for fail in sorted(fails, key=lambda x: x.audit):
                print(textwrap.fill(six.text_type(fail),
                                    initial_indent=u'      - ',
                                    subsequent_indent=u'        '),
                      file=stream)

            # Emit a trailing empty line to offset subsequent audits
            print(u'', file=stream)

    # Emit the final summary statistics
    end = datetime.datetime.utcnow()
    print(u'Audit report generated in %s at %s' % (end - start, start),
          file=stream)
    print(u'Found %d policy violations in %d merged pull requests' %
          (fail_count, pr_count), file=stream)

    # Update the config files
    if update:
        repository.Repository.save(repo_list)


@perform_audit.processor
def _process_perform_audit(args):
    """
    A ``cli_tools`` processor that adapts between the command line
    interface and the ``audit()`` function.  The processor builds a
    ``Context`` object, which will be used to carry various defaults.
    It also selects the correct output stream.  After ``audit()``
    returns, it ensures that the output stream is closed, if required.

    :param args: The ``argparse.Namespace`` object constructed by
                 ``cli_tools``.

    :returns: A ``cli_tools`` processor generator.
    """

    # Enable debugging output
    if args.debug:
        github.enable_console_debug_logging()

    # Construct the context
    args.ctxt = Context(args)

    # Select the correct output stream
    if args.output == '-':
        args.stream = sys.stdout
        close = False
    else:
        args.stream = io.open(args.output, 'w', encoding='utf-8')
        close = True

    # Generate the audit report as requested
    try:
        yield
    finally:
        # Make sure the stream gets closed
        if close:
            args.stream.close()
