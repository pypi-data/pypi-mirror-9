# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import logging
from os.path import join as pjoin

import six

from st2client.models import datastore
from st2client.commands import resource
from st2client.commands.resource import add_auth_token_to_kwargs_from_cli
from st2client.formatters import table
from st2client.models.datastore import KeyValuePair
from st2client.utils.date import format_isodate


LOG = logging.getLogger(__name__)


class KeyValuePairBranch(resource.ResourceBranch):

    def __init__(self, description, app, subparsers, parent_parser=None):
        super(KeyValuePairBranch, self).__init__(
            datastore.KeyValuePair, description, app, subparsers,
            parent_parser=parent_parser,
            commands={
                'list': KeyValuePairListCommand,
                'get': KeyValuePairGetCommand,
                'delete': KeyValuePairDeleteCommand
            })

        # Registers extended commands
        self.commands['set'] = KeyValuePairSetCommand(self.resource, self.app,
                                                      self.subparsers)
        self.commands['load'] = KeyValuePairLoadCommand(
            self.resource, self.app, self.subparsers)
        self.commands['delete_by_prefix'] = KeyValuePairDeleteByPrefixCommand(
            self.resource, self.app, self.subparsers)

        # Remove unsupported commands
        # TODO: Refactor parent class and make it nicer
        del self.commands['create']
        del self.commands['update']


class KeyValuePairListCommand(resource.ResourceListCommand):
    display_attributes = ['name', 'value', 'expire_timestamp']
    attribute_transform_functions = {
        'expire_timestamp': format_isodate,
    }

    def run_and_print(self, args, **kwargs):
        instances = self.run(args, **kwargs)
        self.print_output(reversed(instances), table.MultiColumnTable,
                          attributes=args.attr, widths=args.width,
                          json=args.json,
                          attribute_transform_functions=self.attribute_transform_functions)


class KeyValuePairGetCommand(resource.ResourceGetCommand):
    pk_argument_name = 'name'
    display_attributes = ['name', 'value']


class KeyValuePairSetCommand(resource.ResourceCommand):
    display_attributes = ['name', 'value']

    def __init__(self, resource, *args, **kwargs):
        super(KeyValuePairSetCommand, self).__init__(resource, 'set',
            'Set an existing %s.' % resource.get_display_name().lower(),
            *args, **kwargs)

        self.parser.add_argument('name',
                                 metavar='name',
                                 help='Name of the key value pair.')
        self.parser.add_argument('value', help='Value paired with the key.')

    @add_auth_token_to_kwargs_from_cli
    def run(self, args, **kwargs):
        instance = KeyValuePair()
        instance.id = args.name  # TODO: refactor and get rid of id
        instance.name = args.name
        instance.value = args.value
        return self.manager.update(instance, **kwargs)

    def run_and_print(self, args, **kwargs):
        instance = self.run(args, **kwargs)
        self.print_output(instance, table.PropertyValueTable,
                          attributes=self.display_attributes, json=args.json)


class KeyValuePairDeleteCommand(resource.ResourceDeleteCommand):
    pk_argument_name = 'name'

    @add_auth_token_to_kwargs_from_cli
    def run(self, args, **kwargs):
        resource_id = getattr(args, self.pk_argument_name, None)
        instance = self.get_resource(resource_id, **kwargs)
        instance.id = resource_id  # TODO: refactor and get rid of id
        self.manager.delete(instance, **kwargs)


class KeyValuePairDeleteByPrefixCommand(resource.ResourceCommand):
    """
    Commands which delete all the key value pairs which match the provided
    prefix.
    """
    def __init__(self, resource, *args, **kwargs):
        super(KeyValuePairDeleteByPrefixCommand, self).__init__(resource, 'delete_by_prefix',
            'Delete KeyValue pairs which match the provided prefix', *args, **kwargs)

        self.parser.add_argument('-p', '--prefix', required=True,
                                 help='Name prefix (e.g. twitter.TwitterSensor:)')

    @add_auth_token_to_kwargs_from_cli
    def run(self, args, **kwargs):
        prefix = args.prefix
        key_pairs = self.manager.get_all()

        to_delete = []
        for key_pair in key_pairs:
            if key_pair.name.startswith(prefix):
                key_pair.id = key_pair.name
                to_delete.append(key_pair)

        deleted = []
        for key_pair in to_delete:
            self.manager.delete(instance=key_pair, **kwargs)
            deleted.append(key_pair)

        return deleted

    def run_and_print(self, args, **kwargs):
        # TODO: Need to use args, instead of kwargs (args=) because of bad API
        # FIX ME
        deleted = self.run(args, **kwargs)
        key_ids = [key_pair.id for key_pair in deleted]

        print('Deleted %s keys' % (len(deleted)))
        print('Deleted key ids: %s' % (', '.join(key_ids)))


class KeyValuePairLoadCommand(resource.ResourceCommand):
    pk_argument_name = 'name'
    display_attributes = ['name', 'value']

    def __init__(self, resource, *args, **kwargs):
        help_text = ('Load a list of %s from file.' %
                     resource.get_plural_display_name().lower())
        super(KeyValuePairLoadCommand, self).__init__(resource, 'load',
            help_text, *args, **kwargs)

        self.parser.add_argument(
            'file', help=('JSON file containing the %s to create.'
                          % resource.get_plural_display_name().lower()))

    @add_auth_token_to_kwargs_from_cli
    def run(self, args, **kwargs):
        file_path = os.path.normpath(pjoin(os.getcwd(), args.file))

        if not os.path.exists(args.file):
            raise ValueError('File "%s" doesn\'t exist' % (file_path))

        if not os.path.isfile(args.file):
            raise ValueError('"%s" is not a file' % (file_path))

        with open(file_path, 'r') as f:
            kvps = json.loads(f.read())

        instances = []
        for name, value in six.iteritems(kvps):
            instance = KeyValuePair()
            instance.id = name  # TODO: refactor and get rid of id
            instance.name = name
            instance.value = value

            self.manager.update(instance, **kwargs)
            instances.append(instance)
        return instances

    def run_and_print(self, args, **kwargs):
        instances = self.run(args, **kwargs)
        self.print_output(instances, table.MultiColumnTable,
                          attributes=['id', 'name', 'value'], json=args.json)
