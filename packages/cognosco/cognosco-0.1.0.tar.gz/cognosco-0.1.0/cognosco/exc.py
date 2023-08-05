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


class AuditException(Exception):
    """
    An exception raised by ``perform_audit()`` to report duplicate
    repository specifications.
    """

    pass


class DuplicateRepositoryException(Exception):
    """
    An exception raised if the same repository is defined by multiple
    repository .yaml files.
    """

    def __init__(self, msg='', dups=None):
        """
        Initialize a ``DuplicateRepositoryException`` instance.

        :param msg: The exception message.  Defaults to the empty
                    string.
        :param dups: A dictionary mapping repository names to a list
                     of ``cognosco.repository.Repository`` objects.
        """

        super(DuplicateRepositoryException, self).__init__(msg)
        self.dups = dups
