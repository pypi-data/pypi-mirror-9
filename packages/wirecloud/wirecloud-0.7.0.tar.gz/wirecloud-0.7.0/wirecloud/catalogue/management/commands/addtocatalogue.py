# -*- coding: utf-8 -*-

# Copyright (c) 2012-2015 CoNWeT Lab., Universidad Politécnica de Madrid

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

from __future__ import unicode_literals

import locale
from optparse import make_option

from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import override, ugettext as _

from wirecloud.catalogue.views import add_packaged_resource
from wirecloud.commons.utils.template import TemplateParser
from wirecloud.commons.utils.wgt import WgtFile
from wirecloud.platform.localcatalogue.utils import install_resource_to_user, install_resource_to_group, install_resource_to_all_users


class Command(BaseCommand):
    args = '<file.wgt>...'
    help = 'Adds one or more packaged mashable application components into the catalogue'
    option_list = BaseCommand.option_list + (
        make_option('--redeploy',
            action='store_true',
            dest='redeploy',
            help='Replace mashable application components files with the new ones.',
            default=False),
        make_option('-u', '--users',
            action='store',
            type='string',
            dest='users',
            help='Comma separated list of users that will obtain access to the uploaded mashable application components',
            default=''),
        make_option('-g', '--groups',
            action='store',
            type='string',
            dest='groups',
            help='Comma separated list of groups that will obtain access rights to the uploaded mashable application components',
            default=''),
        make_option('-p', '--public',
            action='store_true',
            dest='public',
            help='Allow any user to access the mashable application components.',
            default=False),
    )

    def _handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError(_('Wrong number of arguments'))

        self.verbosity = int(options.get('verbosity', 1))

        users = []
        groups = []
        redeploy = options['redeploy']
        public = options['public']
        users_string = options['users'].strip()
        groups_string = options['groups'].strip()

        if redeploy is False and public is False and users_string == '' and groups_string == '':
            raise CommandError(_('You must use at least one of the following flags: --redeploy, --users, --groups or --public '))

        if not options['redeploy']:

            if users_string != '':
                for username in users_string.split(','):
                    users.append(User.objects.get(username=username))

            if groups_string != '':
                for groupname in groups_string.split(','):
                    groups.append(Group.objects.get(name=groupname))

        for file_name in args:
            try:
                f = open(file_name, 'rb')
                wgt_file = WgtFile(f)
            except:
                self.log(_('Failed to read from %(file_name)s') % {'file_name': file_name}, level=1)
                continue

            try:
                template_contents = wgt_file.get_template()
                template = TemplateParser(template_contents)
                if options['redeploy']:
                    add_packaged_resource(f, None, wgt_file=wgt_file, template=template, deploy_only=True)
                else:
                    for user in users:
                        install_resource_to_user(user, file_contents=wgt_file)

                    for group in groups:
                        install_resource_to_group(group, file_contents=wgt_file)

                    if public:
                        install_resource_to_all_users(file_contents=wgt_file)

                wgt_file.close()
                f.close()
                self.log(_('Successfully imported \"%(name)s\" from \"%(file_name)s\"') % {'name': template.get_resource_processed_info()['title'], 'file_name': file_name}, level=1)
            except:
                self.log(_('Failed to import the mashable application component from %(file_name)s') % {'file_name': file_name}, level=1)

    def handle(self, *args, **options):
        with override(locale.getdefaultlocale()[0][:2]):
            return self._handle(*args, **options)

    def log(self, msg, level=2):
        """
        Small log helper
        """
        if self.verbosity >= level:
            self.stdout.write(msg)
