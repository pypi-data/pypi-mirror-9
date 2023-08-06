# -*- coding: utf-8 -*-

from datetime import date
from django.core.management.base import BaseCommand
from optparse import make_option


class Command(BaseCommand):
    help = u"Load a database dump."

    option_list = BaseCommand.option_list + (
        make_option('--source',
                    action='store',
                    type="string",
                    dest='source',
                    help=u"Path to the database dump file to load."),
        make_option('--destination',
                    action='store',
                    type="string",
                    dest='destination',
                    default='local',
                    help=u"Where to load the dump."),
        make_option('--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False,
                    help=u'Just pretend...'),
    )

    def handle(self, *args, **options):
        command.stdout.write("Loading %s on %s" % (options.get("source"), options.get("destination")))
