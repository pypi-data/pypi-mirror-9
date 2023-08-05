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

import getpass

import github
from six.moves.urllib import parse as urlparse


# A cache of Github handles for various combinations of username,
# password, and API URL; the key is a tuple of username and normalized
# URL.
_handles = {}


def get_handle(username=None, password=None, url='https://api.github.com'):
    """
    Retrieve a ``github.Github`` object.  This uses a cache, and so
    prevents creating multiple objects to access the same Github
    instance with the same credentials.

    :param username: The username to use to access the Github API.
                     Defaults to the user's system username.
    :param password: The password to use to access the Github API.  If
                     not provided, it will be prompted for.
    :param url: The URL to use to access the Github API.  Defaults to
                "https://api.github.com".  Note that if a username
                and/or a password are present in the URL, that will
                override the values from ``username`` and
                ``password``.

    :returns: An instance of ``github.Github``.
    """

    # Begin by parsing the URL
    parsed = urlparse.urlparse(url)

    # Overwrite username and password
    if parsed.username:
        username = parsed.username
    if parsed.password:
        password = parsed.password

    # Reconstitute the net location
    netloc = parsed.hostname or ''
    if parsed.port:
        netloc += ':%d' % parsed.port

    # Normalize the path
    path = '/' + '/'.join(elem for elem in
                          (parsed.path or '').split('/') if elem)

    # Rebuild the normalized URL
    url = urlparse.urlunparse((parsed.scheme, netloc, path, '', '', ''))

    # Select appropriate defaults for username and password
    if not username:
        username = getpass.getuser()
    if not password:
        password = getpass.getpass(
            u'Password for %s at %s> ' % (username, url))

    # Now build the cache key
    key = (username, url)

    # Do we need to build a new handle?
    if key not in _handles:
        _handles[key] = github.Github(username, password, url)

    return _handles[key]
