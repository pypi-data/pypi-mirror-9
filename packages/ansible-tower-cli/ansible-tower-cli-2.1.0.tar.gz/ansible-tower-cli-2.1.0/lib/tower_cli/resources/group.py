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

from tower_cli import get_resource, models, resources
from tower_cli.api import client
from tower_cli.utils import exceptions as exc, types

INVENTORY_SOURCES = ['manual', 'ec2', 'rax', 'gce', 'azure']


class Resource(models.Resource):
    cli_help = 'Manage groups belonging to an inventory.'
    endpoint = '/groups/'
    identity = ('inventory', 'name')

    name = models.Field(unique=True)
    description = models.Field(required=False, display=False)
    inventory = models.Field(type=types.Related('inventory'))
    variables = models.Field(type=types.File('r'), required=False,
                             display=False)

    @click.option('--credential', type=types.Related('credential'),
                                  required=False,
                                  help='The cloud credential to use.')
    @click.option('--source', type=click.Choice(INVENTORY_SOURCES),
                              default='manual',
                              help='The source to use for this group.')
    def create(self, credential=None, source=None, **kwargs):
        """Create a group and, if necessary, modify the inventory source within
        the group.
        """
        # First, create the group.
        answer = super(Resource, self).create(**kwargs)

        # If the group already exists and we aren't supposed to make changes,
        # then we're done.
        if not kwargs.pop('force_on_exists', False) and not answer['changed']:
            return answer

        # Sanity check: A group was created, but do we need to do anything
        # with the inventory source at all? If no credential or source
        # was specified, then we'd just be updating the inventory source
        # with an effective no-op.
        if not credential and source in ('manual', None):
            return answer

        # Get the inventory source ID ("isid").
        # Inventory sources are not created directly; rather, one was created
        # automatically when the group was created.
        isid = self._get_inventory_source_id(answer)

        # We now have our inventory source ID; modify it according to the
        # provided parameters.
        isrc = get_resource('inventory_source')
        return isrc.modify(isid, credential=credential, source=source,
                                 force_on_exists=True, **kwargs)

    @click.option('--credential', type=types.Related('credential'),
                                  required=False)
    @click.option('--source', type=click.Choice(INVENTORY_SOURCES),
                              default='manual',
                              help='The source to use for this group.')
    def modify(self, pk=None, credential=None, source=None, **kwargs):
        """Modify a group and, if necessary, the inventory source within
        the group.
        """
        # First, modify the group.
        answer = super(Resource, self).modify(pk=pk, **kwargs)

        # If the group already exists and we aren't supposed to make changes,
        # then we're done.
        if not kwargs.pop('force_on_exists', True) and not answer['changed']:
            return answer

        # Get the inventory source ID ("isid").
        # Inventory sources are not created directly; rather, one was created
        # automatically when the group was created.
        isid = self._get_inventory_source_id(answer)

        # We now have our inventory source ID; modify it according to the
        # provided parameters.
        #
        # Note: Any fields that were part of the group modification need
        # to be expunged from kwargs before making this call.
        isrc = get_resource('inventory_source')
        for field in self.fields:
            kwargs.pop(field.name, None)
        return isrc.modify(isid, credential=credential, source=source,
                                 force_on_exists=True, **kwargs)

    @resources.command(ignore_defaults=True, no_args_is_help=False)
    @click.option('--root', is_flag=True, default=False,
                  help='Show only root groups (groups with no parent groups) '
                       'within the given inventory.')
    def list(self, root=False, **kwargs):
        """Return a list of groups."""

        # Sanity check: If we got `--root` and no inventory, that's an
        # error.
        if root and not kwargs.get('inventory', None):
            raise exc.UsageError('The --root option requires specifying an '
                                 'inventory also.')

        # If we are tasked with getting root groups, do that.
        if root:
            inventory_id = kwargs['inventory']
            r = client.get('/inventories/%d/root_groups/' % inventory_id)
            return r.json()

        # Return the superclass implementation.
        return super(Resource, self).list(**kwargs)

    @click.argument('group', type=types.Related('group'))
    @click.option('--monitor', is_flag=True, default=False,
                  help='If sent, immediately calls `monitor` on the newly '
                       'launched job rather than exiting with a success.')
    @click.option('--timeout', required=False, type=int,
                  help='If provided with --monitor, this command (not the job)'
                       ' will time out after the given number of seconds. '
                       'Does nothing if --monitor is not sent.')
    @resources.command(use_fields_as_options=False, no_args_is_help=True)
    def sync(self, group, monitor=False, timeout=None, **kwargs):
        """Update the given group's inventory source."""

        isrc = get_resource('inventory_source')
        isid = self._get_inventory_source_id(group)
        return isrc.update(isid, monitor=monitor, timeout=timeout, **kwargs)

    def _get_inventory_source_id(self, group):
        """Return the inventory source ID given a group dictionary returned
        from the Tower API.
        """
        # If we got a group ID rather than a group, get the group.
        if isinstance(group, int):
            group = self.get(group)

        # Return the inventory soruce ID.
        return int(group['related']['inventory_source'].split('/')[-2])
