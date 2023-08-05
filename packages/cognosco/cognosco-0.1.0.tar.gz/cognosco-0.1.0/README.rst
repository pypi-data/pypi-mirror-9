=============================
Cognosco Pull Request Auditor
=============================

Cognosco is a command line tool for auditing the merged pull requests
on Github or Github Enterprise, using the Github API.  It generates a
report of all policy violations for all the repositories it was
requested to examine.  Each pull request is listed with a link to the
pull request, as well as an indication of which policy rules were
violated.

Usage
=====

Cognosco uses ``cli_tools``, and so provides extensive help text,
accessible by using the "--help" argument.  The primary arguments it
needs have to do with authenticating to Github (see the help for
"--username", "--password", and "--github-url"; note that cognosco
will prompt for a password if none is provided).

Cognosco also must be told which repositories to examine; this is done
by passing one or more of the "--repo", "--user", or "--org" options.
(Note that cognosco will generate an empty report if none of these
options are passed.)  Any mix of these options may be used; cognosco
will explore all listed repositories, and all repositories it can see
under the listed users or organizations.
