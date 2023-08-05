# Copyright 2014, Ansible, Inc.
# Luke Sneeringer <lsneeringer@ansible.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click

from tower_cli import models, resources
from tower_cli.api import client
from tower_cli.utils import types


class Resource(models.Resource):
    cli_help = 'Manage organizations within Ansible Tower.'
    endpoint = '/organizations/'

    name = models.Field(unique=True)
    description = models.Field(required=False, display=False)

    @resources.command(use_fields_as_options=False)
    @click.option('--organization', type=types.Related('organization'))
    @click.option('--user', type=types.Related('user'))
    def associate(self, organization, user):
        """Associate a user with this organization."""
        return self._assoc('users', organization, user)

    @resources.command(use_fields_as_options=False)
    @click.option('--organization', type=types.Related('organization'))
    @click.option('--user', type=types.Related('user'))
    def disassociate(self, organization, user):
        """Disassociate a user from this organization."""
        return self._disassoc('users', organization, user)
