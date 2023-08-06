# Copyright (c) 2014 OpenStack Foundation.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

__all__ = [
    'list_auth_token_opts',
]

import copy

import keystonemiddleware.auth_token
from keystonemiddleware.auth_token import _auth
from keystonemiddleware.auth_token import _base

auth_token_opts = [
    (_base.AUTHTOKEN_GROUP,
     keystonemiddleware.auth_token._OPTS +
     _auth.AuthTokenPlugin.get_options())
]


def list_auth_token_opts():
    """Return a list of oslo_config options available in auth_token middleware.

    The returned list includes all oslo_config options which may be registered
    at runtime by the project.

    Each element of the list is a tuple. The first element is the name of the
    group under which the list of elements in the second element will be
    registered. A group name of None corresponds to the [DEFAULT] group in
    config files.

    This function is also discoverable via the entry point
    'keystonemiddleware.auth_token' under the 'oslo.config.opts'
    namespace.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users by this middleware.

    :returns: a list of (group_name, opts) tuples
    """
    return [(g, copy.deepcopy(o)) for g, o in auth_token_opts]
