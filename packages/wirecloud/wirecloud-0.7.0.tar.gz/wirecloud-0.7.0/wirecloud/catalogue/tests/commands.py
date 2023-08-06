# -*- coding: utf-8 -*-

# Copyright (c) 2015 CoNWeT Lab., Universidad Politécnica de Madrid

# This file is part of Wirecloud.

# Wirecloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Wirecloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with Wirecloud.  If not, see <http://www.gnu.org/licenses/>.

import io
import os
import shutil
from tempfile import mkdtemp

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from mock import Mock, patch, DEFAULT
from whoosh import fields, index

from wirecloud.commons.searchers import get_available_search_engines


@patch('wirecloud.catalogue.management.commands.addtocatalogue.locale.getdefaultlocale', return_value=("en_US",))
class AddToCatalogueCommandTestCase(TestCase):

    tags = ('wirecloud-commands', 'wirecloud-command-addtocatalogue')

    def setUp(self):

        self.options = {"stdout": io.BytesIO(), "stderr": io.BytesIO()}

    def test_addtocatalogue_command_no_args(self, getdefaultlocale_mock):

        args = []

        with self.assertRaises((CommandError, SystemExit)):
            call_command('addtocatalogue', *args, **self.options)

        self.options['stdout'].seek(0)
        self.assertEqual(self.options['stdout'].read(), '')
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')

    def test_addtocatalogue_command_simplewgt_user(self, getdefaultlocale_mock):

        args = ['file.wgt']
        self.options['users'] = 'admin'

        try:
            with patch('__builtin__.open'):
                with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue',
                        add_packaged_resource=DEFAULT, install_resource_to_user=DEFAULT, install_resource_to_group=DEFAULT, install_resource_to_all_users=DEFAULT,
                        WgtFile=DEFAULT, TemplateParser=DEFAULT, User=DEFAULT, Group=DEFAULT, autospec=True) as context:
                    parser = Mock()
                    parser.get_resource_processed_info.return_value = {'title': "Mashable Application Component1"}
                    context['TemplateParser'].return_value = parser

                    # Make the call to addtocatalogue
                    call_command('addtocatalogue', *args, **self.options)

                    # Basic assert code
                    self.assertEqual(context['add_packaged_resource'].call_count, 0)
                    self.assertEqual(context['install_resource_to_user'].call_count, 1)
                    self.assertEqual(context['install_resource_to_group'].call_count, 0)
                    self.assertEqual(context['install_resource_to_all_users'].call_count, 0)

        except SystemExit:
            raise CommandError('')

        self.options['stdout'].seek(0)
        self.assertTrue("Mashable Application Component1" in self.options['stdout'].read())
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')

    def test_addtocatalogue_command_simplewgt_group(self, getdefaultlocale_mock):

        args = ['file.wgt']
        self.options['groups'] = 'group1'

        try:
            with patch('__builtin__.open'):
                with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue',
                        add_packaged_resource=DEFAULT, install_resource_to_user=DEFAULT, install_resource_to_group=DEFAULT, install_resource_to_all_users=DEFAULT,
                        WgtFile=DEFAULT, TemplateParser=DEFAULT, User=DEFAULT, Group=DEFAULT, autospec=True) as context:
                    parser = Mock()
                    parser.get_resource_processed_info.return_value = {'title': "Mashable Application Component1"}
                    context['TemplateParser'].return_value = parser

                    # Make the call to addtocatalogue
                    call_command('addtocatalogue', *args, **self.options)

                    # Basic assert code
                    self.assertEqual(context['add_packaged_resource'].call_count, 0)
                    self.assertEqual(context['install_resource_to_user'].call_count, 0)
                    self.assertEqual(context['install_resource_to_group'].call_count, 1)
                    self.assertEqual(context['install_resource_to_all_users'].call_count, 0)

        except SystemExit:
            raise CommandError('')

        self.options['stdout'].seek(0)
        self.assertTrue("Mashable Application Component1" in self.options['stdout'].read())
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')

    def test_addtocatalogue_command_simplewgt_public(self, getdefaultlocale_mock):

        args = ['file.wgt']
        self.options['public'] = True

        try:
            with patch('__builtin__.open'):
                with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue',
                        add_packaged_resource=DEFAULT, install_resource_to_user=DEFAULT, install_resource_to_group=DEFAULT, install_resource_to_all_users=DEFAULT,
                        WgtFile=DEFAULT, TemplateParser=DEFAULT, User=DEFAULT, Group=DEFAULT, autospec=True) as context:
                    parser = Mock()
                    parser.get_resource_processed_info.return_value = {'title': "Mashable Application Component1"}
                    context['TemplateParser'].return_value = parser

                    # Make the call to addtocatalogue
                    call_command('addtocatalogue', *args, **self.options)

                    # Basic assert code
                    self.assertEqual(context['add_packaged_resource'].call_count, 0)
                    self.assertEqual(context['install_resource_to_user'].call_count, 0)
                    self.assertEqual(context['install_resource_to_group'].call_count, 0)
                    self.assertEqual(context['install_resource_to_all_users'].call_count, 1)

        except SystemExit:
            raise CommandError('')

        self.options['stdout'].seek(0)
        self.assertTrue("Mashable Application Component1" in self.options['stdout'].read())
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')

    def test_addtocatalogue_command_simplewgt_no_action(self, getdefaultlocale_mock):

        args = ['file.wgt']

        with patch('__builtin__.open'):
            with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue',
                    add_packaged_resource=DEFAULT, install_resource_to_user=DEFAULT, install_resource_to_group=DEFAULT, install_resource_to_all_users=DEFAULT,
                    WgtFile=DEFAULT, TemplateParser=DEFAULT, User=DEFAULT, Group=DEFAULT, autospec=True) as context:

                # Make the call to addtocatalogue
                self.assertRaises((CommandError, SystemExit), call_command, 'addtocatalogue', *args, **self.options)

                # Basic assert code
                self.assertEqual(context['add_packaged_resource'].call_count, 0)
                self.assertEqual(context['install_resource_to_user'].call_count, 0)
                self.assertEqual(context['install_resource_to_group'].call_count, 0)
                self.assertEqual(context['install_resource_to_all_users'].call_count, 0)

        self.options['stdout'].seek(0)
        self.assertEqual(self.options['stdout'].read(), '')
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')

    def test_addtocatalogue_command_deploy_only(self, getdefaultlocale_mock):

        self.options['redeploy'] = True

        args = ['file1.wgt', 'file2.wgt']
        try:
            with patch('__builtin__.open'):
                with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue', add_packaged_resource=DEFAULT, WgtFile=DEFAULT, TemplateParser=DEFAULT, autospec=True) as context:
                    call_command('addtocatalogue', *args, **self.options)
                    self.assertEqual(context['add_packaged_resource'].call_count, 2)
                    self.assertEqual(context['add_packaged_resource'].call_args_list[0][1]['deploy_only'], True)
                    self.assertEqual(context['add_packaged_resource'].call_args_list[1][1]['deploy_only'], True)
        except SystemExit:
            raise CommandError('')

    def test_addtocatalogue_command_error_reading_file(self, getdefaultlocale_mock):

        self.options['redeploy'] = True

        args = ['file1.wgt', 'file2.wgt']
        try:
            with patch('__builtin__.open') as open_mock:
                def open_mock_side_effect(file_name, mode):
                    if file_name == 'file1.wgt':
                        raise Exception
                open_mock.side_effect = open_mock_side_effect
                with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue', add_packaged_resource=DEFAULT, WgtFile=DEFAULT, TemplateParser=DEFAULT, autospec=True) as context:
                    call_command('addtocatalogue', *args, **self.options)
                    self.assertEqual(context['add_packaged_resource'].call_count, 1)
                    self.assertEqual(context['add_packaged_resource'].call_args_list[0][1]['deploy_only'], True)
        except SystemExit:
            raise CommandError('')

        self.options['stdout'].seek(0)
        self.assertNotEqual(self.options['stdout'].read(), '')
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')

    def test_addtocatalogue_command_error_installing_mac(self, getdefaultlocale_mock):

        self.options['redeploy'] = True

        args = ['file1.wgt', 'file2.wgt']
        try:
            with patch('__builtin__.open'):
                with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue', add_packaged_resource=DEFAULT, WgtFile=DEFAULT, TemplateParser=DEFAULT, autospec=True) as context:

                    context['TemplateParser'].side_effect = (Exception, None)

                    call_command('addtocatalogue', *args, **self.options)
                    self.assertEqual(context['add_packaged_resource'].call_count, 1)
                    self.assertEqual(context['add_packaged_resource'].call_args_list[0][1]['deploy_only'], True)
        except SystemExit:
            raise CommandError('')

        self.options['stdout'].seek(0)
        self.assertNotEqual(self.options['stdout'].read(), '')
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')

    def test_addtocatalogue_command_error_installing_mac_quiet(self, getdefaultlocale_mock):

        self.options['verbosity'] = '0'
        self.options['redeploy'] = True

        args = ['file1.wgt', 'file2.wgt']
        try:
            with patch('__builtin__.open'):
                with patch.multiple('wirecloud.catalogue.management.commands.addtocatalogue', add_packaged_resource=DEFAULT, WgtFile=DEFAULT, TemplateParser=DEFAULT, autospec=True) as context:

                    context['TemplateParser'].side_effect = (Exception, None)

                    call_command('addtocatalogue', *args, **self.options)
                    self.assertEqual(context['add_packaged_resource'].call_count, 1)
                    self.assertEqual(context['add_packaged_resource'].call_args_list[0][1]['deploy_only'], True)
        except SystemExit:
            raise CommandError('')

        self.options['stdout'].seek(0)
        self.assertEqual(self.options['stdout'].read(), '')
        self.options['stderr'].seek(0)
        self.assertEqual(self.options['stderr'].read(), '')
