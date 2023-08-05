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

from __future__ import absolute_import

import functools
import types

import click
from click.decorators import _param_memo as add_param

from tower_cli.conf import settings


def command(method=None, **kwargs):
    """Cause the given function to become a click command, and add all
    global options.
    """
    # Define the actual decorator.
    # This is done in such a way as to allow @command, @command(), and
    # @command(foo='bar') to all work.
    def actual_decorator(method):
        # Create a wrapper function that will "eat" the authentication
        # if it's provided as keyword arguments and apply it to settings.
        @with_global_options
        @click.command(**kwargs)
        @functools.wraps(method)
        def answer(*inner_a, **inner_kw):
            runtime_settings = {
                'host': inner_kw.pop('tower_host', None),
                'password': inner_kw.pop('tower_password', None),
                'format': inner_kw.pop('format', None),
                'username': inner_kw.pop('tower_username', None),
                'verbose': inner_kw.pop('verbose', None),
            }
            with settings.runtime_values(**runtime_settings):
                return method(*inner_a, **inner_kw)

        # Done, return the wrapped-wrapped-wrapped-wrapped method.
        # BECAUSE WE WRAP ALL THE THINGS!
        return answer

    # If we got the method straight-up, apply the decorator and return
    # the decorated method; otherwise, return the actual decorator for
    # the Python interpreter to apply.
    if method and isinstance(method, types.FunctionType):
        return actual_decorator(method)
    else:
        return actual_decorator


def with_global_options(method):
    """Apply the global options that we desire on every method within
    tower-cli to the given click command.
    """
    # Create global options for the Tower host, username, and password.
    #
    # These are runtime options that will override the configuration file
    # settings.
    method = click.option('-h', '--tower-host',
        help='The location of the Ansible Tower host. '
             'HTTPS is assumed as the protocol unless "http://" is explicitly '
             'provided. This will take precedence over a host provided to '
             '`tower config`, if any.', 
        required=False,
    )(method)
    method = click.option('-u', '--tower-username',
        help='Username to use to authenticate to Ansible Tower. '
             'This will take precedence over a username provided to '
             '`tower config`, if any.',
        required=False,
    )(method)
    method = click.option('-p', '--tower-password',
        help='Password to use to authenticate to Ansible Tower. '
             'This will take precedence over a password provided to '
             '`tower config`, if any.',
        required=False,
    )(method)

    # Create a global verbose/debug option.
    method = click.option('-f', '--format',
        help='Output format. The "human" format is intended for humans '
             'reading output on the CLI; the "json" format is intended for '
             'scripts that wish to parse output. Note that the "json" format '
             'provides more data.',
        type=click.Choice(['human', 'json']),
        required=False,
    )(method)
    method = click.option('-v', '--verbose',
        default=None,
        help='Show information about requests being made.',
        is_flag=True,
        required=False,
    )(method)

    # Okay, we're done adding options; return the method.
    return method
