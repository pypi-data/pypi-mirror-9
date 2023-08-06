# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import sys

from django.core.management.base import BaseCommand
from django.core import management
from django import db


class Command(BaseCommand):
    args = None
    help = ('Initializes new database project.')

    def handle(self, *args, **options):

        tables = db.connection.introspection.table_names()
        if 'auth_permission' in tables:
            self.stdout.write('Database already exists, aborting initialization.')
            sys.exit(1)

        db.close_connection()
        management.call_command('reset_appfwk',
                                force=True,
                                drop_users=True,
                                drop_tokens=True)
