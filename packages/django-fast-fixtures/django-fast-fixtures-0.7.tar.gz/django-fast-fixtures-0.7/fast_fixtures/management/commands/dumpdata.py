
from optparse import make_option

from django.db import connections
from django.apps import apps

from django.core.management.commands.dumpdata import Command as DumpCommand
from fast_fixtures.serializers import json_serializer
from fast_fixtures.migrator import get_app_state


class Command(DumpCommand):
    option_list = DumpCommand.option_list + (
        make_option('-m', '--migrated', action='store_true', dest='migrated',
            help='If specified will dump data to a filename which will be migrated into place when loaded.'),
    )

    def handle(self, *app_labels, **options):
        if not options.pop('migrated', False):
            return super(Command, self).handle(*app_labels, **options)

        # This is all very ugly, but required because of the bad way django
        # serialization was written. This left very few openings for adjusting
        # the output with extra meta information.
        apps_state = get_app_state(app_labels, options.get('database'))
        options['format'] = json_serializer({'migrations': apps_state})

        super(Command, self).handle(*app_labels, **options)

