# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2013 Hewlett Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
HP LeftHand REST Client

:Author: Kurt Martin
:Author: Walter A. Boring IV
:Copyright: Copyright 2013, Hewlett Packard Development Company, L.P.
:License: Apache v2.0

"""

version_tuple = (1, 0, 3)


def get_version_string():
    if isinstance(version_tuple[-1], str):
        return '.'.join(map(str, version_tuple[:-1])) + version_tuple[-1]
    return '.'.join(map(str, version_tuple))

version = get_version_string()
"""Current version of HPLeftHandClient."""
