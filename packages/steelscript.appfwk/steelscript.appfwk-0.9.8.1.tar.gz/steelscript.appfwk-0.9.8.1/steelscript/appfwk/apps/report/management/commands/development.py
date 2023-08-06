# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import logging
import optparse
from cStringIO import StringIO
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand

from steelscript.common.datautils import Formatter
from steelscript.appfwk.project.utils import Importer

from steelscript.appfwk.apps.datasource.models import Table, Job, DatasourceTable
from steelscript.appfwk.apps.datasource.forms import TableFieldForm
from steelscript.appfwk.apps.report.models import Report, Widget

from steelscript.appfwk.apps.plugins import plugins


class Command(BaseCommand):
    args = None
    help = 'Run a defined table and return results in nice tabular format'

    def create_parser(self, prog_name, subcommand):
        """ Override super version to include special option grouping
        """
        parser = super(Command, self).create_parser(prog_name, subcommand)
        group = optparse.OptionGroup(parser, "Development Helpers",
                                     "Helper commands for development of SteelScript reports")
        group.add_option('--table-classes',
                         action='store_true',
                         default=False,
                         help='List available DatasourceTable classes')
        group.add_option('--widget-classes',
                         action='store_true',
                         default=False,
                         help='List currently used Widget classes')
        parser.add_option_group(group)

        return parser

    def console(self, msg, ending=None):
        """ Print text to console except if we are writing CSV file """
        if not self.options['as_csv']:
            self.stdout.write(msg, ending=ending)
            self.stdout.flush()

    def get_subclasses(self, c):
        subclasses = c.__subclasses__()
        for d in list(subclasses):
            subclasses.extend(self.get_subclasses(d))
        subclasses.sort(key=lambda x: x.__module__)
        return subclasses

    def get_tables(self):
        buf = StringIO()
        i = Importer(buf=buf)
        from steelscript.appfwk.apps.datasource.modules import analysis, html
        for p in plugins.all():
            for d in p.get_datasources():
                i.import_file(*d)
        return self.get_subclasses(DatasourceTable)

    def handle(self, *args, **options):
        """ Main command handler
        """
        self.options = options

        if options['table_classes']:
            sc = self.get_tables()
            Formatter.print_table([(c.__name__, c.__module__) for c in sc],
                                  ['Name', 'Package'])

        elif options['widget_classes']:
            # can't use same trick as tables since these aren't subclasses
            W = Widget.objects.all()
            s = set([(w.uiwidget, w.module) for w in W])
            Formatter.print_table(sorted(s, key=lambda x: x[1]),
                                  ['Name', 'Package'])
